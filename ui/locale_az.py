"""KƏŞF — Azərbaycan dili lokalizasiyası
Bütün istifadəçiyə baxan mətnlər burada saxlanılır.
Hər bir modul öz bölməsində qruplaşdırılıb.
"""

# ═══════════════════════════════════════════════════════════
#  APPLICATION IDENTITY
# ═══════════════════════════════════════════════════════════

APP_NAME = "KƏŞF"
APP_FULL_NAME = "Kibernetik Əlaqə və Şəbəkə Forensikası"
APP_SUBTITLE = "Rəqəmsal İz Kəşfiyyat Sistemi"
APP_VERSION = "1.0.0"
APP_AUTHOR = "KƏŞF Layihəsi"
APP_LICENSE = "Yalnız daxili istifadə üçün"
APP_DISCLAIMER = (
    "Bu alət yalnız qanuni və etik OSINT tədqiqatları üçün nəzərdə tutulub. "
    "İcazəsiz istifadə qadağandır."
)
APP_WELCOME = "KƏŞF kəşfiyyat sisteminə xoş gəlmisiniz."
APP_INITIALIZING = "⚙  Sistem komponentləri yüklənir..."
APP_READY = "✅ Sistem hazırdır. Əmrlərinizi gözləyir."
APP_SHUTTING_DOWN = "🔒 Sistem bağlanır. Təhlükəsiz çıxış..."

# ═══════════════════════════════════════════════════════════
#  OPSEC MODULE
# ═══════════════════════════════════════════════════════════

OPSEC_CHECKING_VPN = "🛡  VPN bağlantısı yoxlanılır..."
OPSEC_VPN_ACTIVE = "✅ VPN aktiv: {interface}"
OPSEC_VPN_NOT_FOUND = "⛔ XƏBƏRDARLIQ: VPN bağlantısı tapılmadı!"
OPSEC_VPN_REQUIRED = "Mullvad VPN olmadan davam etmək mümkün deyil."
OPSEC_VPN_CONNECTING = "🔄 VPN-ə qoşulur..."
OPSEC_VPN_RECONNECTING = "🔄 VPN yenidən qoşulur..."
OPSEC_VPN_CONNECTED = "✅ VPN uğurla qoşuldu."
OPSEC_VPN_TIMEOUT = "⏰ VPN bağlantı vaxtı bitdi. Yenidən cəhd edin."
OPSEC_FETCHING_IP = "🌐 Cari IP məlumatları alınır..."
OPSEC_IP_INFO = "IP: {ip} | ISP: {isp} | Ölkə: {country} | Şəhər: {city}"
OPSEC_IP_FETCH_FAILED = "❌ IP məlumatları alına bilmədi: {error}"
OPSEC_IDENTITY_CONFIRM = "[?] Şəxsiyyətiniz qorunurmu? Davam etmək istəyirsiniz? (B/X): "
OPSEC_CONFIRMED = "✅ OpSec yoxlaması keçdi. Modullar aktivləşdirilir..."
OPSEC_DENIED = "❌ İstifadəçi təsdiqi rədd etdi. Çıxış edilir."
OPSEC_DNS_LEAK = "⚠  DNS sızma aşkarlandı! DNS serveriniz: {dns}"
OPSEC_DNS_SAFE = "✅ DNS təhlükəsizdir."
OPSEC_DNS_CHECKING = "🔍 DNS sızma testi aparılır..."
OPSEC_VPN_DROPPED = "⛔ VPN bağlantısı kəsildi! Bütün sorğular dayandırıldı!"
OPSEC_VPN_RESTORED = "✅ VPN bağlantısı bərpa olundu."
OPSEC_KILL_SWITCH = "🛑 Kill switch aktivləşdirildi. Şəbəkə trafiki bloklandı."
OPSEC_KILL_SWITCH_OFF = "✅ Kill switch deaktiv edildi."
OPSEC_TOR_DETECTED = "🧅 Tor çıxış nodu aşkarlandı. Əlavə ehtiyat tədbirləri tətbiq edilir."
OPSEC_REAL_IP_EXPOSED = "🚨 TƏHLÜKƏ: Həqiqi IP ünvanınız ifşa oluna bilər!"
OPSEC_FIREWALL_CHECK = "🔥 Firewall qaydaları yoxlanılır..."
OPSEC_FIREWALL_OK = "✅ Firewall düzgün konfiqurasiya edilib."
OPSEC_FIREWALL_WARN = "⚠  Firewall konfiqurasiyasında problem aşkarlandı."
OPSEC_WEBRTC_LEAK = "⚠  WebRTC sızması mümkündür. Brauzerdə WebRTC-ni söndürün."
OPSEC_WEBRTC_SAFE = "✅ WebRTC sızması aşkarlanmadı."
OPSEC_CHECK_COMPLETE = "✅ Bütün OpSec yoxlamaları tamamlandı."
OPSEC_CHECK_FAILED = "❌ OpSec yoxlaması uğursuz oldu. Davam etmək təhlükəlidir."
OPSEC_MONITORING = "👁  Şəbəkə monitorinqi aktiv. Hər hansı anomaliya izlənir."
OPSEC_ANOMALY_DETECTED = "🚨 Şəbəkə anomaliyası aşkarlandı: {details}"

