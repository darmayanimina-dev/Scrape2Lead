"""Configuration and constants for Canvassing Controller."""

DEFAULT_SHEETS_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbycnb7EsL_ldH5P_pUTQ9ovaYYZoIc5lfctuB97cmkqcdDVEuml0qBHc7Iqp-Zm7kEOPw/exec"

REGIONS_KALSEL = {
    "Kota Banjarmasin": [
        "Banjarmasin Tengah",
        "Banjarmasin Barat",
        "Banjarmasin Timur",
        "Banjarmasin Selatan",
        "Banjarmasin Utara"
    ],
    "Kota Banjarbaru": [
        "Banjarbaru Utara",
        "Banjarbaru Selatan",
        "Landasan Ulin",
        "Liang Anggang",
        "Cempaka Banjarbaru"
    ],
    "Kab. Banjar (Martapura)": [
        "Martapura",
        "Kertak Hanyar",
        "Gambut",
        "Sungai Tabuk",
        "Simpang Empat Banjar",
        "Mataraman",
        "Karang Intan"
    ],
    "Kab. Tanah Laut (Pelaihari)": [
        "Pelaihari",
        "Bati-Bati",
        "Tambang Ulang",
        "Kintap",
        "Jorong"
    ],
    "Kab. Barito Kuala": [
        "Alalak",
        "Marabahan",
        "Mandastana",
        "Anjir Muara"
    ],
    "Banua Enam (Tapin, HSS, HST, HSU, Tabalong)": [
        "Rantau Tapin",
        "Kandangan",
        "Barabai",
        "Amuntai",
        "Tanjung Tabalong",
        "Murung Pudak"
    ],
    "Tanah Bumbu & Kotabaru": [
        "Batulicin",
        "Simpang Empat Tanah Bumbu",
        "Satui",
        "Kotabaru Pulau Laut"
    ],
    "Perbatasan Kalteng": [
        "Kuala Kapuas"
    ]
}

# Flatten list of all Kalsel districts
AREAS_KALSEL = [area for sublist in REGIONS_KALSEL.values() for area in sublist]

PRESET_KEYWORDS = [
    "warung makan",
    "toko bangunan",
    "showroom mobil",
    "bengkel motor",
    "distributor sembako",
    "toko listrik",
    "cafe & resto",
    "apotek",
    "toko pertanian",
    "percetakan"
]
