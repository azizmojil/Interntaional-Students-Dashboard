import re
import pandas as pd

# Constants for undefined/unspecified values
UNDEFINED_AR = "غير محدد"
UNDEFINED_EN = "Undefined"

# Unified nationality mapping dictionary
# Keys are exact nationalities from the data file (including those with trailing spaces)
# Values contain Arabic country name, English country name, and continent
NATIONALITY_MAPPING = {
    "أردني": {"country_ar": "الأردن", "country_en": "Jordan", "continent": "آسيا"},
    "ألماني": {"country_ar": "ألمانيا", "country_en": "Germany", "continent": "أوروبا"},
    "أمريكي": {"country_ar": "الولايات المتحدة الأمريكية", "country_en": "United States", "continent": "أمريكا الشمالية"},
    "أوزبكستاني": {"country_ar": "أوزبكستان", "country_en": "Uzbekistan", "continent": "آسيا"},
    "أوغندي": {"country_ar": "أوغندا", "country_en": "Uganda", "continent": "أفريقيا"},
    "أوكراني": {"country_ar": "أوكرانيا", "country_en": "Ukraine", "continent": "أوروبا"},
    "إماراتي": {"country_ar": "الإمارات العربية المتحدة", "country_en": "United Arab Emirates", "continent": "آسيا"},
    "اثيوبي": {"country_ar": "إثيوبيا", "country_en": "Ethiopia", "continent": "أفريقيا"},
    "اذربيجاني": {"country_ar": "أذربيجان", "country_en": "Azerbaijan", "continent": "آسيا"},
    "ارجنتيني": {"country_ar": "الأرجنتين", "country_en": "Argentina", "continent": "أمريكا الجنوبية"},
    "اريتيري": {"country_ar": "إريتريا", "country_en": "Eritrea", "continent": "أفريقيا"},
    "استرالي": {"country_ar": "أستراليا", "country_en": "Australia", "continent": "أستراليا"},
    "افغانستاني": {"country_ar": "أفغانستان", "country_en": "Afghanistan", "continent": "آسيا"},
    "الاتحاد الأوروبي ": {"country_ar": "الاتحاد الأوروبي", "country_en": "Europe", "continent": "أوروبا"},
    "الباني": {"country_ar": "ألبانيا", "country_en": "Albania", "continent": "أوروبا"},
    "الجبل الاسود": {"country_ar": "الجبل الأسود", "country_en": "Montenegro", "continent": "أوروبا"},
    "الجنسية تحت الإجراء": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "القبائل النازح": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "القبائل النازحة": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "الكنغو": {"country_ar": "الكونغو", "country_en": "Congo", "continent": "أفريقيا"},
    "المملكة المتحدة والجزر الشمالي": {"country_ar": "المملكة المتحدة", "country_en": "United Kingdom", "continent": "أوروبا"},
    "اليابان": {"country_ar": "اليابان", "country_en": "Japan", "continent": "آسيا"},
    "اندونيسي": {"country_ar": "إندونيسيا", "country_en": "Indonesia", "continent": "آسيا"},
    "ايراني": {"country_ar": "إيران", "country_en": "Iran", "continent": "آسيا"},
    "ايطالي": {"country_ar": "إيطاليا", "country_en": "Italy", "continent": "أوروبا"},
    "باكستاني": {"country_ar": "باكستان", "country_en": "Pakistan", "continent": "آسيا"},
    "بحريني": {"country_ar": "البحرين", "country_en": "Bahrain", "continent": "آسيا"},
    "بدون": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "برتغالي": {"country_ar": "البرتغال", "country_en": "Portugal", "continent": "أوروبا"},
    "بريطاني": {"country_ar": "المملكة المتحدة", "country_en": "United Kingdom", "continent": "أوروبا"},
    "بلجيكي": {"country_ar": "بلجيكا", "country_en": "Belgium", "continent": "أوروبا"},
    "بلغاري": {"country_ar": "بلغاريا", "country_en": "Bulgaria", "continent": "أوروبا"},
    "بنغلاديشي": {"country_ar": "بنغلاديش", "country_en": "Bangladesh", "continent": "آسيا"},
    "بنيني": {"country_ar": "بنين", "country_en": "Benin", "continent": "أفريقيا"},
    "بوركيني": {"country_ar": "بوركينا فاسو", "country_en": "Burkina Faso", "continent": "أفريقيا"},
    "بوروندي ": {"country_ar": "بوروندي", "country_en": "Burundi", "continent": "أفريقيا"},
    "بوسني": {"country_ar": "البوسنة والهرسك", "country_en": "Bosnia and Herzegovina", "continent": "أوروبا"},
    "بولندي": {"country_ar": "بولندا", "country_en": "Poland", "continent": "أوروبا"},
    "بيلاروسي": {"country_ar": "بيلاروسيا", "country_en": "Belarus", "continent": "أوروبا"},
    "تايلندي": {"country_ar": "تايلاند", "country_en": "Thailand", "continent": "آسيا"},
    "تركستاني": {"country_ar": "تركستان", "country_en": "Turkestan", "continent": "آسيا"},
    "تركمنستاني": {"country_ar": "تركمانستان", "country_en": "Turkmenistan", "continent": "آسيا"},
    "تركي": {"country_ar": "تركيا", "country_en": "Turkey", "continent": "آسيا"},
    "ترينيداد وتوباغو ": {"country_ar": "ترينيداد وتوباغو", "country_en": "Trinidad and Tobago", "continent": "أمريكا الشمالية"},
    "تشادي": {"country_ar": "تشاد", "country_en": "Chad", "continent": "أفريقيا"},
    "تنزاني": {"country_ar": "تنزانيا", "country_en": "Tanzania", "continent": "أفريقيا"},
    "توغوي": {"country_ar": "توغو", "country_en": "Togo", "continent": "أفريقيا"},
    "تونسي": {"country_ar": "تونس", "country_en": "Tunisia", "continent": "أفريقيا"},
    "ج أفريقيا الوسطى": {"country_ar": "جمهورية أفريقيا الوسطى", "country_en": "Central African Republic", "continent": "أفريقيا"},
    "جامايكي": {"country_ar": "جامايكا", "country_en": "Jamaica", "continent": "أمريكا الشمالية"},
    "جزائري": {"country_ar": "الجزائر", "country_en": "Algeria", "continent": "أفريقيا"},
    "جزر القمر ": {"country_ar": "جزر القمر", "country_en": "Comoros", "continent": "أفريقيا"},
    "جزر فيرجين البريطانية ": {"country_ar": "جزر فيرجن البريطانية", "country_en": "British Virgin Islands", "continent": "أمريكا الشمالية"},
    "جنوب افريقي": {"country_ar": "جنوب أفريقيا", "country_en": "South Africa", "continent": "أفريقيا"},
    "جورجي": {"country_ar": "جورجيا", "country_en": "Georgia", "continent": "آسيا"},
    "جيبوتي": {"country_ar": "جيبوتي", "country_en": "Djibouti", "continent": "أفريقيا"},
    "دانمركي": {"country_ar": "الدنمارك", "country_en": "Denmark", "continent": "أوروبا"},
    "دومينيكي": {"country_ar": "جمهورية الدومينيكان", "country_en": "Dominican Republic", "continent": "أمريكا الشمالية"},
    "رواندي": {"country_ar": "رواندا", "country_en": "Rwanda", "continent": "أفريقيا"},
    "روسي": {"country_ar": "روسيا", "country_en": "Russia", "continent": "أوروبا"},
    "زمبابوي ": {"country_ar": "زيمبابوي", "country_en": "Zimbabwe", "continent": "أفريقيا"},
    "سانت كيتس ونيفس ": {"country_ar": "سانت كيتس ونيفيس", "country_en": "Saint Kitts and Nevis", "continent": "أمريكا الشمالية"},
    "سري لانكي": {"country_ar": "سريلانكا", "country_en": "Sri Lanka", "continent": "آسيا"},
    "سعودي من جهة الأم": {"country_ar": "السعودية", "country_en": "Saudi Arabia", "continent": "آسيا"},
    "سنغافوري": {"country_ar": "سنغافورة", "country_en": "Singapore", "continent": "آسيا"},
    "سنغالي": {"country_ar": "السنغال", "country_en": "Senegal", "continent": "أفريقيا"},
    "سوداني": {"country_ar": "السودان", "country_en": "Sudan", "continent": "أفريقيا"},
    "سوري": {"country_ar": "سوريا", "country_en": "Syria", "continent": "آسيا"},
    "سويدي": {"country_ar": "السويد", "country_en": "Sweden", "continent": "أوروبا"},
    "سويسري": {"country_ar": "سويسرا", "country_en": "Switzerland", "continent": "أوروبا"},
    "سيراليوني": {"country_ar": "سيراليون", "country_en": "Sierra Leone", "continent": "أفريقيا"},
    "صربيا": {"country_ar": "صربيا", "country_en": "Serbia", "continent": "أوروبا"},
    "صومالي": {"country_ar": "الصومال", "country_en": "Somalia", "continent": "أفريقيا"},
    "صيني": {"country_ar": "الصين", "country_en": "China", "continent": "آسيا"},
    "طاجكستان": {"country_ar": "طاجيكستان", "country_en": "Tajikistan", "continent": "آسيا"},
    "عاجي": {"country_ar": "ساحل العاج", "country_en": "Cote d'Ivoire", "continent": "أفريقيا"},
    "عراقي": {"country_ar": "العراق", "country_en": "Iraq", "continent": "آسيا"},
    "عماني": {"country_ar": "عُمان", "country_en": "Oman", "continent": "آسيا"},
    "غابوني": {"country_ar": "الغابون", "country_en": "Gabon", "continent": "أفريقيا"},
    "غامبي": {"country_ar": "غامبيا", "country_en": "Gambia", "continent": "أفريقيا"},
    "غاني": {"country_ar": "غانا", "country_en": "Ghana", "continent": "أفريقيا"},
    "غير سعودي": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "غيني": {"country_ar": "غينيا", "country_en": "Guinea", "continent": "أفريقيا"},
    "غينيا - بيساو ": {"country_ar": "غينيا بيساو", "country_en": "Guinea-Bissau", "continent": "أفريقيا"},
    "غينيا الاستوائية": {"country_ar": "غينيا الاستوائية", "country_en": "Equatorial Guinea", "continent": "أفريقيا"},
    "فرنسي": {"country_ar": "فرنسا", "country_en": "France", "continent": "أوروبا"},
    "فلبيني": {"country_ar": "الفلبين", "country_en": "Philippines", "continent": "آسيا"},
    "فلسطيني": {"country_ar": "فلسطين", "country_en": "Palestine", "continent": "آسيا"},
    "فلسطينية بوثيقة مصري": {"country_ar": "فلسطين", "country_en": "Palestine", "continent": "آسيا"},
    "فنلندي": {"country_ar": "فنلندا", "country_en": "Finland", "continent": "أوروبا"},
    "قبائل نازحة / الحليفه": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "قبائل نازحة / الكويت": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "قطري": {"country_ar": "قطر", "country_en": "Qatar", "continent": "آسيا"},
    "قيرغيزستان ": {"country_ar": "قيرغيزستان", "country_en": "Kyrgyzstan", "continent": "آسيا"},
    "كازاخستاني": {"country_ar": "كازاخستان", "country_en": "Kazakhstan", "continent": "آسيا"},
    "كاميروني": {"country_ar": "الكاميرون", "country_en": "Cameroon", "continent": "أفريقيا"},
    "كمبودي": {"country_ar": "كمبوديا", "country_en": "Cambodia", "continent": "آسيا"},
    "كندي": {"country_ar": "كندا", "country_en": "Canada", "continent": "أمريكا الشمالية"},
    "كوري": {"country_ar": "كوريا", "country_en": "South Korea", "continent": "آسيا"},
    "كوسوفا": {"country_ar": "كوسوفو", "country_en": "Kosovo", "continent": "أوروبا"},
    "كونغوليا": {"country_ar": "جمهورية الكونغو الديمقراطية", "country_en": "Democratic Republic of the Congo", "continent": "أفريقيا"},
    "كويتي": {"country_ar": "الكويت", "country_en": "Kuwait", "continent": "آسيا"},
    "كيني": {"country_ar": "كينيا", "country_en": "Kenya", "continent": "أفريقيا"},
    "لبناني": {"country_ar": "لبنان", "country_en": "Lebanon", "continent": "آسيا"},
    "ليبي": {"country_ar": "ليبيا", "country_en": "Libya", "continent": "أفريقيا"},
    "ليبيري": {"country_ar": "ليبيريا", "country_en": "Liberia", "continent": "أفريقيا"},
    "مالديفي": {"country_ar": "المالديف", "country_en": "Maldives", "continent": "آسيا"},
    "مالطي": {"country_ar": "مالطا", "country_en": "Malta", "continent": "أوروبا"},
    "مالي": {"country_ar": "مالي", "country_en": "Mali", "continent": "أفريقيا"},
    "ماليزي": {"country_ar": "ماليزيا", "country_en": "Malaysia", "continent": "آسيا"},
    "مجري": {"country_ar": "المجر", "country_en": "Hungary", "continent": "أوروبا"},
    "مدغشقري": {"country_ar": "مدغشقر", "country_en": "Madagascar", "continent": "أفريقيا"},
    "مصري": {"country_ar": "مصر", "country_en": "Egypt", "continent": "أفريقيا"},
    "مغربي": {"country_ar": "المغرب", "country_en": "Morocco", "continent": "أفريقيا"},
    "مقدوني": {"country_ar": "مقدونيا الشمالية", "country_en": "North Macedonia", "continent": "أوروبا"},
    "مقيم": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "مقيم / نازح": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "مقيم بلوشي": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "منغولي": {"country_ar": "منغوليا", "country_en": "Mongolia", "continent": "آسيا"},
    "موريتاني": {"country_ar": "موريتانيا", "country_en": "Mauritania", "continent": "أفريقيا"},
    "موزامبيقي": {"country_ar": "موزمبيق", "country_en": "Mozambique", "continent": "أفريقيا"},
    "ميانمار/جواز باكستاني": {"country_ar": "ميانمار", "country_en": "Myanmar", "continent": "آسيا"},
    "ميانماري": {"country_ar": "ميانمار", "country_en": "Myanmar", "continent": "آسيا"},
    "نازح": {"country_ar": "غير محدد", "country_en": "Undefined", "continent": "غير محدد"},
    "نرويجي": {"country_ar": "النرويج", "country_en": "Norway", "continent": "أوروبا"},
    "نمساوي": {"country_ar": "النمسا", "country_en": "Austria", "continent": "أوروبا"},
    "نيبالي": {"country_ar": "نيبال", "country_en": "Nepal", "continent": "آسيا"},
    "نيجري": {"country_ar": "النيجر", "country_en": "Niger", "continent": "أفريقيا"},
    "نيجيري": {"country_ar": "نيجيريا", "country_en": "Nigeria", "continent": "أفريقيا"},
    "نيوزيلندي": {"country_ar": "نيوزيلندا", "country_en": "New Zealand", "continent": "أستراليا"},
    "هندي": {"country_ar": "الهند", "country_en": "India", "continent": "آسيا"},
    "هولندي": {"country_ar": "هولندا", "country_en": "Netherlands", "continent": "أوروبا"},
    "يمني": {"country_ar": "اليمن", "country_en": "Yemen", "continent": "آسيا"},
    "يوغوسلافيا": {"country_ar": "يوغوسلافيا", "country_en": "Yugoslavia", "continent": "أوروبا"},
}