# ═══════════════════════════════════════════════════════════
#  THROTTLE / RATE LIMITING
# ═══════════════════════════════════════════════════════════

THROTTLE_WAITING = "⏳ Gözlənilir... ({seconds} saniyə)"
THROTTLE_RATE_LIMITED = "⚠  Sorğu limiti aşıldı. {seconds} saniyə gözlənilir."
THROTTLE_QUERY_COUNT = "Sorğular: {current}/{max}"
THROTTLE_COOLDOWN = "❄  Soyuma dövrü: {seconds} saniyə qaldı."
THROTTLE_RESUMING = "▶  Sorğular davam etdirilir."
THROTTLE_BACKOFF = "⏳ Eksponensial gözləmə: {seconds} saniyə."
THROTTLE_BLOCKED = "🚫 Müvəqqəti bloklandı. {minutes} dəqiqə gözlənilir."
THROTTLE_QUOTA_RESET = "🔄 Kvota sıfırlanacaq: {time}"
THROTTLE_ADAPTIVE = "📊 Adaptiv tənzimləmə: sorğu sürəti {rate}/dəq olaraq ayarlandı."

# ═══════════════════════════════════════════════════════════
#  BROWSER MODULE
# ═══════════════════════════════════════════════════════════

BROWSER_LAUNCHING = "🌐 Brave brauzer işə salınır (gizli rejim)..."
BROWSER_LAUNCHED = "✅ Brauzer hazırdır."
BROWSER_ERROR = "❌ Brauzer işə salına bilmədi: {error}"
BROWSER_BRAVE_NOT_FOUND = "❌ Brave brauzer tapılmadı: {path}"
BROWSER_CLOSING = "🔒 Brauzer bağlanır..."
BROWSER_CLOSED = "✅ Brauzer uğurla bağlandı."
BROWSER_NAVIGATING = "🔗 Səhifəyə keçilir: {url}"
BROWSER_PAGE_LOADED = "✅ Səhifə yükləndi: {url}"
BROWSER_PAGE_TIMEOUT = "⏰ Səhifə yüklənmə vaxtı bitdi: {url}"
BROWSER_PAGE_ERROR = "❌ Səhifə xətası: {url} — {error}"
BROWSER_SCREENSHOT = "📸 Ekran görüntüsü saxlanıldı: {path}"
BROWSER_CAPTCHA = "⚠  CAPTCHA aşkarlandı. Manual müdaxilə lazım ola bilər."
BROWSER_BLOCKED = "🚫 Brauzer bloklandı. IP dəyişdirilməsi tövsiyə olunur."
BROWSER_COOKIES_CLEARED = "🍪 Çərəzlər təmizləndi."
BROWSER_CACHE_CLEARED = "🧹 Brauzer keşi təmizləndi."
BROWSER_PROFILE_CREATED = "📂 Yeni brauzer profili yaradıldı: {name}"
BROWSER_JS_DISABLED = "🔒 JavaScript söndürüldü."
BROWSER_JS_ENABLED = "✅ JavaScript aktivdir."
BROWSER_USER_AGENT = "🔧 User-Agent dəyişdirildi: {ua}"
BROWSER_PROXY_SET = "🔧 Proksi ayarlandı: {proxy}"
BROWSER_DOWNLOADING = "⬇  Fayl yüklənir: {filename}"
BROWSER_DOWNLOAD_COMPLETE = "✅ Yükləmə tamamlandı: {filename}"
BROWSER_LAUNCH_ERROR = "❌ Brauzer başlama xətası"
BROWSER_NAVIGATE_ERROR = "❌ Naviqasiya xətası"
BROWSER_SEARCHING = "🔍 Axtarılır: {engine} - {query}"
BROWSER_SEARCH_COMPLETE = "✅ Axtarış bitdi: {count} nəticə ({engine})"
BROWSER_SEARCH_ERROR = "❌ Axtarış xətası: {engine}"
BROWSER_CAPTCHA_DETECTED = "⚠ CAPTCHA aşkarlandı!"
BROWSER_TYPING = "⌨ Yazılır: {count} simvol"
BROWSER_COOKIE_ACCEPT = "🍪 Çərəz qəbul edildi: {selector}"

