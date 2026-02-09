import re
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np

# Page configuration
st.set_page_config(
    page_title="لوحة معلومات الطلاب الدوليين",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling with RTL support
st.markdown("""
    <style>
    * {
        direction: rtl;
        text-align: right;
    }
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
    }
    .stMetric label {
        direction: rtl;
    }
    </style>
    """, unsafe_allow_html=True)

# Mapping dictionaries and helpers
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
    "مدغشقري": "مدغشقر",
    "مصري": "مصر",
    "مغربي": "المغرب",
    "مقدوني": "مقدونيا الشمالية",
    "مقيم": "غير محدد",
    "مقيم / نازح": "غير محدد",
    "مقيم بلوشي": "غير محدد",
    "منغولي": "منغوليا",
    "موريتاني": "موريتانيا",
    "موزامبيقي": "موزمبيق",
    "ميانمار/جواز باكستاني": "ميانمار",
    "ميانماري": "ميانمار",
    "نازح": "غير محدد",
    "نرويجي": "النرويج",
    "نمساوي": "النمسا",
    "نيبالي": "نيبال",
    "نيجري": "النيجر",
    "نيجيري": "نيجيريا",
    "نيوزيلندي": "نيوزيلندا",
    "هندي": "الهند",
    "هولندي": "هولندا",
    "يمني": "اليمن",
    "يوغوسلافيا": "يوغوسلافيا"
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


def categorize_status(value: str) -> str:
    if pd.isna(value):
        return "غير محدد"
    text = str(value)
    if any(keyword in text for keyword in STATUS_GRAD_KEYWORDS):
        return "متخرج"
    if any(keyword in text for keyword in STATUS_ACTIVE_KEYWORDS):
        return "نشط"
    if "NOT ACTIVE" in text.upper():
        return "غير نشط"
    if any(keyword in text for keyword in ["منسحب", "مفصول", "موقوف", "مطوي", "متوفى", "محول", "منقطع", "معتذر", "إنسحاب"]):
        return "غير نشط"
    return "غير نشط"


def parse_hijri_year(term_value) -> float | None:
    if pd.isna(term_value):
        return None
    numbers = re.findall(r'\d{3,4}', str(term_value))
    if not numbers:
        return None
    try:
        hijri_year = int(numbers[0])
        return hijri_year + 579  # تقريب تحويل هجري إلى ميلادي
    except ValueError:
        return None


def map_gender(value: str) -> str:
    mapping = {"M": "ذكر", "F": "أنثى", "N": "غير محدد"}
    if pd.isna(value):
        return "غير محدد"
    return mapping.get(str(value).strip(), "غير محدد")

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('data/data.xlsx')
        processed = pd.DataFrame({
            "student_id": df.get("STD_ID"),
            "name": df.get("STD_NAME"),
            "gender": df.get("GENDER").apply(map_gender),
            "country": df.get("CITZ_DESC").apply(map_country),
            "program": df.get("MAJR_DESC").fillna("غير محدد"),
            "college": df.get("COLL_DESC").fillna("غير محدد"),
            "status_detail": df.get("LAST_STST").fillna("غير محدد"),
            "funding": df.get("CELG_CODE").fillna("غير محدد"),
            "gpa": pd.to_numeric(df.get("STD_GPA"), errors="coerce"),
            "hours": pd.to_numeric(df.get("STD_HRS"), errors="coerce"),
            "term_admit": df.get("TERM_ADMIT"),
            "last_term": df.get("LAST_TERM"),
            "level": df.get("LEVL_DESC").fillna("غير محدد"),
            "email": df.get("EMAIL"),
            "mobile": df.get("MOBILE"),
        })

        processed["status"] = processed["status_detail"].apply(categorize_status)
        processed["admit_year"] = processed["term_admit"].apply(parse_hijri_year)
        processed["last_term_year"] = processed["last_term"].apply(parse_hijri_year)
        processed["timeline_year"] = processed["admit_year"].fillna(processed["last_term_year"])
        return processed
    except FileNotFoundError:
        st.error("❌ ملف البيانات غير موجود! يرجى التأكد من وجود 'data/data.xlsx'.")
        st.stop()
    except Exception as e:
        st.error(f"❌ خطأ في تحميل البيانات: {str(e)}")
        st.stop()

# Main app
def main():
    # Title
    st.title("🎓 لوحة معلومات الطلاب الدوليين")
    st.markdown("### تحليلات ذكاء الأعمال لبيانات الطلاب الدوليين")
    
    # Load data
    df = load_data()
    gpa_values = df['gpa'].dropna()
    gpa_min = float(gpa_values.min()) if not gpa_values.empty else 0.0
    gpa_max = float(gpa_values.max()) if not gpa_values.empty else 5.0
    if gpa_min == gpa_max:
        gpa_max = gpa_min + 1
    
    # Sidebar filters
    st.sidebar.header("📊 الفلاتر")
    
    # Country filter
    countries = ['الكل'] + sorted(df['country'].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("اختر الدولة", countries)
    
    # Program filter
    programs = ['الكل'] + sorted(df['program'].dropna().unique().tolist())
    selected_program = st.sidebar.selectbox("اختر البرنامج", programs)
    
    # Status filter
    status_options = ['الكل'] + sorted(df['status'].dropna().unique().tolist())
    selected_status = st.sidebar.selectbox("اختر الحالة", status_options)
    
    # Gender filter
    gender_options = ['الكل'] + sorted(df['gender'].dropna().unique().tolist())
    selected_gender = st.sidebar.selectbox("اختر الجنس", gender_options)
    
    # GPA range filter
    st.sidebar.markdown("**نطاق المعدل التراكمي**")
    gpa_range = st.sidebar.slider(
        "اختر نطاق المعدل التراكمي",
        min_value=gpa_min,
        max_value=gpa_max,
        value=(gpa_min, gpa_max),
        step=0.1
    )
    
    # Apply filters
    filtered_df = df.copy()
    if selected_country != 'الكل':
        filtered_df = filtered_df[filtered_df['country'] == selected_country]
    if selected_program != 'الكل':
        filtered_df = filtered_df[filtered_df['program'] == selected_program]
    if selected_status != 'الكل':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if selected_gender != 'الكل':
        filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
    gpa_for_filter = filtered_df['gpa'].fillna(gpa_min)
    filtered_df = filtered_df[(gpa_for_filter >= gpa_range[0]) & (gpa_for_filter <= gpa_range[1])]
    
    # Display metrics
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("إجمالي الطلاب", len(filtered_df))
    with col2:
        st.metric("الطلاب النشطون", len(filtered_df[filtered_df['status'] == 'نشط']))
    with col3:
        st.metric("الخريجون", len(filtered_df[filtered_df['status'] == 'متخرج']))
    with col4:
        st.metric("متوسط المعدل", f"{filtered_df['gpa'].mean():.2f}")
    with col5:
        st.metric("الدول", filtered_df['country'].nunique())
    
    st.markdown("---")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 نظرة عامة", "🌍 التحليل الجغرافي", "📊 الأداء الأكاديمي", "📋 جدول البيانات"])
    
    with tab1:
        # Overview tab
        col1, col2 = st.columns(2)
        
        with col1:
            # Students by Program
            st.subheader("الطلاب حسب البرنامج")
            program_counts = filtered_df['program'].value_counts().reset_index()
            program_counts.columns = ['program', 'count']
            fig_program = px.bar(
                program_counts,
                x='program',
                y='count',
                color='count',
                color_continuous_scale='Blues',
                labels={'count': 'عدد الطلاب', 'program': 'البرنامج'},
                title="التوزيع حسب البرنامج"
            )
            fig_program.update_layout(showlegend=False)
            st.plotly_chart(fig_program, use_container_width=True)
        
        with col2:
            # Students by Status
            st.subheader("الطلاب حسب الحالة")
            status_counts = filtered_df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            fig_status = px.pie(
                status_counts,
                values='count',
                names='status',
                title="التوزيع حسب الحالة",
                color_discrete_sequence=px.colors.qualitative.Set2
            )
            st.plotly_chart(fig_status, use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Gender Distribution
            st.subheader("التوزيع حسب الجنس")
            gender_counts = filtered_df['gender'].value_counts().reset_index()
            gender_counts.columns = ['gender', 'count']
            fig_gender = px.pie(
                gender_counts,
                values='count',
                names='gender',
                title="التوزيع حسب الجنس",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_gender, use_container_width=True)
        
        with col4:
            # Enrollment Trend
            st.subheader("اتجاه التسجيل")
            timeline_df = filtered_df.dropna(subset=['timeline_year']).copy()
            timeline_df['timeline_year'] = timeline_df['timeline_year'].astype(int)
            enrollment_by_date = timeline_df.groupby('timeline_year').size().reset_index(name='count')
            fig_trend = px.line(
                enrollment_by_date,
                x='timeline_year',
                y='count',
                markers=True,
                title="اتجاه التسجيل حسب السنة (تقريب ميلادي)",
                labels={'count': 'عدد الطلاب', 'timeline_year': 'السنة'}
            )
            fig_trend.update_traces(line_color='#636EFA', line_width=3)
            st.plotly_chart(fig_trend, use_container_width=True)
    
    with tab2:
        # Geographic Analysis tab
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Students by Country (Top 15)
            st.subheader("أفضل الدول")
            country_counts = filtered_df['country'].value_counts().head(15).reset_index()
            country_counts.columns = ['country', 'count']
            fig_country = px.bar(
                country_counts,
                x='count',
                y='country',
                orientation='h',
                color='count',
                color_continuous_scale='Viridis',
                labels={'count': 'عدد الطلاب', 'country': 'الدولة'},
                title="أفضل 15 دولة حسب عدد الطلاب"
            )
            st.plotly_chart(fig_country, use_container_width=True)
        
        with col2:
            # Country statistics
            st.subheader("إحصائيات الدول")
            country_stats = filtered_df.groupby('country').agg({
                'student_id': 'count',
                'gpa': 'mean'
            }).round(2).reset_index()
            country_stats.columns = ['الدولة', 'الطلاب', 'متوسط المعدل']
            country_stats = country_stats.sort_values('الطلاب', ascending=False).head(10)
            st.dataframe(country_stats, hide_index=True, use_container_width=True)
        
        # College Distribution
        st.subheader("أفضل الكليات")
        college_counts = filtered_df['college'].value_counts().head(10).reset_index()
        college_counts.columns = ['college', 'count']
        fig_university = px.bar(
            college_counts,
            x='college',
            y='count',
            color='count',
            color_continuous_scale='Sunset',
            labels={'count': 'عدد الطلاب', 'college': 'الكلية'},
            title="أفضل 10 كليات"
        )
        fig_university.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig_university, use_container_width=True)
    
    with tab3:
        # Academic Performance tab
        col1, col2 = st.columns(2)
        
        with col1:
            # GPA Distribution
            st.subheader("توزيع المعدل التراكمي")
            fig_gpa_hist = px.histogram(
                filtered_df,
                x='gpa',
                nbins=20,
                color_discrete_sequence=['#00CC96'],
                labels={'gpa': 'المعدل التراكمي', 'count': 'عدد الطلاب'},
                title="توزيع المعدل التراكمي"
            )
            st.plotly_chart(fig_gpa_hist, use_container_width=True)
        
        with col2:
            # Average GPA by Program
            st.subheader("متوسط المعدل حسب البرنامج")
            avg_gpa_program = filtered_df.groupby('program')['gpa'].mean().sort_values(ascending=False).reset_index()
            fig_gpa_program = px.bar(
                avg_gpa_program,
                x='program',
                y='gpa',
                color='gpa',
                color_continuous_scale='RdYlGn',
                labels={'gpa': 'متوسط المعدل', 'program': 'البرنامج'},
                title="متوسط المعدل حسب البرنامج"
            )
            fig_gpa_program.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_gpa_program, use_container_width=True)
        
        # Age Distribution
        st.subheader("توزيع الساعات المكتسبة")
        hours_df = filtered_df.dropna(subset=['hours'])
        if hours_df.empty:
            st.info("لا توجد بيانات ساعات لعرضها")
        else:
            fig_hours = px.box(
                hours_df,
                x='program',
                y='hours',
                color='program',
                labels={'hours': 'الساعات المكتسبة', 'program': 'البرنامج'},
                title="توزيع الساعات المكتسبة حسب البرنامج"
            )
            fig_hours.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig_hours, use_container_width=True)
        
        # GPA by Country (Top 10)
        st.subheader("متوسط المعدل حسب الدولة (أفضل 10)")
        avg_gpa_country = filtered_df.groupby('country')['gpa'].mean().sort_values(ascending=False).head(10).reset_index()
        fig_gpa_country = px.bar(
            avg_gpa_country,
            x='country',
            y='gpa',
            color='gpa',
            color_continuous_scale='Plasma',
            labels={'gpa': 'متوسط المعدل', 'country': 'الدولة'},
            title="أفضل 10 دول حسب متوسط المعدل"
        )
        st.plotly_chart(fig_gpa_country, use_container_width=True)
    
    with tab4:
        # Data Table tab
        st.subheader("بيانات الطلاب")
        
        # Search functionality
        search_term = st.text_input("🔍 البحث بالاسم أو الدولة أو الكلية أو التخصص", "")
        
        if search_term:
            mask = (
                filtered_df['name'].str.contains(search_term, case=False, na=False) |
                filtered_df['country'].str.contains(search_term, case=False, na=False) |
                filtered_df['college'].str.contains(search_term, case=False, na=False) |
                filtered_df['program'].str.contains(search_term, case=False, na=False)
            )
            display_df = filtered_df[mask]
        else:
            display_df = filtered_df

        columns_to_show = {
            "student_id": "الرقم الجامعي",
            "name": "الاسم",
            "country": "الدولة",
            "program": "التخصص",
            "college": "الكلية",
            "status": "الحالة المختصرة",
            "status_detail": "تفاصيل الحالة",
            "gpa": "المعدل التراكمي",
            "hours": "الساعات المكتسبة",
            "funding": "نوع المنحة",
            "term_admit": "فصل القبول (هجري)",
            "last_term": "آخر فصل (هجري)",
            "admit_year": "سنة القبول (ميلادي تقديري)",
            "last_term_year": "آخر فصل (ميلادي تقديري)",
            "email": "البريد الإلكتروني",
            "mobile": "الجوال"
        }
        display_df = display_df[list(columns_to_show.keys())].rename(columns=columns_to_show)
        
        # Display dataframe
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button
        csv = display_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 تحميل البيانات كملف CSV",
            data=csv,
            file_name=f"international_students_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )
        
        # Summary statistics
        st.subheader("الإحصائيات الموجزة")
        numeric_summary = display_df.select_dtypes(include=['number']).describe()
        st.dataframe(numeric_summary, use_container_width=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center'>
            <p>لوحة معلومات الطلاب الدوليين | مبني بواسطة Streamlit 🎓</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
