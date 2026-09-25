import asyncio
import os
import random
import threading
import time
from typing import List, Dict, Any, Callable, Optional, Set
from sheets_service import (
    clean_phone,
    get_now_wita_str,
    get_existing_numbers,
    update_live_progress,
    send_lead_to_master,
    check_remote_task,
)
from config import DEFAULT_SHEETS_WEBAPP_URL, AREAS_KALSEL


class ScraperController:
    """Thread-safe controller and state manager for automated canvassing."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(ScraperController, cls).__new__(cls)
                cls._instance._init_state()
            return cls._instance

    def _init_state(self):
        self.is_running = False
        self.stop_requested = False
        self.current_status = "IDLE"  # IDLE, RUNNING, SELESAI, STOPPED, ERROR
        self.current_message = "Sistem siap. Tekan Mulai Cari Data."
        self.current_keyword = ""
        self.current_target = 0
        self.current_count = 0
        self.current_area = ""
        self.db_path = "leads_history.json"
        self.collected_leads: List[Dict[str, Any]] = self._load_saved_leads()
        self.logs: List[Dict[str, str]] = []
        self.existing_numbers_count = 0
        self.webapp_url = DEFAULT_SHEETS_WEBAPP_URL
        self.worker_thread: Optional[threading.Thread] = None
        self.listener_thread: Optional[threading.Thread] = None
        self.listener_active = False

        # Prefetch initial existing numbers count from sheets in background
        def _fetch_initial():
            try:
                numbers = get_existing_numbers(self.webapp_url)
                self.existing_numbers_count = len(numbers)
            except Exception:
                pass
        threading.Thread(target=_fetch_initial, daemon=True).start()

    def _load_saved_leads(self) -> List[Dict[str, Any]]:
        import json
        if os.path.exists("leads_history.json"):
            try:
                with open("leads_history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _persist_leads(self):
        import json
        try:
            with open("leads_history.json", "w", encoding="utf-8") as f:
                json.dump(self.collected_leads, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Error saving leads]: {e}")

    def add_log(self, level: str, message: str):
        now_str = time.strftime("%H:%M:%S")
        entry = {"time": now_str, "level": level, "msg": message}
        self.logs.append(entry)
        # Keep recent 200 logs
        if len(self.logs) > 200:
            self.logs.pop(0)

    def start_scraping(self, keyword: str, target: int, areas: Optional[List[str]] = None, webapp_url: Optional[str] = None):
        if self.is_running:
            return False

        if webapp_url:
            self.webapp_url = webapp_url.strip()

        self.is_running = True
        self.stop_requested = False
        self.current_status = "RUNNING"
        self.current_keyword = keyword.strip()
        self.current_target = target
        self.current_count = 0
        self.current_message = "Menginisialisasi scraping..."
        self.add_log("INFO", f"Memulai scraping untuk: '{keyword}' (Target: {target} kontak)")

        areas_to_search = list(areas) if areas else list(AREAS_KALSEL)

        def runner():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(
                    self._async_scrape_process(
                        keyword=self.current_keyword,
                        target=self.current_target,
                        areas=areas_to_search,
                        webapp_url=self.webapp_url
                    )
                )
            except Exception as e:
                self.current_status = "ERROR"
                self.current_message = f"Terjadi kesalahan: {str(e)}"
                self.add_log("ERROR", f"Eksepsi Scraper: {str(e)}")
            finally:
                self.is_running = False
                loop.close()

        self.worker_thread = threading.Thread(target=runner, daemon=True)
        self.worker_thread.start()
        return True

    def stop_scraping(self):
        if self.is_running:
            self.stop_requested = True
            self.current_message = "Meminta penghentian proses..."
            self.add_log("WARN", "Penghentian manual diminta oleh pengguna.")

    async def _async_scrape_process(
        self,
        keyword: str,
        target: int,
        areas: List[str],
        webapp_url: str
    ):
        from playwright.async_api import async_playwright

        self.add_log("INFO", "Mengambil database nomor yang sudah ada dari Google Sheets...")
        update_live_progress("RUNNING", "Menyiapkan browser & database...", 0, webapp_url)
        
        existing_numbers = get_existing_numbers(webapp_url)
        self.existing_numbers_count = len(existing_numbers)
        self.add_log("SUCCESS", f"Berhasil memuat {len(existing_numbers)} nomor terdaftar.")

        total_saved = 0
        areas_copy = areas.copy()
        random.shuffle(areas_copy)

        # Launch browser with Google Chrome fallback or Chromium
        async with async_playwright() as p:
            browser = None
            chrome_app_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

            launch_options = {
                "headless": True,
                "args": ["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
            }

            try:
                if os.path.exists(chrome_app_path):
                    self.add_log("INFO", "Menggunakan Google Chrome lokal Mac...")
                    browser = await p.chromium.launch(
                        executable_path=chrome_app_path,
                        **launch_options
                    )
                else:
                    browser = await p.chromium.launch(
                        channel="chrome",
                        **launch_options
                    )
            except Exception as e:
                self.add_log("INFO", f"Menggunakan Chromium bawaan: {e}")
                browser = await p.chromium.launch(**launch_options)

            context = await browser.new_context(
                locale="id-ID",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            for area in areas_copy:
                if self.stop_requested or total_saved >= target:
                    break

                self.current_area = area
                self.current_message = f"Menyisir area: {area}"
                self.current_count = total_saved
                self.add_log("SEARCH", f"Menyisir: {area}...")
                update_live_progress("RUNNING", f"Menyisir: <b>{area}</b>", total_saved, webapp_url)

                if any(k in area.lower() for k in ["kalimantan", "jawa", "sulawesi", "sumatera", "jakarta", "bali", "kotamadya", "kabupaten", ","]):
                    query = f"{keyword} di {area}"
                else:
                    query = f"{keyword} di {area}, Kalimantan Selatan"
                url = f"https://www.google.com/maps/search/{query.replace(' ', '+')}"

                try:
                    await page.goto(url, timeout=35000)
                    await asyncio.sleep(2.0)

                    if self.stop_requested:
                        break

                    feed_selector = 'div[role="feed"]'
                    try:
                        await page.wait_for_selector(feed_selector, timeout=6000)
                    except Exception:
                        # Cek apakah Google Maps langsung membuka 1 tempat tunggal
                        name_el = page.locator('h1.DUwDvf')
                        if await name_el.count() > 0:
                            name = (await name_el.inner_text()).strip()
                            phone_el = page.locator('button[data-tooltip="Salin nomor telepon"], button[aria-label*="Telepon:"]')
                            raw_phone = ""
                            if await phone_el.count() > 0:
                                raw_phone = (await phone_el.first.get_attribute("aria-label")) or (await phone_el.first.inner_text())
                            phone = clean_phone(raw_phone)

                            if phone and phone not in existing_numbers:
                                addr_el = page.locator('button[data-tooltip="Salin alamat"], button[aria-label*="Alamat:"]')
                                address = (await addr_el.first.inner_text()).strip() if await addr_el.count() > 0 else ""
                                total_saved += 1
                                self.current_count = total_saved
                                existing_numbers.add(phone)
                                
                                lead_item = {
                                    "name": name,
                                    "category": keyword,
                                    "area": area,
                                    "phone": phone,
                                    "address": address,
                                    "url": page.url,
                                    "time": get_now_wita_str()
                                }
                                self.collected_leads.insert(0, lead_item)
                                self._persist_leads()
                                send_lead_to_master(name, keyword, area, phone, address, page.url, total_saved, webapp_url)
                                self.add_log("SUCCESS", f"[{total_saved}/{target}] Kontak Baru: {name} | {phone} ({area})")
                        continue

                    # Scroll feed untuk memuat lebih banyak hasil
                    for _ in range(3):
                        if self.stop_requested:
                            break
                        await page.hover(feed_selector)
                        await page.mouse.wheel(0, 3500)
                        await asyncio.sleep(1.0)

                    if self.stop_requested:
                        break

                    cards = await page.locator('div[role="feed"] > div > div[jsaction]').all()
                    for card in cards:
                        if self.stop_requested or total_saved >= target:
                            break

                        try:
                            await card.click()
                            await asyncio.sleep(1.4)

                            name_el = page.locator('h1.DUwDvf')
                            name = (await name_el.inner_text()).strip() if await name_el.count() > 0 else ""
                            if not name:
                                continue

                            phone_el = page.locator('button[data-tooltip="Salin nomor telepon"], button[aria-label*="Telepon:"]')
                            raw_phone = ""
                            if await phone_el.count() > 0:
                                raw_phone = (await phone_el.first.get_attribute("aria-label")) or (await phone_el.first.inner_text())

                            phone = clean_phone(raw_phone)
                            if not phone:
                                continue
                            if phone in existing_numbers:
                                self.add_log("SKIP", f"Nomor sudah ada (Skip): {name} ({phone})")
                                continue

                            addr_el = page.locator('button[data-tooltip="Salin alamat"], button[aria-label*="Alamat:"]')
                            address = (await addr_el.first.inner_text()).strip() if await addr_el.count() > 0 else ""

                            total_saved += 1
                            self.current_count = total_saved
                            existing_numbers.add(phone)

                            lead_item = {
                                "name": name,
                                "category": keyword,
                                "area": area,
                                "phone": phone,
                                "address": address,
                                "url": page.url,
                                "time": get_now_wita_str()
                            }
                            self.collected_leads.insert(0, lead_item)
                            self._persist_leads()

                            send_lead_to_master(name, keyword, area, phone, address, page.url, total_saved, webapp_url)
                            self.add_log("SUCCESS", f"[{total_saved}/{target}] Tersimpan: {name} | {phone} ({area})")

                            if total_saved >= target:
                                break

                        except Exception:
                            continue
                except Exception as ex:
                    self.add_log("WARN", f"Gagal memuat URL area {area}: {str(ex)[:80]}")
                    continue

            await browser.close()

        time_done = get_now_wita_str()
        if self.stop_requested:
            self.current_status = "STOPPED"
            self.current_message = f"Proses dihentikan manual. Terkumpul {total_saved}/{target} kontak."
            self.add_log("WARN", f"Proses dihentikan. Total tersimpan: {total_saved} kontak.")
            update_live_progress("STOPPED", f"Dihentikan manual pada {time_done}. Total {total_saved} kontak.", total_saved, webapp_url)
        else:
            self.current_status = "SELESAI"
            self.current_message = f"Selesai! Berhasil mengumpulkan {total_saved}/{target} kontak."
            self.add_log("SUCCESS", f"Pencarian tuntas. Total {total_saved}/{target} kontak berhasil disimpan.")
            update_live_progress("SELESAI", f"Sukses pada {time_done}! Target {total_saved} kontak tercapai.", total_saved, webapp_url)

    def start_listener(self, webapp_url: Optional[str] = None):
        """Start background polling listener for tasks from Google Sheets."""
        if self.listener_active:
            return

        if webapp_url:
            self.webapp_url = webapp_url.strip()

        self.listener_active = True
        self.add_log("INFO", "Background listener diaktifkan. Memantau perintah dari Google Sheets...")

        def listener_loop():
            while self.listener_active:
                try:
                    if not self.is_running:
                        task = check_remote_task(self.webapp_url)
                        if task and task.get("status") == "JALANKAN":
                            kw = task.get("keyword") or "toko bangunan"
                            tgt = int(task.get("target") or 5)
                            self.add_log("INFO", f"Menerima sinyal JALANKAN dari Google Sheets: '{kw}' (Target: {tgt})")
                            self.start_scraping(kw, tgt, webapp_url=self.webapp_url)
                except Exception as e:
                    self.add_log("WARN", f"Listener error: {e}")
                time.sleep(4)

        self.listener_thread = threading.Thread(target=listener_loop, daemon=True)
        self.listener_thread.start()

    def stop_listener(self):
        """Stop background listener."""
        self.listener_active = False
        self.add_log("INFO", "Background listener dinonaktifkan.")