# Helper function to get Arabic country name from nationality
def _get_country_ar(nationality: str) -> str:
    """Get Arabic country name from nationality, handling whitespace variations."""
    # First try exact match
    if nationality in NATIONALITY_MAPPING:
        return NATIONALITY_MAPPING[nationality]["country_ar"]
    # Then try stripped version
    stripped = nationality.strip()
    if stripped in NATIONALITY_MAPPING:
        return NATIONALITY_MAPPING[stripped]["country_ar"]
    # Try to find a matching key that when stripped matches
    for key, value in NATIONALITY_MAPPING.items():
        if key.strip() == stripped:
            return value["country_ar"]
    return stripped if stripped else UNDEFINED_AR

# Helper function to get English country name from Arabic country name
def _get_country_en(country_ar: str) -> str | None:
    """Get English country name from Arabic country name.
    
    Note: This is an internal helper used for building ARABIC_TO_ENGLISH.
    Returns None if the country is not found in the mapping.
    """
    for mapping in NATIONALITY_MAPPING.values():
        if mapping["country_ar"] == country_ar:
            return mapping["country_en"]
    return None

# Helper function to get continent from nationality
def _get_continent(nationality: str) -> str:
    """Get continent from nationality, handling whitespace variations."""
    # First try exact match
    if nationality in NATIONALITY_MAPPING:
        return NATIONALITY_MAPPING[nationality]["continent"]
    # Then try stripped version
    stripped = nationality.strip()
    if stripped in NATIONALITY_MAPPING:
        return NATIONALITY_MAPPING[stripped]["continent"]
    # Try to find a matching key that when stripped matches
    for key, value in NATIONALITY_MAPPING.items():
        if key.strip() == stripped:
            return value["continent"]
    return UNDEFINED_AR

