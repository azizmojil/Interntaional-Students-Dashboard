import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import numpy as np
from utils import (
    map_country,
    map_continent,
    categorize_status,
    parse_hijri_year,
    format_hijri_date,
    map_gender,
    format_plot,
    ARABIC_TO_ENGLISH
)

# Page configuration
st.set_page_config(
    page_title="لوحة معلومات الطلاب الدوليين",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to mimic an AdminKit-like layout with RTL support
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

    :root {
        --primary: #0d6efd;
        --surface: #ffffff;
        --muted: #6b7280;
        --border: #e5e7eb;
    }

    /* Apply RTL to the main app container */
    .stApp {
        direction: rtl;
        text-align: right;
        font-family: 'Inter', sans-serif;
    }

    body {
        background: #f5f7fb;
        color: #111827;
    }
    
    /* Improve input visibility - targeting Streamlit widgets specifically */
    .stSelectbox div[data-baseweb="select"] > div,
    .stSelectbox div[data-baseweb="select"] span {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        caret-color: #111827 !important;
    }

    /* Force input text color and background */
    input[type="text"],
    .stTextInput input,
    .stNumberInput input {
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        caret-color: #111827 !important;
        background-color: #ffffff !important;
    }
    
    /* Placeholder styling */
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {
        color: #6b7280 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #6b7280 !important;
    }
    
    /* Dropdown menu items */
    ul[data-baseweb="menu"] li {
        color: #111827 !important;
        direction: rtl;
        text-align: right;
    }
    
    /* Fix Plotly Overlaps: Force LTR for the chart container to prevent coordinate flipping bugs */
    .js-plotly-plot, .plot-container {
        direction: ltr !important;
    }
    
    /* Ensure tooltips are readable */
    .js-plotly-plot .plotly .hovertext text {
        text-anchor: start !important;
    }
    
    /* Fix Streamlit slider interaction issues in RTL */
    .stSlider {
        direction: ltr !important;
    }
    
    /* Re-align slider label to right */
    .stSlider label {
        direction: rtl !important;
        text-align: right !important;
        width: 100%;
    }

    /* Fix sidebar collapse button position for RTL - move to right side */
    [data-testid="collapsedControl"] {
        left: auto !important;
        right: 0.5rem !important;
    }
    
    /* Fix Plotly hover tooltip positioning for RTL */
    .js-plotly-plot .hoverlayer .hovertext {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* Ensure hover box contains text properly */
    .js-plotly-plot .hoverlayer .hovertext rect {
        rx: 4;
        ry: 4;
    }
    
    /* Fix hover text alignment inside the box */
    .js-plotly-plot .hoverlayer .hovertext text {
        text-anchor: end !important;
    }
    
    /* Hide undefined text in Plotly legend/annotation areas */
    .js-plotly-plot .infolayer .legend .legendtext,
    .js-plotly-plot .infolayer .gtitle {
        visibility: hidden !important;
    }

    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #111827 0%, #0b1220 100%);
        color: #e5e7eb;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }
    [data-testid="stSidebar"] * {
        color: #e5e7eb !important;
    }
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"] {
        border-radius: 10px;
    }
    
    /* Sidebar inputs */
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.1);
        color: white !important;
    }
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    /* Stat cards */
    .stat-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 10px 30px rgba(17, 24, 39, 0.08);
        display: flex;
        gap: 12px;
        align-items: center;
        height: 100%;
        transition: transform 0.1s ease, box-shadow 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 32px rgba(17, 24, 39, 0.12);
    }
    .stat-icon {
        width: 42px;
        height: 42px;
        border-radius: 12px;
        background: rgba(13, 110, 253, 0.12);
        color: var(--accent, var(--primary));
        display: grid;
        place-items: center;
        font-size: 18px;
        font-weight: 700;
    }
    .stat-content p {
        margin: 0;
        color: var(--muted);
        font-weight: 600;
        font-size: 13px;
    }
    .stat-content h3 {
        margin: 2px 0 0;
        font-size: 24px;
        color: #111827;
        font-weight: 700;
    }

    /* Tabs */
    .stTabs [role="tablist"] {
        gap: 0.5rem;
    }
    .stTabs [role="tab"] {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 10px 14px;
        color: #111827;
        font-weight: 600;
    }
    .stTabs [role="tab"][aria-selected="true"] {
        background: var(--primary);
        color: #ffffff;
        border-color: var(--primary);
        box-shadow: 0 8px 20px rgba(13, 110, 253, 0.2);
    }

    /* Chart & table containers */
    [data-testid="stDataFrame"] {
        border: 1px solid var(--border);
        border-radius: 12px;
        box-shadow: 0 8px 24px rgba(17, 24, 39, 0.06);
    }
    .element-container:has(.plotly) {
        background: var(--surface);
        border-radius: 14px;
        padding: 12px 12px 4px;
        border: 1px solid var(--border);
        box-shadow: 0 8px 24px rgba(17, 24, 39, 0.06);
    }

    .divider {
        margin: 18px 0;
        border-bottom: 1px solid var(--border);
    }
    
    /* Hide header anchor links */
    [data-testid="stHeaderActionElements"] {
        display: none !important;
    }
    
    /* Hide all anchor tags inside headers */
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
    }
    
    /* Hide anchor links by href pattern (internal links) */
    a[href^="#"] {
        display: none !important;
    }
    
    /* Hide specific anchor class if present */
    a.anchor-link {
        display: none !important;
    }
    
    /* Hide anchor links (chain icon) next to headers */
    [data-testid="stMarkdownContainer"] h1 a,
    [data-testid="stMarkdownContainer"] h2 a,
    [data-testid="stMarkdownContainer"] h3 a,
    [data-testid="stMarkdownContainer"] h4 a,
    [data-testid="stMarkdownContainer"] h5 a,
    [data-testid="stMarkdownContainer"] h6 a {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
        processed["continent"] = processed["country"].apply(map_continent)
        # Add formatted Hijri date columns
        processed["admit_date_hijri"] = processed["term_admit"].apply(format_hijri_date)
        processed["last_term_hijri"] = processed["last_term"].apply(format_hijri_date)
        return processed
    except FileNotFoundError:
        st.error("❌ ملف البيانات غير موجود! يرجى التأكد من وجود 'data/data.xlsx'.")
        st.stop()
    except Exception as e:
        st.error(f"❌ خطأ في تحميل البيانات: {str(e)}")
        st.stop()

def gaussian_kde(data, bandwidth=None):
    """
    Compute Gaussian KDE manually to avoid scipy dependency.
    """
    data = np.asarray(data)
    n = len(data)
    if n == 0:
        return np.array([]), np.array([])
    
    std = np.std(data)
    if std == 0:
        # If all values are the same, return a spike
        return np.array([data[0]]), np.array([1.0])
        
    if bandwidth is None:
        # Scott's Rule
        bandwidth = 1.06 * std * (n ** (-1/5))
        
    if bandwidth == 0:
        bandwidth = 0.1

    min_x = data.min() - 3 * bandwidth
    max_x = data.max() + 3 * bandwidth
    x = np.linspace(min_x, max_x, 200)
    
    # Vectorized calculation
    # x[:, None] is (200, 1), data[None, :] is (1, n)
    # diff is (200, n)
    diff = (x[:, None] - data[None, :]) / bandwidth
    # pdf is (200,)
    pdf = (np.exp(-0.5 * diff**2) / np.sqrt(2 * np.pi)).sum(axis=1) / (n * bandwidth)
    
    return x, pdf


def build_intake_df_from_upload(
    applicants_df: pd.DataFrame,
    current_students_df: pd.DataFrame,   # pass FULL df (unfiltered)
    exclude_ksa: bool = True,
    current_country_col: str = "country"
):
    """
    applicants_df must have: country, applicants
    current_students_df must have: country (already mapped in your app's load_data)
    Returns: country, continent, applicants, current_students
    """
    req = {"country", "applicants"}
    if not req.issubset(applicants_df.columns):
        raise ValueError("Uploaded file must contain columns: country, applicants")

    up = applicants_df.copy()
    up["country"] = up["country"].astype(str).str.strip()
    up["applicants"] = pd.to_numeric(up["applicants"], errors="coerce").fillna(0).astype(int)

    # Normalize uploaded country to match your dashboard naming
    up["country"] = up["country"].apply(map_country)

    # Compute continent internally (no continent column needed)
    up["continent"] = up["country"].apply(map_continent)

    # Current students: DO NOT re-map; load_data already mapped it
    cur = current_students_df.copy()
    if current_country_col not in cur.columns:
        raise ValueError(f"current_students_df must contain '{current_country_col}'")

    cur[current_country_col] = cur[current_country_col].astype(str).str.strip()
    current_counts = cur.groupby(current_country_col).size().rename("current_students").reset_index()
    current_counts = current_counts.rename(columns={current_country_col: "country"})

    out = up.merge(current_counts, on="country", how="left")
    out["current_students"] = out["current_students"].fillna(0).astype(int)

    # Remove KSA (international only)
    if exclude_ksa:
        ksa_variants = {
            "المملكة العربية السعودية", "السعودية",
            "Saudi Arabia", "KSA", "Kingdom of Saudi Arabia"
        }
        out = out[~out["country"].isin(ksa_variants)].copy()

    out = out[out["applicants"] > 0].copy()

    return out[["country", "continent", "applicants", "current_students"]]


def allocate_seats_post_intake_representation(
    df: pd.DataFrame,
    seats: int,
    min_per_country: int = 0,
    max_seat_share: float = 1.0,
    max_post_share: float = 1.0,
):
    """
    Balance post-intake representation using applicants as target weights.

    Required columns in df:
      - country
      - applicants
      - current_students

    Constraints:
      - min_per_country: lower bound on admits per country (applied if feasible)
      - max_seat_share: admits_i <= floor(seats * max_seat_share)
      - max_post_share: (current_i + admits_i) <= floor(max_post_share * (total_current + seats))

    Returns df with:
      target_admits, post_total, post_share, target_weight
    """

    data = df.copy()
    for col in ["applicants", "current_students"]:
        data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0).astype(int)

    data = data[data["applicants"] > 0].copy()

    if data.empty or seats <= 0:
        data["target_admits"] = 0
        data["post_total"] = data["current_students"]
        data["post_share"] = 0.0
        data["target_weight"] = 0.0
        return data

    seats = int(seats)
    min_per_country = int(min_per_country)
    max_seat_share = float(max_seat_share)
    max_post_share = float(max_post_share)

    total_apps = int(data["applicants"].sum())
    total_current = int(data["current_students"].sum())
    post_total_all = total_current + seats

    # Target weights based on applicants
    data["target_weight"] = data["applicants"] / total_apps

    # Ideal post-intake totals and raw "top-up" need
    ideal_post_total = data["target_weight"] * post_total_all
    raw_need = (ideal_post_total - data["current_students"]).clip(lower=0)

    # If nobody needs seats (current already exceeds targets everywhere), fall back to weights
    if raw_need.sum() <= 0:
        raw_need = data["target_weight"].copy()

    # Scale needs to sum to seats
    scaled = raw_need * (seats / raw_need.sum())
    admits = np.floor(scaled).astype(int)

    # Caps
    cap_seat = int(np.floor(seats * max_seat_share))
    cap_seat = max(0, cap_seat)

    cap_post = np.floor(max_post_share * post_total_all - data["current_students"]).astype(int)
    cap_post = cap_post.clip(lower=0)

    cap_final = np.minimum(cap_seat, cap_post)

    # Apply caps (cap beats min if infeasible)
    admits = np.minimum(admits, cap_final)

    # Try to apply minimums only where possible
    if min_per_country > 0:
        admits = np.minimum(np.maximum(admits, min_per_country), cap_final)

    data["target_admits"] = admits.astype(int)

    def remaining():
        return int(seats - data["target_admits"].sum())

    rem = remaining()

    # Distribute remaining seats by largest fractional remainder of 'scaled', respecting caps
    frac = (scaled - np.floor(scaled)).to_numpy()
    guard = 0
    while rem > 0 and guard < 10_000_000:
        guard += 1
        eligible = data["target_admits"].to_numpy() < cap_final.to_numpy()
        if not eligible.any():
            break
        # pick eligible with highest frac; if ties/zero, use target_weight
        score = np.where(eligible, frac, -np.inf)
        idx = int(np.argmax(score))
        if not np.isfinite(score[idx]):
            # fallback: weight-based
            score2 = np.where(eligible, data["target_weight"].to_numpy(), -np.inf)
            idx = int(np.argmax(score2))
            if not np.isfinite(score2[idx]):
                break
        data.iloc[idx, data.columns.get_loc("target_admits")] += 1
        rem = remaining()

    # If overshot (can happen when mins bind), remove from lowest priority above min
    guard = 0
    while rem < 0 and guard < 10_000_000:
        guard += 1
        can_remove = data["target_admits"] > max(0, min_per_country)
        if not can_remove.any():
            break
        # remove from those with smallest fractional remainder (or smallest weight)
        score = np.where(can_remove.to_numpy(), frac, np.inf)
        idx = int(np.argmin(score))
        data.iloc[idx, data.columns.get_loc("target_admits")] -= 1
        rem = remaining()

    # Post-intake diagnostics
    data["post_total"] = data["current_students"] + data["target_admits"]
    data["post_share"] = data["post_total"] / float(post_total_all)

    return data.sort_values("target_admits", ascending=False).reset_index(drop=True)


