import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

# Load data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/students_data.csv')
        df['enrollment_date'] = pd.to_datetime(df['enrollment_date'])
        df['graduation_date'] = pd.to_datetime(df['graduation_date'])
        return df
    except FileNotFoundError:
        st.error("❌ ملف البيانات غير موجود! يرجى التأكد من وجود 'data/students_data.csv'.")
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
    
    # Sidebar filters
    st.sidebar.header("📊 الفلاتر")
    
    # Country filter
    countries = ['الكل'] + sorted(df['country'].unique().tolist())
    selected_country = st.sidebar.selectbox("اختر الدولة", countries)
    
    # Program filter
    programs = ['الكل'] + sorted(df['program'].unique().tolist())
    selected_program = st.sidebar.selectbox("اختر البرنامج", programs)
    
    # Status filter
    status_options = ['الكل'] + sorted(df['status'].unique().tolist())
    selected_status = st.sidebar.selectbox("اختر الحالة", status_options)
    
    # Gender filter
    gender_options = ['الكل'] + sorted(df['gender'].unique().tolist())
    selected_gender = st.sidebar.selectbox("اختر الجنس", gender_options)
    
    # GPA range filter
    st.sidebar.markdown("**نطاق المعدل التراكمي**")
    gpa_range = st.sidebar.slider(
        "اختر نطاق المعدل التراكمي",
        min_value=float(df['gpa'].min()),
        max_value=float(df['gpa'].max()),
        value=(float(df['gpa'].min()), float(df['gpa'].max())),
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
    filtered_df = filtered_df[(filtered_df['gpa'] >= gpa_range[0]) & (filtered_df['gpa'] <= gpa_range[1])]
    
    # Display metrics
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("إجمالي الطلاب", len(filtered_df))
    with col2:
        st.metric("الطلاب النشطون", len(filtered_df[filtered_df['status'] == 'Active']))
    with col3:
        st.metric("الخريجون", len(filtered_df[filtered_df['status'] == 'Graduated']))
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
            enrollment_by_date = filtered_df.groupby(filtered_df['enrollment_date'].dt.year).size().reset_index()
            enrollment_by_date.columns = ['year', 'count']
            fig_trend = px.line(
                enrollment_by_date,
                x='year',
                y='count',
                markers=True,
                title="اتجاه التسجيل حسب السنة",
                labels={'count': 'عدد الطلاب', 'year': 'السنة'}
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
        
        # University Distribution
        st.subheader("أفضل الجامعات")
        university_counts = filtered_df['university'].value_counts().head(10).reset_index()
        university_counts.columns = ['university', 'count']
        fig_university = px.bar(
            university_counts,
            x='university',
            y='count',
            color='count',
            color_continuous_scale='Sunset',
            labels={'count': 'عدد الطلاب', 'university': 'الجامعة'},
            title="أفضل 10 جامعات"
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
        st.subheader("توزيع الأعمار")
        fig_age = px.box(
            filtered_df,
            x='program',
            y='age',
            color='program',
            labels={'age': 'العمر', 'program': 'البرنامج'},
            title="توزيع الأعمار حسب البرنامج"
        )
        fig_age.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)
        
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
        search_term = st.text_input("🔍 البحث بالاسم أو الدولة أو الجامعة", "")
        
        if search_term:
            mask = (
                filtered_df['name'].str.contains(search_term, case=False, na=False) |
                filtered_df['country'].str.contains(search_term, case=False, na=False) |
                filtered_df['university'].str.contains(search_term, case=False, na=False)
            )
            display_df = filtered_df[mask]
        else:
            display_df = filtered_df
        
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
        st.dataframe(display_df.describe(), use_container_width=True)
    
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