# Build ARABIC_TO_ENGLISH for backward compatibility
ARABIC_TO_ENGLISH = {}
for mapping in NATIONALITY_MAPPING.values():
    country_ar = mapping["country_ar"]
    country_en = mapping["country_en"]
    if country_ar not in ARABIC_TO_ENGLISH and country_ar != UNDEFINED_AR:
        ARABIC_TO_ENGLISH[country_ar] = country_en

# Build ENGLISH_TO_ARABIC reverse mapping (for accepting English country names in CSV uploads)
ENGLISH_TO_ARABIC = {}
for mapping in NATIONALITY_MAPPING.values():
    country_ar = mapping["country_ar"]
    country_en = mapping["country_en"]
    if country_en not in ENGLISH_TO_ARABIC and country_ar != UNDEFINED_AR and country_en != UNDEFINED_EN:
        ENGLISH_TO_ARABIC[country_en] = country_ar

# Build COUNTRY_TO_CONTINENT from NATIONALITY_MAPPING for backward compatibility
COUNTRY_TO_CONTINENT = {UNDEFINED_AR: UNDEFINED_AR}
for mapping in NATIONALITY_MAPPING.values():
    country_ar = mapping["country_ar"]
    continent = mapping["continent"]
    if country_ar not in COUNTRY_TO_CONTINENT:
        COUNTRY_TO_CONTINENT[country_ar] = continent