# ═══════════════════════════════════════════════════════════
#  DORKING / SEARCH ENGINE
# ═══════════════════════════════════════════════════════════

DORK_STARTING = "🔍 Axtarış başladılır..."
DORK_ENGINE = "Axtarış motoru: {engine}"
DORK_QUERY = "Sorğu: {query}"
DORK_RESULTS_FOUND = "📋 {count} nəticə tapıldı."
DORK_NO_RESULTS = "Nəticə tapılmadı."
DORK_PROCESSING = "⚙  Nəticələr emal edilir..."
DORK_COMPLETE = "✅ Axtarış tamamlandı. Cəmi: {total} nəticə."
DORK_GENERATING = "⚙ Sorğular yaradılır..."
DORK_GENERATED = "✅ {count} sorğu yaradıldı."
DORK_TEMPLATE_LOAD_ERROR = "❌ Şablonlar yüklənə bilmədi: {0}"
DORK_EXECUTING = "▶ İcra edilir: {0} ({1})"
DORK_RESULT_COUNT = "📋 {0} yeni nəticə tapıldı (ümumi: {1})"
DORK_CAMPAIGN_START = "🚀 Axtarış kampaniyası başladılır..."
DORK_CAMPAIGN_PROGRESS = "İcra edilir"
DORK_CAMPAIGN_COMPLETE = "✅ Kampaniya bitdi. Cəmi: {total} nəticə, {docs} sənəd."
DORK_DEDUP_COUNT = "🔁 Dublikatlar təmizləndi."
DORK_DOCUMENT_FOUND = "📄 Sənəd tapıldı [{doc_type}]: {url}"
DORK_LIMIT_REACHED = "⚠ Sorğu limitinə çatıldı."
DORK_ENGINE_ROTATE = "🔄 Motor dəyişdirilir: {0} -> {1}"
DORK_CATEGORY = "📁 Kateqoriya: {category}"
DORK_PAGE = "Səhifə: {current}/{total}"
DORK_NEXT_PAGE = "➡  Növbəti səhifəyə keçilir..."
DORK_LAST_PAGE = "📄 Son səhifəyə çatıldı."
DORK_DUPLICATE = "🔁 Dublikat nəticə süzüldü: {url}"
DORK_FILTERED = "🔍 {count} nəticə süzgəcdən keçirildi."
DORK_EXPORTING = "📤 Nəticələr ixrac edilir..."
DORK_EXPORTED = "✅ Nəticələr ixrac edildi: {path}"
DORK_QUEUED = "📋 Sorğu növbəyə əlavə edildi: {query}"
DORK_QUEUE_SIZE = "📋 Növbədəki sorğular: {count}"
DORK_SKIPPING_ENGINE = "⏭  {engine} motoru keçilir (əlçatmazdır)."
DORK_SOCIAL_HIT = "📱 Sosial media profili tapıldı: {platform}"
DORK_EMAIL_HIT = "📧 E-poçt ünvanı tapıldı: {email}"
DORK_PHONE_HIT = "📞 Telefon nömrəsi tapıldı: {phone}"
DORK_USERNAME_HIT = "👤 İstifadəçi adı tapıldı: {username}"
DORK_PHOTO_HIT = "🖼  Şəkil tapıldı: {url}"

# ═══════════════════════════════════════════════════════════
#  DOCUMENT HANDLER
# ═══════════════════════════════════════════════════════════

