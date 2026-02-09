import re
import pandas as pd

# Mapping dictionaries
NATIONALITY_TO_COUNTRY = {
    "أردني": "الأردن",
    "ألماني": "ألمانيا",
    "أمريكي": "الولايات المتحدة الأمريكية",
    "أوزبكستاني": "أوزبكستان",
    "أوغندي": "أوغندا",
    "أوكراني": "أوكرانيا",
    "إماراتي": "الإمارات العربية المتحدة",
    "اثيوبي": "إثيوبيا",
    "اذربيجاني": "أذربيجان",
    "ارجنتيني": "الأرجنتين",
    "اريتيري": "إريتريا",
    "استرالي": "أستراليا",
    "افغانستاني": "أفغانستان",
    "الاتحاد الأوروبي": "الاتحاد الأوروبي",
    "الباني": "ألبانيا",
    "الجبل الاسود": "الجبل الأسود",
    "الجنسية تحت الإجراء": "غير محدد",
    "القبائل النازح": "غير محدد",
    "القبائل النازحة": "غير محدد",
    "الكنغو": "الكونغو",
    "المملكة المتحدة والجزر الشمالي": "المملكة المتحدة",
    "اليابان": "اليابان",
    "اندونيسي": "إندونيسيا",
    "ايراني": "إيران",
    "ايطالي": "إيطاليا",
    "باكستاني": "باكستان",
    "بحريني": "البحرين",
    "بدون": "غير محدد",
    "برتغالي": "البرتغال",
    "بريطاني": "المملكة المتحدة",
    "بلجيكي": "بلجيكا",
    "بلغاري": "بلغاريا",
    "بنغلاديشي": "بنغلاديش",
    "بنيني": "بنين",
    "بوركيني": "بوركينا فاسو",
    "بوروندي": "بوروندي",
    "بوسني": "البوسنة والهرسك",
    "بولندي": "بولندا",
    "بيلاروسي": "بيلاروسيا",
    "تايلندي": "تايلاند",
    "تركستاني": "تركستان",
    "تركمنستاني": "تركمانستان",
    "تركي": "تركيا",
    "ترينيداد وتوباغو": "ترينيداد وتوباغو",
    "تشادي": "تشاد",
    "تنزاني": "تنزانيا",
    "توغوي": "توغو",
    "تونسي": "تونس",
    "ج أفريقيا الوسطى": "جمهورية أفريقيا الوسطى",
    "جامايكي": "جامايكا",
    "جزائري": "الجزائر",
    "جزر القمر": "جزر القمر",
    "جزر فيرجين البريطانية": "جزر فيرجن البريطانية",
    "جنوب افريقي": "جنوب أفريقيا",
    "جورجي": "جورجيا",
    "جيبوتي": "جيبوتي",
    "دانمركي": "الدنمارك",
    "دومينيكي": "جمهورية الدومينيكان",
    "رواندي": "رواندا",
    "روسي": "روسيا",
    "زمبابوي": "زيمبابوي",
    "سانت كيتس ونيفس": "سانت كيتس ونيفيس",
    "سري لانكي": "سريلانكا",
    "سعودي من جهة الأم": "السعودية",
    "سنغافوري": "سنغافورة",
    "سنغالي": "السنغال",
    "سوداني": "السودان",
    "سوري": "سوريا",
    "سويدي": "السويد",
    "سويسري": "سويسرا",
    "سيراليوني": "سيراليون",
    "صربيا": "صربيا",
    "صومالي": "الصومال",
    "صيني": "الصين",
    "طاجكستان": "طاجيكستان",
    "عاجي": "ساحل العاج",
    "عراقي": "العراق",
    "عماني": "عُمان",
    "غابوني": "الغابون",
    "غامبي": "غامبيا",
    "غاني": "غانا",
    "غير سعودي": "غير محدد",
    "غيني": "غينيا",
    "غينيا - بيساو": "غينيا بيساو",
    "غينيا الاستوائية": "غينيا الاستوائية",
    "فرنسي": "فرنسا",
    "فلبيني": "الفلبين",
    "فلسطيني": "فلسطين",
    "فلسطينية بوثيقة مصري": "فلسطين",
    "فنلندي": "فنلندا",
    "قبائل نازحة / الحليفه": "غير محدد",
    "قبائل نازحة / الكويت": "غير محدد",
    "قطري": "قطر",
    "قيرغيزستان": "قيرغيزستان",
    "كازاخستاني": "كازاخستان",
    "كاميروني": "الكاميرون",
    "كمبودي": "كمبوديا",
    "كندي": "كندا",
    "كوري": "كوريا",
    "كوسوفا": "كوسوفو",
    "كونغوليا": "جمهورية الكونغو الديمقراطية",
    "كويتي": "الكويت",
    "كيني": "كينيا",
    "لبناني": "لبنان",
    "ليبي": "ليبيا",
    "ليبيري": "ليبيريا",
    "مالديفي": "المالديف",
    "مالطي": "مالطا",
    "مالي": "مالي",
    "ماليزي": "ماليزيا",
    "مجري": "المجر",
    "مدغشقري": "مدغضقر",
    "مصري": "مصر",
    "مغربي": "Morocco",
    "مقدوني": "مقدونيا الشمالية",
    "منغولي": "منغوليا",
    "موريتاني": "موريتانيا",
    "موزامبيقي": "موزمبيق",
    "ميانماري": "ميانمار",
    "ميانمار/جواز باكستاني": "ميانمار",
    "نرويجي": "النرويج",
    "نمساوي": "النمسا",
    "نيبالي": "نيبال",
    "نيجري": "النيجر",
    "نيجيري": "نيجيريا",
    "نيوزيلندي": "نيوزيلندا",
    "هندي": "الهند",
    "هولندا": "هولندا",
    "يمني": "اليمن",
    "يوغوسلافيا": "يوغوسلافيا"
}