STATUS_ACTIVE_KEYWORDS = [
    "متابع",
    "مؤهل",
    "مكتمل",
    "زائر",
    "مؤجل"
]

STATUS_GRAD_KEYWORDS = [
    "متخرج",
    "خريج"
]


def map_country(value: str) -> str:
    if pd.isna(value):
        return UNDEFINED_AR
    key = str(value).strip()
    # First try English country name mapping
    if key in ENGLISH_TO_ARABIC:
        return ENGLISH_TO_ARABIC[key]
    # Then try Arabic nationality to country mapping
    return _get_country_ar(key)

def map_continent(value: str) -> str:
    if pd.isna(value):
        return UNDEFINED_AR
    key = str(value).strip()
    return COUNTRY_TO_CONTINENT.get(key, UNDEFINED_AR)

def categorize_status(value: str) -> str:
    if pd.isna(value):
        return UNDEFINED_AR
    text = str(value)
    if any(keyword in text for keyword in STATUS_GRAD_KEYWORDS):
        return "متخرج"
    if any(keyword in text for keyword in STATUS_ACTIVE_KEYWORDS):
        return "نشط"
    return "غير نشط"


# Semester to Hijri month mapping for date formatting
SEMESTER_MONTH_MAPPING = {
    'الأول': 'بداية محرم',      # First semester
    'الثاني': 'بداية جمادى الأولى',  # Second semester
    'الثالث': 'بداية رمضان',     # Third semester (summer)
    'التكميلي': 'نهاية شوال',    # Supplementary semester
}