DOC_FOUND = "📄 Sənəd aşkarlandı!"
DOC_FILE_NAME = "Fayl adı: {name}"
DOC_FILE_URL = "🔗 URL: {url}"
DOC_FILE_CONTEXT = "📝 Kontekst: {context}"
DOC_FILE_SIZE = "📏 Ölçü: {size}"
DOC_FILE_TYPE = "📎 Fayl növü: {type}"
DOC_FILE_HASH = "🔐 SHA-256: {hash}"
DOC_DOWNLOAD_PROMPT = "[?] Bu sənəd yüklənib analiz edilsin? (B/X): "
DOC_DOWNLOADING = "⬇  Sənəd sandbox-a yüklənir..."
DOC_DOWNLOAD_SUCCESS = "✅ Sənəd uğurla yükləndi."
DOC_DOWNLOAD_FAILED = "❌ Sənəd yüklənə bilmədi: {error}"
DOC_DOWNLOAD_PROGRESS = "⬇  Yükləmə: {percent}% ({downloaded}/{total})"
DOC_SKIPPED = "⏭  Sənəd keçildi. Link jurnala yazıldı."
DOC_PARSING = "⚙  Sənəd analiz edilir..."
DOC_PARSE_FAILED = "❌ Sənəd analiz edilə bilmədi: {error}"
DOC_METADATA = "📋 Metadata:"
DOC_AUTHOR = "  Müəllif: {author}"
DOC_CREATED = "  Yaranma tarixi: {date}"
DOC_MODIFIED = "  Son dəyişiklik: {date}"
DOC_SOFTWARE = "  Proqram: {software}"
DOC_TITLE = "  Başlıq: {title}"
DOC_PAGES = "  Səhifə sayı: {count}"
DOC_LANGUAGE = "  Dil: {lang}"
DOC_ENCRYPTED = "🔐 Sənəd şifrələnib. Açmaq üçün parol lazımdır."
DOC_UNSUPPORTED = "⚠  Dəstəklənməyən fayl növü: {type}"
DOC_TOO_LARGE = "⚠  Fayl çox böyükdür (>{max_mb}MB). Keçilir."
DOC_TEXT_EXTRACTED = "📝 {chars} simvol mətn çıxarıldı."
DOC_NEW_CLUES = "🔎 {count} yeni ipucu tapıldı!"
DOC_CLUE_EMAIL = "  📧 E-poçt: {email}"
DOC_CLUE_PHONE = "  📞 Telefon: {phone}"
DOC_CLUE_NAME = "  👤 Ad: {name}"
DOC_CLUE_ADDRESS = "  📍 Ünvan: {address}"
DOC_CLUE_URL = "  🔗 URL: {url}"
DOC_CLUE_DATE = "  📅 Tarix: {date}"
DOC_QUARANTINED = "🔒 Sənəd karantinə alındı: {path}"
DOC_SCAN_CLEAN = "✅ Sənəd təhlükəsizdir."
DOC_SCAN_SUSPICIOUS = "⚠  Sənəddə şübhəli məzmun aşkarlandı!"
DOC_EXIF_FOUND = "📸 EXIF məlumatları tapıldı!"
DOC_EXIF_GPS = "  📍 GPS koordinatları: {lat}, {lon}"
DOC_EXIF_CAMERA = "  📷 Kamera: {camera}"
DOC_EXIF_DATE = "  📅 Çəkilmə tarixi: {date}"
DOC_FOUND_TITLE = "Sənəd Aşkarlandı!"
DOC_FILENAME_LABEL = "Fayl adı:"
DOC_URL_LABEL = "URL:"
DOC_CONTEXT_LABEL = "Kontekst:"
DOC_TYPE_LABEL = "Növ:"
DOC_DOWNLOAD_ERROR = "❌ Yükləmə xətası"
DOC_DOWNLOAD_SKIPPED = "⏭ Sənəd yüklənmədi."
DOC_EXTRACTING = "⚙ Mətn çıxarılır..."
DOC_EXTRACT_SUCCESS = "✅ Mətn uğurla çıxarıldı."
DOC_EXTRACT_ERROR = "❌ Çıxarma xətası"
DOC_UNSUPPORTED_TYPE = "⚠ Dəstəklənməyən növ: {file_type}"
DOC_SIZE_EXCEEDED = "⚠ Fayl çox böyükdür: {size}MB (Max: {max_size}MB)"
DOC_CLUES_FOUND = "🔎 {count} ipucu tapıldı!"
DOC_METADATA_TITLE = "📋 METADATA"
DOC_METADATA_AUTHOR = "Müəllif:"
DOC_METADATA_CREATED = "Yaradılıb:"
DOC_METADATA_MODIFIED = "Dəyişdirilib:"
DOC_METADATA_CREATOR = "Proqram:"
DOC_CLEANUP_DONE = "🧹 Təmizlik tamamlandı."
DOC_SANDBOX_CREATED = "📂 Sandbox yaradıldı: {0}"

# ═══════════════════════════════════════════════════════════
#  INTELLIGENCE ENGINE
# ═══════════════════════════════════════════════════════════