def herfindahl_share(counts: pd.Series) -> float:
    """Concentration index: sum_i (share_i^2). Lower = more balanced."""
    total = counts.sum()
    if total <= 0:
        return 0.0
    s = (counts / total).astype(float)
    return float((s * s).sum())


# Main app
def main():
    # Title
    st.title("🎓 لوحة معلومات الطلاب الدوليين")
    st.markdown("### تحليلات ذكاء الأعمال لبيانات الطلاب الدوليين")
    
    # Load data
    df = load_data()
    
    # Removed Hero Header as requested
    
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
    
    # College filter
    colleges = ['الكل'] + sorted(df['college'].dropna().unique().tolist())
    selected_college = st.sidebar.selectbox("اختر الكلية", colleges)
    
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
    if selected_college != 'الكل':
        filtered_df = filtered_df[filtered_df['college'] == selected_college]
    if selected_program != 'الكل':
        filtered_df = filtered_df[filtered_df['program'] == selected_program]
    if selected_status != 'الكل':
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    if selected_gender != 'الكل':
        filtered_df = filtered_df[filtered_df['gender'] == selected_gender]
    gpa_for_filter = filtered_df['gpa'].fillna(gpa_min)
    filtered_df = filtered_df[(gpa_for_filter >= gpa_range[0]) & (gpa_for_filter <= gpa_range[1])]
    
    # Display metrics as AdminKit-like stat cards
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    avg_gpa = filtered_df['gpa'].mean()
    stats = [
        {
            "label": "إجمالي الطلاب",
            "value": f"{len(filtered_df):,}",
            "icon": "👥",
            "color": "#0d6efd"
        },
        {
            "label": "الطلاب النشطون",
            "value": f"{len(filtered_df[filtered_df['status'] == 'نشط']):,}",
            "icon": "✅",
            "color": "#22c55e"
        },
        {
            "label": "الخريجون",
            "value": f"{len(filtered_df[filtered_df['status'] == 'متخرج']):,}",
            "icon": "🎓",
            "color": "#f97316"
        },
        {
            "label": "متوسط المعدل",
            "value": f"{avg_gpa:.2f}" if not np.isnan(avg_gpa) else "--",
            "icon": "⭐",
            "color": "#8b5cf6"
        },
        {
            "label": "عدد الدول",
            "value": f"{filtered_df['country'].nunique():,}",
            "icon": "🌍",
            "color": "#14b8a6"
        }
    ]
    stat_cols = st.columns(len(stats))
    for col, stat in zip(stat_cols, stats):
        col.markdown(f"""
            <div class="stat-card" style="--accent: {stat['color']}">
                <div class="stat-icon">{stat['icon']}</div>
                <div class="stat-content">
                    <p>{stat['label']}</p>
                    <h3>{stat['value']}</h3>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📈 نظرة عامة", "🌍 التحليل الجغرافي", "📊 الأداء الأكاديمي", "📋 جدول البيانات", "🎯 خطة القبول"])

    with tab5:
        st.subheader("🎯 خطة القبول لتحقيق توازن التمثيل بعد القبول (Stock + Flow)")

        st.markdown("""
        **الفكرة:** نستخدم عدد المتقدمين كـ *وزن مستهدف* لتوزيع إجمالي الطلاب بعد القبول
        (الطلاب الحاليين + المقبولين الجدد).  
        ثم نحسب القبول المطلوب لكل دولة كـ **تعويض/تغذية (Top-up)** للوصول لهذا التمثيل،
        مع قيود اختيارية لتجنب التركز.
        """)

        colA, colB, colC, colD = st.columns(4)
        seats = colA.number_input("عدد المقاعد المتاحة", min_value=0, value=300, step=10)
        min_per_country = colB.number_input("حد أدنى للمقبولين لكل دولة", min_value=0, value=0, step=1)
        max_share = colC.slider("حد أقصى كنسبة من المقاعد الجديدة لكل دولة", min_value=0.05, max_value=1.0, value=0.25,
                                step=0.05)
        max_post_share = colD.slider("حد أقصى للتمثيل بعد القبول (نسبة من الإجمالي)", min_value=0.02, max_value=1.0,
                                     value=0.10, step=0.01)

        st.markdown("### 1) ارفع ملف المتقدمين (CSV)")
        st.caption("الأعمدة المطلوبة: country, applicants  (والدولة يمكن أن تكون عربي/إنجليزي حسب mapping لديك)")
        uploaded = st.file_uploader("Upload applicants.csv", type=["csv"], key="applicants_upload")

        if uploaded is None:
            st.info("ارفع ملف المتقدمين لإنتاج الخطة والخرائط.")
        else:
            applicants_df = pd.read_csv(uploaded)

            if not {"country", "applicants"}.issubset(applicants_df.columns):
                st.error("الملف يجب أن يحتوي الأعمدة: country, applicants")
            else:
                # Build intake df using your existing current dataset
                intake_df = build_intake_df_from_upload(
                    applicants_df=applicants_df,
                    current_students_df=df,
                    exclude_ksa=True
                )

                if intake_df.empty:
                    st.warning("لا توجد صفوف صالحة بعد المعالجة (تحقق من أسماء الدول أو أن applicants > 0).")
                else:
                    plan = allocate_seats_post_intake_representation(
                        df=intake_df,
                        seats=int(seats),
                        min_per_country=int(min_per_country),
                        max_seat_share=float(max_share),
                        max_post_share=float(max_post_share),
                    )

                    # ---- KPIs
                    total_apps = int(plan["applicants"].sum())
                    total_admits = int(plan["target_admits"].sum())
                    total_current = int(plan["current_students"].sum())
                    post_total_all = total_current + int(seats)

                    # Intake acceptance rate (diagnostic only)
                    intake_rate = (total_admits / total_apps) if total_apps else 0.0
                    hhi = herfindahl_share(plan["target_admits"])

                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("إجمالي المتقدمين", f"{total_apps:,}")
                    m2.metric("الطلاب الحاليين (للبلدان الموجودة بالملف)", f"{total_current:,}")
                    m3.metric("المقبولين الجدد (المخطط)", f"{total_admits:,}")
                    m4.metric("معدل القبول (للمتقدمين فقط)", f"{intake_rate:.2%}")

                    st.caption(
                        f"مؤشر التركز (Herfindahl) للمقاعد الجديدة = {hhi:.4f} — كلما كان أقل كان التوزيع أكثر توازناً.")

                    # ---- Map
                    st.markdown("### 2) الخريطة العالمية للمقاعد المقترحة")
                    plan_map = plan.copy()

                    # Map Arabic -> English names for Plotly if available
                    if "ARABIC_TO_ENGLISH" in globals():
                        plan_map["country_en"] = plan_map["country"].map(ARABIC_TO_ENGLISH).fillna(plan_map["country"])
                    else:
                        plan_map["country_en"] = plan_map["country"]

                    fig_map = px.choropleth(
                        plan_map,
                        locations="country_en",
                        locationmode="country names",
                        color="target_admits",
                        hover_name="country",
                        hover_data={
                            "applicants": True,
                            "current_students": True,
                            "target_admits": True,
                            "post_total": True,
                            "post_share": ":.2%",
                            "target_weight": ":.2%"
                        },
                        labels={"target_admits": "المقاعد المقترحة"}
                    )
                    fig_map.update_layout(
                        geo=dict(showframe=False, showcoastlines=False, projection_type="equirectangular"))
                    st.plotly_chart(fig_map, use_container_width=True)

                    # ---- Top bar
                    st.markdown("### 3) أعلى الدول من حيث المقاعد المقترحة")
                    topN = plan.sort_values("target_admits", ascending=False).head(20).copy()
                    fig_bar = px.bar(
                        topN,
                        x="country",
                        y="target_admits",
                        hover_data={
                            "applicants": True,
                            "current_students": True,
                            "post_share": ":.2%"
                        },
                        labels={"country": "الدولة", "target_admits": "المقاعد المقترحة"}
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                    # ---- Table + download
                    st.markdown("### 4) جدول الخطة")
                    show = plan.rename(columns={
                        "country": "الدولة",
                        "continent": "القارة",
                        "applicants": "عدد المتقدمين",
                        "current_students": "الطلاب الحاليين",
                        "target_admits": "المقاعد المقترحة",
                        "post_total": "إجمالي بعد القبول",
                        "post_share": "حصة بعد القبول",
                        "target_weight": "وزن مستهدف"
                    })
                    st.dataframe(show, use_container_width=True, hide_index=True)

                    csv = show.to_csv(index=False).encode("utf-8")
                    st.download_button(
                        "📥 تنزيل خطة القبول (CSV)",
                        data=csv,
                        file_name="admissions_plan.csv",
                        mime="text/csv",
                    )

    with tab1:
        # Overview tab
        col1, col2 = st.columns(2)
        
        with col1:
            # Students by College (was Program)
            st.subheader("عدد الطلاب حسب الكلية")
            college_counts_overview = filtered_df['college'].value_counts().reset_index()
            college_counts_overview.columns = ['college', 'count']
            fig_college_overview = px.bar(
                college_counts_overview,
                x='college',
                y='count',
                labels={'count': 'عدد الطلاب', 'college': 'الكلية'}
            )
            fig_college_overview.update_traces(marker_color='#0d6efd', name='')
            fig_college_overview.update_layout(showlegend=False)
            st.plotly_chart(format_plot(fig_college_overview), use_container_width=True)
        
        with col2:
            # Students by Status
            st.subheader("عدد الطلاب حسب الحالة الأكاديمية")
            status_counts = filtered_df['status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            fig_status = px.pie(
                status_counts,
                values='count',
                names='status',
                color_discrete_sequence=px.colors.qualitative.Set2,
                hole=0.5
            )
            # Update traces to show labels and hide hover info
            fig_status.update_traces(textinfo='label+percent+value', hoverinfo='skip')
            st.plotly_chart(format_plot(fig_status), use_container_width=True)
        
        col3, col4 = st.columns(2)
        
        with col3:
            # Gender Distribution
            st.subheader("التوزيع حسب الجنس")
            # Filter out "غير محدد" from gender visualization
            gender_df = filtered_df[filtered_df['gender'] != "غير محدد"]
            gender_counts = gender_df['gender'].value_counts().reset_index()
            gender_counts.columns = ['gender', 'count']
            fig_gender = px.pie(
                gender_counts,
                values='count',
                names='gender',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                hole=0.5
            )
            # Update traces to show labels and hide hover info
            fig_gender.update_traces(textinfo='label+percent+value', hoverinfo='skip')
            st.plotly_chart(format_plot(fig_gender), use_container_width=True)
        
        with col4:
            # Enrollment Trend
            st.subheader("عدد الطلاب المسجلين سنوياً")
            timeline_df = filtered_df.dropna(subset=['timeline_year']).copy()
            timeline_df['timeline_year'] = timeline_df['timeline_year'].astype(int)
            enrollment_by_date = timeline_df.groupby('timeline_year').size().reset_index(name='count')
            fig_trend = px.line(
                enrollment_by_date,
                x='timeline_year',
                y='count',
                markers=True,
                labels={'count': 'عدد الطلاب', 'timeline_year': 'السنة الهجرية'}
            )
            fig_trend.update_traces(line_color='#636EFA', line_width=3, name='')
            # Add "هـ" suffix with space for better readability in Hijri year labels
            fig_trend.update_xaxes(ticksuffix=" هـ")
            st.plotly_chart(format_plot(fig_trend), use_container_width=True)
    
    with tab2:
        # Geographic Analysis tab
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # World Map
            st.subheader("التوزيع بحسب الجنسية")
            
            # Prepare data for map
            map_data = filtered_df['country'].value_counts().reset_index()
            map_data.columns = ['country_ar', 'count']
            
            # Map Arabic names to English for Plotly
            map_data['country_en'] = map_data['country_ar'].map(ARABIC_TO_ENGLISH)
            
            fig_map = px.choropleth(
                map_data,
                locations='country_en',
                locationmode='country names',
                color='count',
                hover_name='country_ar',
                color_continuous_scale='Viridis',
                labels={'count': 'عدد الطلاب'}
            )
            fig_map.update_layout(
                geo=dict(
                    showframe=False,
                    showcoastlines=False,
                    projection_type='equirectangular'
                )
            )
            st.plotly_chart(format_plot(fig_map), use_container_width=True)
        
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
                labels={'gpa': 'المعدل التراكمي', 'count': 'عدد الطلاب'}
            )
            fig_gpa_hist.update_traces(name='')
            st.plotly_chart(format_plot(fig_gpa_hist), use_container_width=True)
        
        with col2:
            # Average GPA by Program
            st.subheader("متوسط المعدل حسب البرنامج")
            avg_gpa_program = filtered_df.groupby('program')['gpa'].mean().sort_values(ascending=False).reset_index()
            fig_gpa_program = px.bar(
                avg_gpa_program,
                x='program',
                y='gpa',
                labels={'gpa': 'متوسط المعدل', 'program': 'البرنامج'}
            )
            fig_gpa_program.update_traces(marker_color='#0d6efd', name='')
            fig_gpa_program.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(format_plot(fig_gpa_program), use_container_width=True)
        
        # KDE Chart of GPA
        st.subheader("توزيع كثافة المعدل التراكمي (KDE)")
        gpa_data = filtered_df['gpa'].dropna()
        if gpa_data.empty or len(gpa_data) < 2:
            st.info("لا توجد بيانات كافية لعرض الرسم البياني")
        else:
            # Calculate KDE manually to avoid scipy dependency
            x_kde, y_kde = gaussian_kde(gpa_data)
            
            fig_kde = px.area(
                x=x_kde, 
                y=y_kde,
                labels={'x': 'المعدل التراكمي', 'y': 'الكثافة'}
            )
            # Fix: 'fill_color' is not a valid property for update_traces in this context.
            # Use 'fillcolor' (no underscore) for area charts in Plotly.
            fig_kde.update_traces(line_color='#0d6efd', fillcolor='rgba(13, 110, 253, 0.2)', name='')
            st.plotly_chart(format_plot(fig_kde), use_container_width=True)
        
        # GPA by Country (Top 10)
        st.subheader("متوسط المعدل حسب الدولة (أفضل 10)")
        avg_gpa_country = filtered_df.groupby('country')['gpa'].mean().sort_values(ascending=False).head(10).reset_index()
        fig_gpa_country = px.bar(
            avg_gpa_country,
            x='country',
            y='gpa',
            labels={'gpa': 'متوسط المعدل', 'country': 'الدولة'}
        )
        fig_gpa_country.update_traces(marker_color='#0d6efd', name='')
        st.plotly_chart(format_plot(fig_gpa_country), use_container_width=True)
    
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
            "continent": "القارة",
            "program": "التخصص",
            "college": "الكلية",
            "status": "الحالة المختصرة",
            "status_detail": "تفاصيل الحالة",
            "gpa": "المعدل التراكمي",
            "hours": "الساعات المكتسبة",
            "funding": "نوع المنحة",
            "term_admit": "فصل القبول",
            "admit_date_hijri": "تاريخ القبول (هجري)",
            "last_term": "آخر فصل",
            "last_term_hijri": "تاريخ آخر فصل (هجري)",
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

if __name__ == "__main__":
    main()