ARABIC_TO_ENGLISH = {
    "الأردن": "Jordan",
    "ألمانيا": "Germany",
    "الولايات المتحدة الأمريكية": "United States",
    "أوزبكستان": "Uzbekistan",
    "أوغندا": "Uganda",
    "أوكرانيا": "Ukraine",
    "الإمارات العربية المتحدة": "United Arab Emirates",
    "إثيوبيا": "Ethiopia",
    "أذربيجان": "Azerbaijan",
    "الأرجنتين": "Argentina",
    "إريتريا": "Eritrea",
    "أستراليا": "Australia",
    "أفغانستان": "Afghanistan",
    "الاتحاد الأوروبي": "Europe",
    "ألبانيا": "Albania",
    "الجبل الأسود": "Montenegro",
    "الكونغو": "Congo",
    "المملكة المتحدة": "United Kingdom",
    "اليابان": "Japan",
    "إندونيسيا": "Indonesia",
    "إيران": "Iran",
    "إيطاليا": "Italy",
    "باكستان": "Pakistan",
    "البحرين": "Bahrain",
    "البرتغال": "Portugal",
    "بلجيكا": "Belgium",
    "بلغاريا": "Bulgaria",
    "بنغلاديش": "Bangladesh",
    "بنين": "Benin",
    "بوركينا فاسو": "Burkina Faso",
    "بوروندي": "Burundi",
    "البوسنة والهرسك": "Bosnia and Herzegovina",
    "بولندا": "Poland",
    "بيلاروسيا": "Belarus",
    "تايلاند": "Thailand",
    "تركستان": "Turkestan",
    "تركمانستان": "Turkmenistan",
    "تركيا": "Turkey",
    "ترينيداد وتوباغو": "Trinidad and Tobago",
    "تشاد": "Chad",
    "تنزانيا": "Tanzania",
    "توغو": "Togo",
    "تونس": "Tunisia",
    "جمهورية أفريقيا الوسطى": "Central African Republic",
    "جامايكا": "Jamaica",
    "الجزائر": "Algeria",
    "جزر القمر": "Comoros",
    "جزر فيرجن البريطانية": "British Virgin Islands",
    "جنوب أفريقيا": "South Africa",
    "جورجيا": "Georgia",
    "جيبوتي": "Djibouti",
    "الدنمارك": "Denmark",
    "جمهورية الدومينيكان": "Dominican Republic",
    "رواندا": "Rwanda",
    "روسيا": "Russia",
    "زيمبابوي": "Zimbabwe",
    "سانت كيتس ونيفيس": "Saint Kitts and Nevis",
    "سريلانكا": "Sri Lanka",
    "السعودية": "Saudi Arabia",
    "سنغافورة": "Singapore",
    "السنغال": "Senegal",
    "السودان": "Sudan",
    "سوريا": "Syria",
    "السويد": "Sweden",
    "سويسرا": "Switzerland",
    "سيراليون": "Sierra Leone",
    "صربيا": "Serbia",
    "الصومال": "Somalia",
    "الصين": "China",
    "طاجيكستان": "Tajikistan",
    "ساحل العاج": "Cote d'Ivoire",
    "العراق": "Iraq",
    "عُمان": "Oman",
    "الغابون": "Gabon",
    "غامبيا": "Gambia",
    "غانا": "Ghana",
    "غينيا": "Guinea",
    "غينيا بيساو": "Guinea-Bissau",
    "غينيا الاستوائية": "Equatorial Guinea",
    "فرنسا": "France",
    "الفلبين": "Philippines",
    "فلسطين": "Palestine",
    "فنلندا": "Finland",
    "قطر": "Qatar",
    "قيرغيزستان": "Kyrgyzstan",
    "كازاخستان": "Kazakhstan",
    "الكاميرون": "Cameroon",
    "كمبوديا": "Cambodia",
    "كندا": "Canada",
    "كوريا": "South Korea",
    "كوسوفو": "Kosovo",
    "جمهورية الكونغو الديمقراطية": "Democratic Republic of the Congo",
    "الكويت": "Kuwait",
    "كينيا": "Kenya",
    "لبنان": "Lebanon",
    "ليبيا": "Libya",
    "ليبيريا": "Liberia",
    "المالديف": "Maldives",
    "مالطا": "Malta",
    "مالي": "Mali",
    "ماليزيا": "Malaysia",
    "المجر": "Hungary",
    "مدغشقري": "Madagascar",
    "مصر": "Egypt",
    "المغرب": "Morocco",
    "مقدونيا الشمالية": "North Macedonia",
    "منغوليا": "Mongolia",
    "موريتانيا": "Mauritania",
    "موزمبيق": "Mozambique",
    "ميانمار": "Myanmar",
    "النرويج": "Norway",
    "النمسا": "Austria",
    "نيبال": "Nepal",
    "النيجر": "Niger",
    "نيجيريا": "Nigeria",
    "نيوزيلندا": "New Zealand",
    "الهند": "India",
    "هولندا": "Netherlands",
    "اليمن": "Yemen",
    "يوغوسلافيا": "Yugoslavia"
}

COUNTRY_TO_CONTINENT = {
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
        return "غير محدد"
    key = str(value).strip()
    return NATIONALITY_TO_COUNTRY.get(key, key if key else "غير محدد")

def map_continent(value: str) -> str:
    if pd.isna(value):
        return "غير محدد"
    key = str(value).strip()
    return COUNTRY_TO_CONTINENT.get(key, "غير محدد")

def categorize_status(value: str) -> str:
    if pd.isna(value):
        return "غير محدد"
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
        return "غير محدد"
    return mapping.get(str(value).strip(), "غير محدد")

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
