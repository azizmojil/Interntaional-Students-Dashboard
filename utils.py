import re
import pandas as pd

# Constant for undefined/unspecified values
UNDEFINED_AR = "غير محدد"

# Unified nationality mapping dictionary
# Keys are exact nationalities from the data file (including those with trailing spaces)
# Values contain both Arabic and English country names
NATIONALITY_MAPPING = {
    "أردني": {"country_ar": "الأردن", "country_en": "Jordan"},
    "ألماني": {"country_ar": "ألمانيا", "country_en": "Germany"},
    "أمريكي": {"country_ar": "الولايات المتحدة الأمريكية", "country_en": "United States"},
    "أوزبكستاني": {"country_ar": "أوزبكستان", "country_en": "Uzbekistan"},
    "أوغندي": {"country_ar": "أوغندا", "country_en": "Uganda"},
    "أوكراني": {"country_ar": "أوكرانيا", "country_en": "Ukraine"},
    "إماراتي": {"country_ar": "الإمارات العربية المتحدة", "country_en": "United Arab Emirates"},
    "اثيوبي": {"country_ar": "إثيوبيا", "country_en": "Ethiopia"},
    "اذربيجاني": {"country_ar": "أذربيجان", "country_en": "Azerbaijan"},
    "ارجنتيني": {"country_ar": "الأرجنتين", "country_en": "Argentina"},
    "اريتيري": {"country_ar": "إريتريا", "country_en": "Eritrea"},
    "استرالي": {"country_ar": "أستراليا", "country_en": "Australia"},
    "افغانستاني": {"country_ar": "أفغانستان", "country_en": "Afghanistan"},
    "الاتحاد الأوروبي ": {"country_ar": "الاتحاد الأوروبي", "country_en": "Europe"},
    "الباني": {"country_ar": "ألبانيا", "country_en": "Albania"},
    "الجبل الاسود": {"country_ar": "الجبل الأسود", "country_en": "Montenegro"},
    "الجنسية تحت الإجراء": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "القبائل النازح": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "القبائل النازحة": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "الكنغو": {"country_ar": "الكونغو", "country_en": "Congo"},
    "المملكة المتحدة والجزر الشمالي": {"country_ar": "المملكة المتحدة", "country_en": "United Kingdom"},
    "اليابان": {"country_ar": "اليابان", "country_en": "Japan"},
    "اندونيسي": {"country_ar": "إندونيسيا", "country_en": "Indonesia"},
    "ايراني": {"country_ar": "إيران", "country_en": "Iran"},
    "ايطالي": {"country_ar": "إيطاليا", "country_en": "Italy"},
    "باكستاني": {"country_ar": "باكستان", "country_en": "Pakistan"},
    "بحريني": {"country_ar": "البحرين", "country_en": "Bahrain"},
    "بدون": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "برتغالي": {"country_ar": "البرتغال", "country_en": "Portugal"},
    "بريطاني": {"country_ar": "المملكة المتحدة", "country_en": "United Kingdom"},
    "بلجيكي": {"country_ar": "بلجيكا", "country_en": "Belgium"},
    "بلغاري": {"country_ar": "بلغاريا", "country_en": "Bulgaria"},
    "بنغلاديشي": {"country_ar": "بنغلاديش", "country_en": "Bangladesh"},
    "بنيني": {"country_ar": "بنين", "country_en": "Benin"},
    "بوركيني": {"country_ar": "بوركينا فاسو", "country_en": "Burkina Faso"},
    "بوروندي ": {"country_ar": "بوروندي", "country_en": "Burundi"},
    "بوسني": {"country_ar": "البوسنة والهرسك", "country_en": "Bosnia and Herzegovina"},
    "بولندي": {"country_ar": "بولندا", "country_en": "Poland"},
    "بيلاروسي": {"country_ar": "بيلاروسيا", "country_en": "Belarus"},
    "تايلندي": {"country_ar": "تايلاند", "country_en": "Thailand"},
    "تركستاني": {"country_ar": "تركستان", "country_en": "Turkestan"},
    "تركمنستاني": {"country_ar": "تركمانستان", "country_en": "Turkmenistan"},
    "تركي": {"country_ar": "تركيا", "country_en": "Turkey"},
    "ترينيداد وتوباغو ": {"country_ar": "ترينيداد وتوباغو", "country_en": "Trinidad and Tobago"},
    "تشادي": {"country_ar": "تشاد", "country_en": "Chad"},
    "تنزاني": {"country_ar": "تنزانيا", "country_en": "Tanzania"},
    "توغوي": {"country_ar": "توغو", "country_en": "Togo"},
    "تونسي": {"country_ar": "تونس", "country_en": "Tunisia"},
    "ج أفريقيا الوسطى": {"country_ar": "جمهورية أفريقيا الوسطى", "country_en": "Central African Republic"},
    "جامايكي": {"country_ar": "جامايكا", "country_en": "Jamaica"},
    "جزائري": {"country_ar": "الجزائر", "country_en": "Algeria"},
    "جزر القمر ": {"country_ar": "جزر القمر", "country_en": "Comoros"},
    "جزر فيرجين البريطانية ": {"country_ar": "جزر فيرجن البريطانية", "country_en": "British Virgin Islands"},
    "جنوب افريقي": {"country_ar": "جنوب أفريقيا", "country_en": "South Africa"},
    "جورجي": {"country_ar": "جورجيا", "country_en": "Georgia"},
    "جيبوتي": {"country_ar": "جيبوتي", "country_en": "Djibouti"},
    "دانمركي": {"country_ar": "الدنمارك", "country_en": "Denmark"},
    "دومينيكي": {"country_ar": "جمهورية الدومينيكان", "country_en": "Dominican Republic"},
    "رواندي": {"country_ar": "رواندا", "country_en": "Rwanda"},
    "روسي": {"country_ar": "روسيا", "country_en": "Russia"},
    "زمبابوي ": {"country_ar": "زيمبابوي", "country_en": "Zimbabwe"},
    "سانت كيتس ونيفس ": {"country_ar": "سانت كيتس ونيفيس", "country_en": "Saint Kitts and Nevis"},
    "سري لانكي": {"country_ar": "سريلانكا", "country_en": "Sri Lanka"},
    "سعودي من جهة الأم": {"country_ar": "السعودية", "country_en": "Saudi Arabia"},
    "سنغافوري": {"country_ar": "سنغافورة", "country_en": "Singapore"},
    "سنغالي": {"country_ar": "السنغال", "country_en": "Senegal"},
    "سوداني": {"country_ar": "السودان", "country_en": "Sudan"},
    "سوري": {"country_ar": "سوريا", "country_en": "Syria"},
    "سويدي": {"country_ar": "السويد", "country_en": "Sweden"},
    "سويسري": {"country_ar": "سويسرا", "country_en": "Switzerland"},
    "سيراليوني": {"country_ar": "سيراليون", "country_en": "Sierra Leone"},
    "صربيا": {"country_ar": "صربيا", "country_en": "Serbia"},
    "صومالي": {"country_ar": "الصومال", "country_en": "Somalia"},
    "صيني": {"country_ar": "الصين", "country_en": "China"},
    "طاجكستان": {"country_ar": "طاجيكستان", "country_en": "Tajikistan"},
    "عاجي": {"country_ar": "ساحل العاج", "country_en": "Cote d'Ivoire"},
    "عراقي": {"country_ar": "العراق", "country_en": "Iraq"},
    "عماني": {"country_ar": "عُمان", "country_en": "Oman"},
    "غابوني": {"country_ar": "الغابون", "country_en": "Gabon"},
    "غامبي": {"country_ar": "غامبيا", "country_en": "Gambia"},
    "غاني": {"country_ar": "غانا", "country_en": "Ghana"},
    "غير سعودي": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "غيني": {"country_ar": "غينيا", "country_en": "Guinea"},
    "غينيا - بيساو ": {"country_ar": "غينيا بيساو", "country_en": "Guinea-Bissau"},
    "غينيا الاستوائية": {"country_ar": "غينيا الاستوائية", "country_en": "Equatorial Guinea"},
    "فرنسي": {"country_ar": "فرنسا", "country_en": "France"},
    "فلبيني": {"country_ar": "الفلبين", "country_en": "Philippines"},
    "فلسطيني": {"country_ar": "فلسطين", "country_en": "Palestine"},
    "فلسطينية بوثيقة مصري": {"country_ar": "فلسطين", "country_en": "Palestine"},
    "فنلندي": {"country_ar": "فنلندا", "country_en": "Finland"},
    "قبائل نازحة / الحليفه": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "قبائل نازحة / الكويت": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "قطري": {"country_ar": "قطر", "country_en": "Qatar"},
    "قيرغيزستان ": {"country_ar": "قيرغيزستان", "country_en": "Kyrgyzstan"},
    "كازاخستاني": {"country_ar": "كازاخستان", "country_en": "Kazakhstan"},
    "كاميروني": {"country_ar": "الكاميرون", "country_en": "Cameroon"},
    "كمبودي": {"country_ar": "كمبوديا", "country_en": "Cambodia"},
    "كندي": {"country_ar": "كندا", "country_en": "Canada"},
    "كوري": {"country_ar": "كوريا", "country_en": "South Korea"},
    "كوسوفا": {"country_ar": "كوسوفو", "country_en": "Kosovo"},
    "كونغوليا": {"country_ar": "جمهورية الكونغو الديمقراطية", "country_en": "Democratic Republic of the Congo"},
    "كويتي": {"country_ar": "الكويت", "country_en": "Kuwait"},
    "كيني": {"country_ar": "كينيا", "country_en": "Kenya"},
    "لبناني": {"country_ar": "لبنان", "country_en": "Lebanon"},
    "ليبي": {"country_ar": "ليبيا", "country_en": "Libya"},
    "ليبيري": {"country_ar": "ليبيريا", "country_en": "Liberia"},
    "مالديفي": {"country_ar": "المالديف", "country_en": "Maldives"},
    "مالطي": {"country_ar": "مالطا", "country_en": "Malta"},
    "مالي": {"country_ar": "مالي", "country_en": "Mali"},
    "ماليزي": {"country_ar": "ماليزيا", "country_en": "Malaysia"},
    "مجري": {"country_ar": "المجر", "country_en": "Hungary"},
    "مدغشقري": {"country_ar": "مدغشقر", "country_en": "Madagascar"},
    "مصري": {"country_ar": "مصر", "country_en": "Egypt"},
    "مغربي": {"country_ar": "المغرب", "country_en": "Morocco"},
    "مقدوني": {"country_ar": "مقدونيا الشمالية", "country_en": "North Macedonia"},
    "مقيم": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "مقيم / نازح": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "مقيم بلوشي": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "منغولي": {"country_ar": "منغوليا", "country_en": "Mongolia"},
    "موريتاني": {"country_ar": "موريتانيا", "country_en": "Mauritania"},
    "موزامبيقي": {"country_ar": "موزمبيق", "country_en": "Mozambique"},
    "ميانمار/جواز باكستاني": {"country_ar": "ميانمار", "country_en": "Myanmar"},
    "ميانماري": {"country_ar": "ميانمار", "country_en": "Myanmar"},
    "نازح": {"country_ar": "غير محدد", "country_en": "Undefined"},
    "نرويجي": {"country_ar": "النرويج", "country_en": "Norway"},
    "نمساوي": {"country_ar": "النمسا", "country_en": "Austria"},
    "نيبالي": {"country_ar": "نيبال", "country_en": "Nepal"},
    "نيجري": {"country_ar": "النيجر", "country_en": "Niger"},
    "نيجيري": {"country_ar": "نيجيريا", "country_en": "Nigeria"},
    "نيوزيلندي": {"country_ar": "نيوزيلندا", "country_en": "New Zealand"},
    "هندي": {"country_ar": "الهند", "country_en": "India"},
    "هولندي": {"country_ar": "هولندا", "country_en": "Netherlands"},
    "يمني": {"country_ar": "اليمن", "country_en": "Yemen"},
    "يوغوسلافيا": {"country_ar": "يوغوسلافيا", "country_en": "Yugoslavia"},
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

# Build ARABIC_TO_ENGLISH for backward compatibility
ARABIC_TO_ENGLISH = {}
for mapping in NATIONALITY_MAPPING.values():
    country_ar = mapping["country_ar"]
    country_en = mapping["country_en"]
    if country_ar not in ARABIC_TO_ENGLISH and country_ar != UNDEFINED_AR:
        ARABIC_TO_ENGLISH[country_ar] = country_en

COUNTRY_TO_CONTINENT = {
    "غير محدد": "غير محدد",
    "الأردن": "آسيا",
    "ألمانيا": "أوروبا",
    "الولايات المتحدة الأمريكية": "أمريكا الشمالية",
    "أوزبكستان": "آسيا",
    "أوغندا": "أفريقيا",
    "أوكرانيا": "أوروبا",
    "الإمارات العربية المتحدة": "آسيا",
    "إثيوبيا": "أفريقيا",
    "أذربيجان": "آسيا",
    "الأرجنتين": "أمريكا الجنوبية",
    "إريتريا": "أفريقيا",
    "أستراليا": "أستراليا",
    "أفغانستان": "آسيا",
    "الاتحاد الأوروبي": "أوروبا",
    "ألبانيا": "أوروبا",
    "الجبل الأسود": "أوروبا",
    "الكونغو": "أفريقيا",
    "المملكة المتحدة": "أوروبا",
    "اليابان": "آسيا",
    "إندونيسيا": "آسيا",
    "إيران": "آسيا",
    "إيطاليا": "أوروبا",
    "باكستان": "آسيا",
    "البحرين": "آسيا",
    "البرتغال": "أوروبا",
    "بلجيكا": "أوروبا",
    "بلغاريا": "أوروبا",
    "بنغلاديش": "آسيا",
    "بنين": "أفريقيا",
    "بوركينا فاسو": "أفريقيا",
    "بوروندي": "أفريقيا",
    "البوسنة والهرسك": "أوروبا",
    "بولندا": "أوروبا",
    "بيلاروسيا": "أوروبا",
    "تايلاند": "آسيا",
    "تركستان": "آسيا",
    "تركمانستان": "آسيا",
    "تركيا": "آسيا",
    "ترينيداد وتوباغو": "أمريكا الشمالية",
    "تشاد": "أفريقيا",
    "تنزانيا": "أفريقيا",
    "توغو": "أفريقيا",
    "تونس": "أفريقيا",
    "جمهورية أفريقيا الوسطى": "أفريقيا",
    "جامايكا": "أمريكا الشمالية",
    "الجزائر": "أفريقيا",
    "جزر القمر": "أفريقيا",
    "جزر فيرجن البريطانية": "أمريكا الشمالية",
    "جنوب أفريقيا": "أفريقيا",
    "جورجيا": "آسيا",
    "جيبوتي": "أفريقيا",
    "الدنمارك": "أوروبا",
    "جمهورية الدومينيكان": "أمريكا الشمالية",
    "رواندا": "أفريقيا",
    "روسيا": "أوروبا",
    "زيمبابوي": "أفريقيا",
    "سانت كيتس ونيفيس": "أمريكا الشمالية",
    "سريلانكا": "آسيا",
    "السعودية": "آسيا",
    "سنغافورة": "آسيا",
    "السنغال": "أفريقيا",
    "السودان": "أفريقيا",
    "سوريا": "آسيا",
    "السويد": "أوروبا",
    "سويسرا": "أوروبا",
    "سيراليون": "أفريقيا",
    "صربيا": "أوروبا",
    "الصومال": "أفريقيا",
    "الصين": "آسيا",
    "طاجيكستان": "آسيا",
    "ساحل العاج": "أفريقيا",
    "العراق": "آسيا",
    "عُمان": "آسيا",
    "مصر": "أفريقيا",
    "الغابون": "أفريقيا",
    "غامبيا": "أفريقيا",
    "غانا": "أفريقيا",
    "غينيا": "أفريقيا",
    "غينيا بيساو": "أفريقيا",
    "غينيا الاستوائية": "أفريقيا",
    "فرنسا": "أوروبا",
    "الفلبين": "آسيا",
    "فلسطين": "آسيا",
    "فنلندا": "أوروبا",
    "قطر": "آسيا",
    "قيرغيزستان": "آسيا",
    "كازاخستان": "آسيا",
    "الكاميرون": "أفريقيا",
    "كمبوديا": "آسيا",
    "كندا": "أمريكا الشمالية",
    "كوريا": "آسيا",
    "كوسوفو": "أوروبا",
    "جمهورية الكونغو الديمقراطية": "أفريقيا",
    "الكويت": "آسيا",
    "كينيا": "أفريقيا",
    "لبنان": "آسيا",
    "ليبيا": "أفريقيا",
    "ليبيريا": "أفريقيا",
    "المالديف": "آسيا",
    "مالطا": "أوروبا",
    "مالي": "أفريقيا",
    "ماليزيا": "آسيا",
    "المجر": "أوروبا",
    "مدغشقر": "أفريقيا",
    "المغرب": "أفريقيا",
    "مقدونيا الشمالية": "أوروبا",
    "منغوليا": "آسيا",
    "موريتانيا": "أفريقيا",
    "موزمبيق": "أفريقيا",
    "ميانمار": "آسيا",
    "النرويج": "أوروبا",
    "النمسا": "أوروبا",
    "نيبال": "آسيا",
    "النيجر": "أفريقيا",
    "نيجيريا": "أفريقيا",
    "نيوزيلندا": "أستراليا",
    "الهند": "آسيا",
    "هولندا": "أوروبا",
    "اليمن": "آسيا",
    "يوغوسلافيا": "أوروبا"
}

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
    key = str(value)
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