INTEL_STARTING = "🧠 Kəşfiyyat mühərriki işə salınır..."
INTEL_SEED_DATA = "🎯 İlkin məlumatlar yükləndi: {count} data nöqtəsi"
INTEL_SEARCHING = "🔍 Axtarış dərinliyi: {depth}/{max_depth}"
INTEL_NEW_PIVOT = "🔄 Yeni pivot nöqtəsi aşkarlandı: {value} (etibar: {confidence}%)"
INTEL_LOW_CONFIDENCE = "⚠  Aşağı etibar nöqtəsi: {value} ({confidence}%)"
INTEL_CONFIRM_PIVOT = "[?] Bu məlumat hədəf şəxsə aiddir? (B/X): "
INTEL_PIVOT_ACCEPTED = "✅ Pivot təsdiqləndi. Yeni axtarış başladılır."
INTEL_PIVOT_REJECTED = "❌ Pivot rədd edildi. Qrafdan silinir."
INTEL_MAX_DEPTH = "📊 Maksimum axtarış dərinliyinə çatıldı."
INTEL_MAX_QUERIES = "📊 Maksimum sorğu sayına çatıldı ({max})."
INTEL_COMPLETE = "✅ Kəşfiyyat analizi tamamlandı."
INTEL_GRAPH_STATS = "📊 Qraf: {nodes} node | {edges} edge | Etibar: {confidence}%"
INTEL_FALSE_POSITIVE = "🚫 Yanlış müsbət aşkarlandı və süzüldü: {value}"
INTEL_CLUSTER_FOUND = "🔗 Yeni klaster aşkarlandı: {count} əlaqəli node"
INTEL_MERGE_NODES = "🔗 Oxşar node-lar birləşdirildi: {value}"
INTEL_ORPHAN_NODE = "⚠  Yetim node aşkarlandı: {value}"
INTEL_ORPHAN_REMOVED = "🗑  Yetim node silindi: {value}"
INTEL_WEIGHT_UPDATED = "📊 Kənar çəkisi yeniləndi: {edge} → {weight}"
INTEL_CYCLE_DETECTED = "🔄 Dövri əlaqə aşkarlandı: {path}"
INTEL_ENRICHING = "🔄 Node zənginləşdirilir: {value}"
INTEL_ENRICHED = "✅ Node zənginləşdirildi: {value} (+{count} atribut)"
INTEL_SNAPSHOT = "📸 Qraf snapshot-ı saxlanıldı: {path}"
INTEL_ROLLBACK = "⏪ Qraf əvvəlki vəziyyətə qaytarıldı."
INTEL_TIMELINE = "📅 Zaman xətti yeniləndi: {count} hadisə"
INTEL_PATTERN = "🧩 Davranış nümunəsi aşkarlandı: {pattern}"
INTEL_CORRELATION = "🔗 Korrelyasiya tapıldı: {a} ↔ {b} (güc: {strength}%)"
INTEL_DEAD_END = "🚧 Bu yolda nəticə tapılmadı. Geri dönülür."
INTEL_RECURSIVE_START = "🔄 Rekursiv axtarış başladılır (dərinlik: {depth})..."
INTEL_RECURSIVE_END = "✅ Rekursiv axtarış tamamlandı."

# ═══════════════════════════════════════════════════════════
#  SESSION MANAGEMENT
# ═══════════════════════════════════════════════════════════

SESSION_STARTED = "📅 Sessiya başladı: {session_id}"
SESSION_RESUMED = "📅 Sessiya davam etdirilir: {session_id}"
SESSION_DURATION = "⏱  Sessiya müddəti: {duration}"
SESSION_TIMEOUT = "⏰ Sessiya vaxtı bitdi! Avtomatik dayandırma."
SESSION_ENDING = "🔒 Sessiya bağlanır..."
SESSION_ENDED = "✅ Sessiya uğurla bağlandı."
SESSION_SANDBOX_CLEANED = "🧹 Sandbox təmizləndi."
SESSION_SANDBOX_ERROR = "❌ Sandbox təmizlənə bilmədi: {error}"
SESSION_SAVED = "💾 Sessiya məlumatları saxlanıldı: {path}"
SESSION_SAVE_FAILED = "❌ Sessiya saxlanıla bilmədi: {error}"
SESSION_LOADED = "📂 Sessiya yükləndi: {session_id}"
SESSION_LOAD_FAILED = "❌ Sessiya yüklənə bilmədi: {error}"
SESSION_NOT_FOUND = "❌ Sessiya tapılmadı: {session_id}"
SESSION_LIST = "📋 Mövcud sessiyalar:"
SESSION_NO_SESSIONS = "📋 Heç bir sessiya tapılmadı."
SESSION_AUTO_SAVE = "💾 Avtomatik saxlama... ({interval} saniyə)"
SESSION_RECOVERY = "🔄 Son sessiya bərpa edilir..."
SESSION_RECOVERY_FAILED = "❌ Sessiya bərpa edilə bilmədi."

