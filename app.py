import time
import pandas as pd
import streamlit as st
from config import DEFAULT_SHEETS_WEBAPP_URL, AREAS_KALSEL, REGIONS_KALSEL, PRESET_KEYWORDS
from scraper_engine import ScraperController
from sheets_service import get_existing_numbers, update_live_progress

# Configure Streamlit page
st.set_page_config(
    page_title="Canvassing Controller | Automated Scraper",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Clean & Minimalist CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main container background */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }

    /* Header styling */
    .app-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem 0 1.25rem 0;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    .app-title-box {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    .app-icon {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        width: 42px;
        height: 42px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
    }
    .app-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .app-subtitle {
        font-size: 0.82rem;
        color: #64748b;
        margin: 0;
    }

    /* Canvassing Controller Card (matching reference mockup) */
    .controller-panel {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.25rem;
    }
    .panel-header-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .inner-blue-box {
        background: #f8faff;
        border: 1px solid #dbeafe;
        border-radius: 12px;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
    }
    .inner-blue-title {
        color: #2563eb;
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    /* Metric cards */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.1rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    .metric-label {
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748b;
        margin-bottom: 0.35rem;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0f172a;
        margin: 0;
        line-height: 1.2;
    }
    .metric-sub {
        font-size: 0.75rem;
        color: #94a3b8;
        margin-top: 0.25rem;
    }

    /* Status Pills */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
    }
    .status-idle {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
    }
    .status-running {
        background-color: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }
    .status-selesai {
        background-color: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
    }
    .status-stopped {
        background-color: #fffbeb;
        color: #b45309;
        border: 1px solid #fde68a;
    }
    .status-error {
        background-color: #fef2f2;
        color: #b91c1c;
        border: 1px solid #fecaca;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }

    /* Primary green action button */
    div[data-testid="stButton"] button[kind="primary"] {
        background-color: #16a34a !important;
        border-color: #15803d !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        padding: 0.6rem 1.25rem !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(22, 163, 74, 0.25) !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        background-color: #15803d !important;
        border-color: #166534 !important;
        box-shadow: 0 4px 10px rgba(22, 163, 74, 0.35) !important;
    }

    /* Secondary button styling */
    div[data-testid="stButton"] button[kind="secondary"] {
        border-radius: 8px !important;
        font-weight: 600 !important;
    }

    /* Activity Terminal */
    .terminal-container {
        background-color: #0f172a;
        color: #e2e8f0;
        font-family: 'JetBrains Mono', monospace;
        border-radius: 12px;
        padding: 1rem;
        height: 280px;
        overflow-y: auto;
        font-size: 0.78rem;
        line-height: 1.5;
        border: 1px solid #1e293b;
    }
    .log-line {
        margin-bottom: 0.25rem;
        word-break: break-all;
    }
    .log-time { color: #64748b; }
    .log-INFO { color: #38bdf8; font-weight: 600; }
    .log-SUCCESS { color: #4ade80; font-weight: 600; }
    .log-SEARCH { color: #fbbf24; font-weight: 600; }
    .log-SKIP { color: #94a3b8; }
    .log-WARN { color: #f87171; font-weight: 600; }
    .log-ERROR { color: #ef4444; font-weight: 700; }

    /* Leads Card */
    .lead-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 0.85rem 1rem;
        margin-bottom: 0.65rem;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .lead-card:hover {
        border-color: #3b82f6;
        transform: translateY(-1px);
    }
    .lead-name {
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e293b;
    }
    .lead-phone {
        font-family: 'JetBrains Mono', monospace;
        color: #059669;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .lead-meta {
        font-size: 0.76rem;
        color: #64748b;
        margin-top: 0.25rem;
    }

    /* Hide default streamlit decorations */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 2rem !important;
        max-width: 1400px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize Controller
controller = ScraperController()

if "prev_running" not in st.session_state:
    st.session_state.prev_running = controller.is_running

# Top Navigation Bar
st.markdown(
    """
    <div class="app-header">
        <div class="app-title-box">
            <div class="app-icon">📍</div>
            <div>
                <h1 class="app-title">Canvassing Controller</h1>
                <p class="app-subtitle">Automated Lead Scraper & Real-time Google Sheets Synchronization</p>
            </div>
        </div>
        <div>
            <span class="status-pill status-idle" id="live-badge">Sistem Aktif</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Quick Preset State
if "search_keyword" not in st.session_state:
    st.session_state.search_keyword = "warung makan"
if "target_count" not in st.session_state:
    st.session_state.target_count = 5

# Main Layout: 2 Columns (Left: Controller Card, Right: Live Dashboard & Feeds)
col_ctrl, col_dash = st.columns([1, 1.6], gap="large")

with col_ctrl:
    with st.container(border=True):
        # Status Header
        status_class = {
            "IDLE": "status-idle",
            "RUNNING": "status-running",
            "SELESAI": "status-selesai",
            "STOPPED": "status-stopped",
            "ERROR": "status-error",
        }.get(controller.current_status, "status-idle")

        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.85rem;">
                <span style="font-size: 1.15rem; font-weight: 700; color: #1e293b;">Canvassing Controller</span>
                <span class="status-pill {status_class}">{controller.current_status}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Inner Card (Matching reference UI: "Automated Canvassing")
        with st.container(border=True):
            st.markdown(
                """
                <h4 style="color: #2563eb; font-size: 1.05rem; font-weight: 700; margin-top: 0; margin-bottom: 0.75rem;">
                    Automated Canvassing
                </h4>
                """,
                unsafe_allow_html=True,
            )

            # Form inputs
            keyword_input = st.text_input(
                "Kata Kunci Usaha",
                value=st.session_state.search_keyword,
                placeholder="Contoh: warung makan, toko bangunan...",
                help="Kategori atau jenis usaha yang ingin Anda targetkan di Google Maps.",
                disabled=controller.is_running,
            )

            # Keyword Chips / Suggestions
            st.caption("Pilihan Cepat Kategori:")
            selected_pill = st.pills(
                "Pilihan Cepat",
                options=PRESET_KEYWORDS[:6],
                selection_mode="single",
                label_visibility="collapsed",
                disabled=controller.is_running,
            )
            if selected_pill and selected_pill != st.session_state.search_keyword:
                st.session_state.search_keyword = selected_pill
                st.rerun()

            target_input = st.number_input(
                "Target Kontak Baru",
                min_value=1,
                max_value=500,
                value=st.session_state.target_count,
                step=1,
                help="Jumlah lead unik baru yang ingin dicari sebelum proses berhenti otomatis.",
                disabled=controller.is_running,
            )

            # Pengaturan Wilayah / Daerah Target
            st.markdown("<div style='margin-top: 0.6rem; font-size: 0.86rem; font-weight: 700; color: #334155;'>📍 Pengaturan Wilayah Target:</div>", unsafe_allow_html=True)
            area_mode = st.radio(
                "Mode Wilayah",
                options=["Semua Kalsel", "Pilih Kota / Kab", "Pilih Kecamatan", "Kustom / Kota Lain"],
                horizontal=True,
                label_visibility="collapsed",
                disabled=controller.is_running,
            )

            final_selected_areas = None

            if area_mode == "Semua Kalsel":
                final_selected_areas = AREAS_KALSEL
                st.caption("✅ Menyisir seluruh kecamatan & kota di Kalimantan Selatan secara acak presisi.")

            elif area_mode == "Pilih Kota / Kab":
                selected_cities = st.multiselect(
                    "Pilih Kabupaten / Kota:",
                    options=list(REGIONS_KALSEL.keys()),
                    default=["Kota Banjarmasin", "Kota Banjarbaru"],
                    disabled=controller.is_running,
                    help="Semua kecamatan di dalam kota/kabupaten yang dipilih akan disisir otomatis."
                )
                if selected_cities:
                    final_selected_areas = [area for city in selected_cities for area in REGIONS_KALSEL[city]]
                    st.caption(f"📍 Mencakup {len(final_selected_areas)} kecamatan di {len(selected_cities)} wilayah.")
                else:
                    st.warning("Pilih minimal satu kota/kabupaten.")
                    final_selected_areas = AREAS_KALSEL

            elif area_mode == "Pilih Kecamatan":
                chosen_kec = st.multiselect(
                    "Pilih Kecamatan / Daerah Spesifik:",
                    options=AREAS_KALSEL,
                    default=["Banjarmasin Tengah", "Banjarbaru Utara", "Martapura"],
                    disabled=controller.is_running,
                    help="Ketik untuk mencari kecamatan tertentu."
                )
                final_selected_areas = chosen_kec if chosen_kec else AREAS_KALSEL
                st.caption(f"📍 {len(final_selected_areas)} kecamatan spesifik dipilih.")

            elif area_mode == "Kustom / Kota Lain":
                custom_area_text = st.text_input(
                    "Ketik Kota / Daerah Bebas (pisahkan koma):",
                    value="Banjarmasin, Banjarbaru, Martapura",
                    placeholder="Contoh: Balikpapan, Samarinda, Jakarta Selatan, Surabaya...",
                    disabled=controller.is_running,
                    help="Bisa diisi nama kota mana saja di Indonesia."
                )
                parsed = [x.strip() for x in custom_area_text.split(",") if x.strip()]
                final_selected_areas = parsed if parsed else AREAS_KALSEL
                st.caption(f"📍 Mencakup {len(final_selected_areas)} lokasi kustom.")

            st.session_state["active_areas"] = final_selected_areas

            # Primary Action Button inside the inner card
            if not controller.is_running:
                if st.button("Mulai Cari Data", type="primary", use_container_width=True):
                    if not keyword_input.strip():
                        st.error("Mohon isi Kata Kunci Usaha terlebih dahulu.")
                    else:
                        st.session_state.search_keyword = keyword_input
                        st.session_state.target_count = target_input
                        controller.start_scraping(
                            keyword=keyword_input,
                            target=int(target_input),
                            areas=final_selected_areas,
                            webapp_url=st.session_state.get("custom_sheets_url", controller.webapp_url)
                        )
                        st.rerun()
            else:
                if st.button("⏹️ Hentikan Proses", type="secondary", use_container_width=True):
                    controller.stop_scraping()
                    st.rerun()

        # Action bar under card
        sub_c1, sub_c2 = st.columns(2)
        with sub_c1:
            if st.button("🧹 Bersihkan Feed", use_container_width=True, disabled=controller.is_running):
                controller.collected_leads = []
                controller.logs = []
                st.rerun()
        with sub_c2:
            if st.button("🔄 Cek Koneksi Sheets", use_container_width=True):
                with st.spinner("Menghubungi Google Sheets..."):
                    existing = get_existing_numbers(controller.webapp_url)
                    controller.existing_numbers_count = len(existing)
                    st.toast(f"Terkoneksi! {len(existing)} nomor di database.")
                    st.rerun()

        # Webhook & Google Sheets Setting Expander
        with st.expander("🔗 Konfigurasi Google Sheets WebApp", expanded=False):
            custom_url = st.text_input(
                "URL WebApp Google Sheets:",
                value=controller.webapp_url,
                disabled=controller.is_running,
                help="URL Google Apps Script Web App tempat lead akan disimpan secara otomatis."
            )
            st.session_state["custom_sheets_url"] = custom_url

        # Background Listener Switch (Listening to Google Sheets triggers)
        st.markdown("<hr style='margin: 1rem 0 0.75rem 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 0.95rem; font-weight: 700; color: #1e293b; margin-bottom: 0.25rem;'>⚡ Otomatisasi Google Sheets</div>", unsafe_allow_html=True)
        st.caption("Jika diaktifkan, server ini memantau perintah 'JALANKAN' dari spreadsheet di latar belakang.")

        listen_col1, listen_col2 = st.columns([1.5, 1])
        with listen_col1:
            is_active = controller.listener_active
            if not is_active:
                if st.button("🟢 Aktifkan Listener", use_container_width=True):
                    controller.start_listener(webapp_url=st.session_state.get("custom_sheets_url", controller.webapp_url))
                    st.rerun()
            else:
                if st.button("🔴 Matikan Listener", use_container_width=True):
                    controller.stop_listener()
                    st.rerun()

        with listen_col2:
            if controller.listener_active:
                st.markdown('<div style="padding-top: 6px;"><span class="status-pill status-running">● Aktif</span></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div style="padding-top: 6px;"><span class="status-pill status-idle">● Standby</span></div>', unsafe_allow_html=True)



# Right Column: Live Execution Monitor, KPI Metrics, Leads Feed & Terminal
with col_dash:
    # Fragment to auto-refresh live scraping stats smoothly
    @st.fragment(run_every=2 if controller.is_running else None)
    def render_live_dashboard():
        # Auto-sync entire page when background scraping transitions
        if st.session_state.get("prev_running") and not controller.is_running:
            st.session_state.prev_running = False
            st.rerun()
        if controller.is_running:
            st.session_state.prev_running = True

        # Top KPI Metric Cards
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Target Kontak</div>
                    <div class="metric-value">{controller.current_target if controller.current_target else target_input}</div>
                    <div class="metric-sub">Batas maksimal</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m_col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Tersimpan (Sesi)</div>
                    <div class="metric-value" style="color: #16a34a;">{len(controller.collected_leads)}</div>
                    <div class="metric-sub">{controller.current_count} lead diproses</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m_col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Di Google Sheets</div>
                    <div class="metric-value" style="color: #2563eb;">{controller.existing_numbers_count}</div>
                    <div class="metric-sub">Nomor terdaftar</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with m_col4:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">Status Mesin</div>
                    <div class="metric-value" style="font-size: 1.15rem; color: #475569; padding-top: 0.35rem;">
                        {controller.current_status}
                    </div>
                    <div class="metric-sub">{getattr(controller, 'current_area', '') if getattr(controller, 'current_area', '') else 'Siap'}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

        # Live Progress Bar & Alert Message
        target_val = max(controller.current_target, 1)
        progress_pct = min(1.0, float(len(controller.collected_leads)) / float(target_val)) if controller.is_running else (1.0 if controller.current_status == "SELESAI" else 0.0)

        if controller.is_running:
            st.progress(progress_pct, text=f"Sedang Menyisir Google Maps ({int(progress_pct * 100)}%) — {controller.current_message}")
        elif controller.current_status == "SELESAI":
            st.success(f"🎉 {controller.current_message}")
        elif controller.current_status == "STOPPED":
            st.warning(f"⚠️ {controller.current_message}")
        elif controller.current_status == "ERROR":
            st.error(f"❌ {controller.current_message}")

        # Tabs for Leads Feed, Table View & System Terminal Logs
        tab_feed, tab_table, tab_terminal = st.tabs(["📋 Feed Kontak Baru", "📊 Tabel Data & Ekspor", "🖥️ Terminal Aktivitas"])

        with tab_feed:
            if not controller.collected_leads:
                st.markdown(
                    """
                    <div style="text-align: center; padding: 2.5rem 1rem; color: #94a3b8; background: #ffffff; border-radius: 12px; border: 1px dashed #cbd5e1;">
                        <div style="font-size: 2.2rem; margin-bottom: 0.5rem;">🔍</div>
                        <div style="font-weight: 600; color: #64748b;">Belum ada lead kontak yang dikumpulkan</div>
                        <div style="font-size: 0.8rem; margin-top: 0.25rem;">Masukkan kata kunci dan klik <b>Mulai Cari Data</b> untuk memulai.</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.caption(f"Menampilkan {len(controller.collected_leads)} kontak terbaru:")
                for item in controller.collected_leads[:20]:
                    wa_clean = item["phone"].replace("+", "")
                    st.markdown(
                        f"""
                        <div class="lead-card">
                            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                                <div>
                                    <div class="lead-name">{item['name']}</div>
                                    <div class="lead-phone">📞 {item['phone']}</div>
                                </div>
                                <div style="display: flex; gap: 0.4rem;">
                                    <a href="https://wa.me/{wa_clean}" target="_blank" style="text-decoration: none; background: #25d366; color: white; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.72rem; font-weight: 700;">WhatsApp</a>
                                    <a href="{item.get('url', '#')}" target="_blank" style="text-decoration: none; background: #f1f5f9; color: #3b82f6; border: 1px solid #cbd5e1; padding: 0.25rem 0.6rem; border-radius: 6px; font-size: 0.72rem; font-weight: 600;">Maps</a>
                                </div>
                            </div>
                            <div class="lead-meta">
                                📍 <b>{item.get('area', '-')}</b> | 🏢 {item.get('address', 'Alamat tidak tersedia')} | ⏱️ {item.get('time', '')}
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        with tab_table:
            if controller.collected_leads:
                df = pd.DataFrame(controller.collected_leads)
                st.dataframe(df, use_container_width=True, height=300)

                # Export Options
                csv_data = df.to_csv(index=False).encode("utf-8")
                exp_c1, exp_c2 = st.columns(2)
                with exp_c1:
                    st.download_button(
                        label="📥 Download Data CSV",
                        data=csv_data,
                        file_name=f"canvassing_leads_{int(time.time())}.csv",
                        mime="text/csv",
                        use_container_width=True,
                    )
                with exp_c2:
                    st.link_button("🌐 Buka Google Sheets", "https://docs.google.com/spreadsheets", use_container_width=True)
            else:
                st.info("Tabel data akan muncul saat kontak berhasil ditemukan.")

        with tab_terminal:
            st.caption("Live Real-time Terminal Log:")
            log_entries_html = []
            for log in reversed(controller.logs[-50:]):
                lvl = log.get("level", "INFO")
                msg = log.get("msg", "")
                t = log.get("time", "")
                log_entries_html.append(
                    f'<div class="log-line"><span class="log-time">[{t}]</span> <span class="log-{lvl}">[{lvl}]</span> {msg}</div>'
                )
            
            terminal_body = "\n".join(log_entries_html) if log_entries_html else '<div class="log-line" style="color: #64748b;">Menunggu aktivitas...</div>'
            st.markdown(
                f'<div class="terminal-container">{terminal_body}</div>',
                unsafe_allow_html=True,
            )

    render_live_dashboard()