def parse_hijri_year(term_value) -> int | None:
    """Extract Hijri year from term value (returns Hijri year directly)."""
    if pd.isna(term_value):
        return None
    numbers = re.findall(r'\d{3,4}', str(term_value))
    if not numbers:
        return None
    try:
        hijri_year = int(numbers[0])
        return hijri_year  # Return Hijri year directly without conversion
    except ValueError:
        return None


def format_hijri_date(term_value) -> str | None:
    """Format term value as a Hijri date description with approximate date.
    
    Maps semesters to approximate Hijri months:
    - First semester (الأول): Beginning of Muharram (بداية محرم)
    - Second semester (الثاني): Beginning of Jumada al-Awwal (بداية جمادى الأولى)
    - Third semester (الثالث): Beginning of Ramadan (بداية رمضان)
    - Supplementary (التكميلي): End of Shawwal (نهاية شوال)
    """
    if pd.isna(term_value):
        return None
    
    term_str = str(term_value)
    numbers = re.findall(r'\d{3,4}', term_str)
    if not numbers:
        return None
    
    hijri_year = numbers[0]
    
    # Check for supplementary first (it contains 'الأول' substring)
    if 'التكميلي' in term_str:
        month_desc = SEMESTER_MONTH_MAPPING['التكميلي']
    # Then check for specific semester patterns
    elif 'الثالث' in term_str:
        month_desc = SEMESTER_MONTH_MAPPING['الثالث']
    elif 'الثاني' in term_str:
        month_desc = SEMESTER_MONTH_MAPPING['الثاني']
    elif 'الأول' in term_str:
        month_desc = SEMESTER_MONTH_MAPPING['الأول']
    else:
        # Default: just return the year
        return f"{hijri_year}هـ"
    
    return f"{month_desc} {hijri_year}هـ"