# ═══════════════════════════════════════════════════════════
#  TARGET INPUT
# ═══════════════════════════════════════════════════════════

INPUT_HEADER = "🎯 Hədəf Məlumatları"
INPUT_FIRST_NAME = "Ad: "
INPUT_LAST_NAME = "Soyad: "
INPUT_MIDDLE_NAME = "Ata adı (əgər varsa): "
INPUT_USERNAME = "İstifadəçi adı (əgər varsa): "
INPUT_EMAIL = "E-poçt (əgər varsa): "
INPUT_PHONE = "Telefon (əgər varsa): "
INPUT_EMPLOYER = "İş yeri (əgər varsa): "
INPUT_UNIVERSITY = "Universitet (əgər varsa): "
INPUT_CITY = "Şəhər: "
INPUT_COUNTRY = "Ölkə [Azərbaycan]: "
INPUT_EXTRA = "Əlavə məlumat (əgər varsa): "
INPUT_CONFIRM = "[?] Bu məlumatlar düzgündür? Axtarışa başlansın? (B/X): "
INPUT_EMPTY_WARNING = "⚠  Ən azı ad və soyad daxil edilməlidir."
INPUT_INVALID_EMAIL = "⚠  E-poçt formatı düzgün deyil: {email}"
INPUT_INVALID_PHONE = "⚠  Telefon formatı düzgün deyil: {phone}"
INPUT_FIELD_TOO_LONG = "⚠  Sahə çox uzundur (max {max} simvol): {field}"
INPUT_SOCIAL_MEDIA = "Sosial media profili (əgər varsa): "
INPUT_DOB = "Doğum tarixi (əgər varsa, GG.AA.İİİİ): "
INPUT_ALIAS = "Ləqəb / alternativ ad (əgər varsa): "
INPUT_PHOTO_PATH = "Şəkil yolu (əgər varsa): "
INPUT_NOTES = "Qeydlər: "
INPUT_EDITING = "📝 Hədəf məlumatları redaktə edilir..."
INPUT_UPDATED = "✅ Hədəf məlumatları yeniləndi."

# ═══════════════════════════════════════════════════════════
#  REPORTS
# ═══════════════════════════════════════════════════════════

REPORT_GENERATING = "📊 Hesabat hazırlanır..."
REPORT_SAVED = "✅ Hesabat saxlanıldı: {path}"
REPORT_SAVE_FAILED = "❌ Hesabat saxlanıla bilmədi: {error}"
REPORT_TITLE = "KƏŞFİYYAT HESABATI"
REPORT_SUMMARY = "Xülasə"
REPORT_PROFILE = "Hədəf Profili"
REPORT_FOOTPRINTS = "Rəqəmsal İzlər"
REPORT_DOCUMENTS = "Sənəd Tapıntıları"
REPORT_GRAPH = "Əlaqə Qrafı"
REPORT_CONFIDENCE = "Etibar Qiymətləndirməsi"
REPORT_RAW_DATA = "Xam Məlumatlar"
REPORT_GENERATED_AT = "Hesabat tarixi: {date}"
REPORT_SESSION_ID = "Sessiya: {session_id}"
REPORT_CLASSIFICATION = "Təsnifat: {level}"
REPORT_CLASSIFICATION_PUBLIC = "AÇIQ"
REPORT_CLASSIFICATION_INTERNAL = "DAXİLİ"
REPORT_CLASSIFICATION_CONFIDENTIAL = "MƏXFİ"
REPORT_TOC = "Mündəricat"
REPORT_APPENDIX = "Əlavələr"
REPORT_METHODOLOGY = "Metodologiya"
REPORT_TIMELINE = "Zaman Xətti"
REPORT_SOURCES = "Mənbələr"
REPORT_SOURCE_COUNT = "İstifadə edilən mənbə sayı: {count}"
REPORT_TOTAL_QUERIES = "Ümumi sorğu sayı: {count}"
REPORT_TOTAL_DOCUMENTS = "Tapılan sənəd sayı: {count}"
REPORT_TOTAL_PIVOTS = "Pivot nöqtələri: {count}"
REPORT_EXPORTING_PDF = "📄 PDF formatında ixrac edilir..."
REPORT_EXPORTING_JSON = "📄 JSON formatında ixrac edilir..."
REPORT_EXPORTING_HTML = "📄 HTML formatında ixrac edilir..."
REPORT_EXPORTED = "✅ Hesabat ixrac edildi: {path}"
REPORT_EXPORT_FAILED = "❌ Hesabat ixrac edilə bilmədi: {error}"

# ═══════════════════════════════════════════════════════════
#  LOGGING
# ═══════════════════════════════════════════════════════════

LOG_FILE_CREATED = "📝 Jurnal faylı yaradıldı: {path}"
LOG_FILE_ERROR = "❌ Jurnal faylı yaradıla bilmədi: {error}"
LOG_LEVEL_SET = "📝 Jurnal səviyyəsi ayarlandı: {level}"
LOG_ROTATED = "🔄 Jurnal faylı rotasiya edildi."
LOG_ENTRY = "[{timestamp}] [{level}] {message}"
LOG_AUDIT = "📋 Audit qeydi: {action} — {details}"

# ═══════════════════════════════════════════════════════════
#  CONFIGURATION
# ═══════════════════════════════════════════════════════════

CONFIG_LOADED = "⚙  Konfiqurasiya yükləndi: {path}"
CONFIG_NOT_FOUND = "⚠  Konfiqurasiya faylı tapılmadı. Standart ayarlar istifadə edilir."
CONFIG_INVALID = "❌ Konfiqurasiya faylı düzgün deyil: {error}"
CONFIG_SAVED = "✅ Konfiqurasiya saxlanıldı: {path}"
CONFIG_SAVE_FAILED = "❌ Konfiqurasiya saxlanıla bilmədi: {error}"
CONFIG_RESET = "🔄 Konfiqurasiya standart vəziyyətə qaytarıldı."
CONFIG_KEY_MISSING = "⚠  Konfiqurasiya açarı tapılmadı: {key}"
CONFIG_VALUE_INVALID = "❌ Yanlış konfiqurasiya dəyəri: {key}={value}"

# ═══════════════════════════════════════════════════════════
#  NETWORK / CONNECTIVITY
# ═══════════════════════════════════════════════════════════

NET_NO_CONNECTION = "❌ İnternet bağlantısı yoxdur."
NET_CONNECTION_RESTORED = "✅ İnternet bağlantısı bərpa olundu."
NET_TIMEOUT = "⏰ Bağlantı vaxtı bitdi: {url}"
NET_SSL_ERROR = "🔒 SSL xətası: {url} — {error}"
NET_HTTP_ERROR = "❌ HTTP xətası ({code}): {url}"
NET_DNS_ERROR = "❌ DNS həll edilə bilmədi: {domain}"
NET_RETRY = "🔄 Yenidən cəhd: {attempt}/{max_attempts}"
NET_MAX_RETRIES = "❌ Maksimum cəhd sayına çatıldı: {url}"
NET_PROXY_ERROR = "❌ Proksi xətası: {proxy} — {error}"
NET_RATE_429 = "⚠  HTTP 429: Çox sayda sorğu. Geri çəkilir."
NET_FORBIDDEN_403 = "🚫 HTTP 403: Giriş qadağandır: {url}"
NET_NOT_FOUND_404 = "❌ HTTP 404: Tapılmadı: {url}"
NET_SERVER_ERROR_5XX = "❌ Server xətası ({code}): {url}"

# ═══════════════════════════════════════════════════════════
#  FILESYSTEM / SANDBOX
# ═══════════════════════════════════════════════════════════

FS_SANDBOX_CREATED = "📂 Sandbox qovluğu yaradıldı: {path}"
FS_SANDBOX_EXISTS = "📂 Sandbox qovluğu mövcuddur: {path}"
FS_SANDBOX_CLEANED = "🧹 Sandbox təmizləndi: {count} fayl silindi."
FS_SANDBOX_ERROR = "❌ Sandbox xətası: {error}"
FS_FILE_SAVED = "💾 Fayl saxlanıldı: {path}"
FS_FILE_DELETED = "🗑  Fayl silindi: {path}"
FS_FILE_NOT_FOUND = "❌ Fayl tapılmadı: {path}"
FS_DIR_CREATED = "📂 Qovluq yaradıldı: {path}"
FS_DIR_NOT_FOUND = "❌ Qovluq tapılmadı: {path}"
FS_DISK_SPACE = "💾 Disk sahəsi: {used}/{total} ({percent}%)"
FS_DISK_LOW = "⚠  Disk sahəsi azdır! Qalan: {remaining}"
FS_PERMISSION_ERROR = "❌ İcazə xətası: {path}"