def map_gender(value: str) -> str:
    mapping = {"M": "ذكر", "F": "أنثى"}
    if pd.isna(value):
        return UNDEFINED_AR
    return mapping.get(str(value).strip(), UNDEFINED_AR)

# Constant for undefined trace name
_UNDEFINED_TRACE_NAME = 'undefined'

# Helper to format plots for RTL
def format_plot(fig):
    fig.update_layout(
        title="",  # Set to empty string instead of None to avoid "undefined"
        showlegend=False,
        font=dict(family="Inter, sans-serif"),
        margin=dict(t=20, l=50, r=50, b=20),
        # Fix hover label styling for RTL
        hoverlabel=dict(
            align="right",
            namelength=0  # Hide trace name in hover
        )
    )
    # Clean trace names to remove undefined values
    for trace in fig.data:
        if hasattr(trace, 'name') and (trace.name is None or trace.name == _UNDEFINED_TRACE_NAME):
            trace.name = ''
        # Clean hovertemplate if it contains undefined
        if hasattr(trace, 'hovertemplate') and trace.hovertemplate:
            if _UNDEFINED_TRACE_NAME in str(trace.hovertemplate):
                trace.hovertemplate = trace.hovertemplate.replace(_UNDEFINED_TRACE_NAME, '')
    return fig