# ═══════════════════════════════════════════════════════════
#  MENU / NAVIGATION
# ═══════════════════════════════════════════════════════════

MENU_MAIN = "ANA MENYU"
MENU_OPTION_NEW_SESSION = "Yeni sessiya başlat"
MENU_OPTION_RESUME_SESSION = "Mövcud sessiyanı davam etdir"
MENU_OPTION_VIEW_REPORTS = "Hesabatları göstər"
MENU_OPTION_SETTINGS = "Ayarlar"
MENU_OPTION_HELP = "Kömək"
MENU_OPTION_EXIT = "Çıxış"
MENU_CHOOSE = "Seçiminizi daxil edin: "
MENU_INVALID = "❌ Yanlış seçim. Yenidən cəhd edin."
MENU_BACK = "⬅  Geri"
MENU_SETTINGS_TITLE = "AYARLAR"
MENU_HELP_TITLE = "KÖMƏK"

# ═══════════════════════════════════════════════════════════
#  GENERAL / COMMON
# ═══════════════════════════════════════════════════════════

GENERAL_YES = "B"
GENERAL_NO = "X"
GENERAL_ERROR = "❌ Xəta: {error}"
GENERAL_WARNING = "⚠  Xəbərdarlıq: {message}"
GENERAL_INFO = "ℹ  {message}"
GENERAL_SUCCESS = "✅ {message}"
GENERAL_LOADING = "⏳ Yüklənir..."
GENERAL_PRESS_ENTER = "Davam etmək üçün Enter basın..."
GENERAL_EXIT = "Çıxış edilir. Sağ olun!"
GENERAL_INVALID_INPUT = "❌ Yanlış daxiletmə. Yenidən cəhd edin."
GENERAL_CANCELLED = "❌ Əməliyyat ləğv edildi."
GENERAL_CONFIRM = "[?] Əminsiniz? (B/X): "
GENERAL_PROCESSING = "⚙  İşlənir..."
GENERAL_DONE = "✅ Tamamlandı."
GENERAL_FAILED = "❌ Uğursuz oldu."
GENERAL_NOT_IMPLEMENTED = "⚠  Bu funksiya hələ hazır deyil."
GENERAL_DEPRECATED = "⚠  Bu funksiya köhnəlib. Əvəzini istifadə edin: {alternative}"
GENERAL_DEBUG = "🐛 Debug: {message}"
GENERAL_VERBOSE = "📢 {message}"
GENERAL_SEPARATOR = "─" * 60
GENERAL_DOUBLE_SEPARATOR = "═" * 60
GENERAL_ELAPSED = "⏱  Keçən vaxt: {duration}"
GENERAL_COUNT = "Sayı: {count}"
GENERAL_TOTAL = "Cəmi: {total}"
GENERAL_NONE = "Yoxdur"
GENERAL_UNKNOWN = "Naməlum"
GENERAL_NA = "—"
GENERAL_EMPTY = "(boş)"
GENERAL_RETRY = "🔄 Yenidən cəhd edilir..."
GENERAL_SKIP = "⏭  Keçilir..."
GENERAL_ABORT = "🛑 Dayandırılır..."
GENERAL_CLEANUP = "🧹 Təmizlik aparılır..."
GENERAL_READY = "✅ Hazırdır."
GENERAL_STANDBY = "⏸  Gözləmə rejimi."
GENERAL_INTERRUPTED = "⚠  Əməliyyat kəsildi."
GENERAL_PERMISSION_DENIED = "🚫 İcazə yoxdur."
GENERAL_FEATURE_LOCKED = "🔒 Bu funksiya kilidlənib."

# ═══════════════════════════════════════════════════════════
#  BANNER / ASCII ART
# ═══════════════════════════════════════════════════════════

BANNER_ART = r"""
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║     ██╗  ██╗ ██████╗ ███████╗███████╗                             ║
║     ██║ ██╔╝██╔════╝ ██╔════╝██╔════╝                             ║
║     █████╔╝ ████████╗███████╗█████╗                               ║
║     ██╔═██╗ ╚════██║╚════██║██╔══╝                                ║
║     ██║  ██╗██████╔╝███████║██║                                   ║
║     ╚═╝  ╚═╝╚═════╝ ╚══════╝╚═╝                                  ║
║                                                                   ║
║     Kibernetik Əlaqə və Şəbəkə Forensikası                      ║
║     Rəqəmsal İz Kəşfiyyat Sistemi                                ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""

BANNER_MINI = "══ KƏŞF ══ Kibernetik Əlaqə və Şəbəkə Forensikası ══"
