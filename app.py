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
    ARABIC_TO_ENGLISH,
    NATIONALITY_MAPPING,
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

    /* Selectbox text visibility */
/* Main area (light background): keep text dark */
.stSelectbox div[data-baseweb="select"] > div,
.stSelectbox div[data-baseweb="select"] span,
.stSelectbox div[data-baseweb="select"] input {
    color: #111827 !important;
    -webkit-text-fill-color: #111827 !important;
    caret-color: #111827 !important;
}

/* Sidebar selectboxes: white background + black text */
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div,
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] span,
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] input {
    color: #000000 !important;
    -webkit-text-fill-color: #e5e7eb !important;
    caret-color: #000000 !important;
}
/* Force input text color and background - Aggressive override */
    input,
    input[type="text"],
    .stTextInput input,
    .stNumberInput input,
    div[data-baseweb="input"] input {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
        background-color: #ffffff !important;
    }

    /* Placeholder styling */
    .stTextInput input::placeholder,
    .stNumberInput input::placeholder {
        color: #6b7280 !important;
        opacity: 1 !important;
        -webkit-text-fill-color: #6b7280 !important;
    }

    /* Dropdown menu: full RTL for container, list, and items */
ul[data-baseweb="menu"],
[role="listbox"] {
    direction: rtl !important;
    text-align: right !important;
}
ul[data-baseweb="menu"] li,
[role="option"] {
    direction: rtl !important;
    text-align: right !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}
ul[data-baseweb="menu"] li span,
ul[data-baseweb="menu"] li div,
[role="option"] span,
[role="option"] div {
    direction: rtl !important;
    text-align: right !important;
}
[data-baseweb="popover"] {
    direction: rtl !important;
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

/* Plotly hover tooltip – restored to previous working state */
.js-plotly-plot .hoverlayer .hovertext text {
    text-anchor: end !important;
}
.js-plotly-plot .hoverlayer .hovertext rect {
    rx: 4;
    ry: 4;
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
    background-color: #ffffff !important;
}

/* Sidebar selectbox: ensure inner control is white so black text is readable */
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
    background: #ffffff !important;
}
/* (Text color handled in the "Sidebar (dark background)" block above) */
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
        flex-shrink: 0;
    }
    .stat-content {
        flex: 1;
        text-align: right;
        direction: rtl;
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
    /* Sidebar input text should be light on dark sidebar */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea,
[data-testid="stSidebar"] div[data-baseweb="input"] input,
[data-testid="stSidebar"] div[data-baseweb="select"] input {
  color: #e5e7eb !important;
  -webkit-text-fill-color: #e5e7eb !important;
  caret-color: #e5e7eb !important;
  background: rgba(255, 255, 255, 0.08) !important;
}

/* Sidebar placeholders */
[data-testid="stSidebar"] input::placeholder,
[data-testid="stSidebar"] textarea::placeholder {
  color: rgba(229, 231, 235, 0.65) !important;
  -webkit-text-fill-color: rgba(229, 231, 235, 0.65) !important;
  opacity: 1 !important;
}
div[data-baseweb="popover"] input {
  color: #111827 !important;
  -webkit-text-fill-color: #111827 !important;
  background: #ffffff !important;
}
/* === FINAL OVERRIDES (must be last) === */
/* Sidebar selectboxes: force true black */
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] * {
  color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
  opacity: 1 !important;
}
[data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] > div {
  background: #ffffff !important;
}

/* If dropdown/search renders in a popover outside sidebar DOM */
div[data-baseweb="popover"] div[data-baseweb="select"] * ,
div[data-baseweb="popover"] div[data-baseweb="select"] input {
  color: #000000 !important;
  -webkit-text-fill-color: #000000 !important;
  opacity: 1 !important;
}

    /* ── RTL fixes for acceptance plan tab components ── */

    /* Selectbox: RTL dropdown control and menu */
    .stSelectbox [data-baseweb="select"] > div {
        direction: rtl !important;
        text-align: right !important;
    }
    .stSelectbox [data-baseweb="select"] [data-baseweb="icon"] {
        order: -1;
    }

    /* Multiselect: RTL tags and search input */
    .stMultiSelect [data-baseweb="select"] > div {
        direction: rtl !important;
        text-align: right !important;
    }
    .stMultiSelect [data-baseweb="tag"] {
        direction: rtl;
    }

    /* Number input: RTL layout for container and label.
       BaseWeb sets direction:ltr on [data-baseweb="input"] internally,
       so we override it here, then re-force the <input> to LTR so
       digits still render in the correct order. */
    div[data-testid="stNumberInput"],
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stNumberInput"] [data-baseweb="form-control"],
    div[data-testid="stNumberInput"] [data-baseweb="input"] {
        direction: rtl !important;
        text-align: right !important;
    }
    div[data-testid="stNumberInput"] label,
    div[data-testid="stNumberInput"] p {
        direction: rtl !important;
        text-align: right !important;
        width: 100% !important;
        display: block !important;
    }
    /* Keep the actual number value LTR inside the box */
    div[data-testid="stNumberInput"] input[type="number"] {
        direction: ltr !important;
        text-align: right !important;
    }

    /* File uploader: RTL label and drop zone */
    [data-testid="stFileUploader"] {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploaderDropzone"] {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] {
        direction: rtl;
        text-align: right;
    }

    /* Metric: RTL label and value */
    [data-testid="stMetric"],
    [data-testid="metric-container"] {
        direction: rtl;
        text-align: right;
    }

    /* Alert boxes (info / warning / error) */
    [data-testid="stAlert"],
    [data-testid="stAlert"] * {
        direction: rtl;
        text-align: right;
    }

    /* Caption */
    [data-testid="stCaptionContainer"] {
        direction: rtl;
        text-align: right;
    }

    /* Buttons */
    .stButton > button {
        direction: rtl;
    }

    /* Markdown content */
    [data-testid="stMarkdownContainer"] {
        direction: rtl;
        text-align: right;
    }

    /* Dataframe header and cells: RTL */
    [data-testid="stDataFrame"] th,
    [data-testid="stDataFrame"] td {
        direction: rtl;
        text-align: right !important;
    }

    /* Download button */
    [data-testid="stDownloadButton"] > button {
        direction: rtl;
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
        bandwidth = 1.06 * std * (n ** (-1 / 5))

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
    pdf = (np.exp(-0.5 * diff ** 2) / np.sqrt(2 * np.pi)).sum(axis=1) / (n * bandwidth)

    return x, pdf


def suggest_applicants(
        applicants_df: pd.DataFrame,
        current_students_df: pd.DataFrame,
        intl_seats: int,
        country_targets_en: dict,
) -> pd.DataFrame:
    """
    Suggest which applicants to accept.

    Priority order:
      1. Country targets  – fill specified minimums per nationality first
      2. Geographical balance – underrepresented countries (low current share) get priority
      3. Discipline balance  – accepted slots are distributed as evenly as possible across
                               disciplines; 2nd/3rd choice used when 1st is overloaded.

    applicants_df must have: applicant_id, nationality, disc1, disc2, disc3
    current_students_df must have: country, program
    country_targets_en: {english_country_name: min_count}

    Returns applicants_df with added columns:
      mapped_nationality, geo_score, accepted, acceptance_reason,
      assigned_discipline, accepted_at_choice
    """
    data = applicants_df.copy().reset_index(drop=True)

    # Map uploaded nationalities to internal Arabic country names
    data["mapped_nationality"] = data["nationality"].astype(str).str.strip().apply(map_country)

    # ── Geographical score (higher = more underrepresented in current enrollment)
    current_country_counts = current_students_df["country"].value_counts()
    total_current = max(len(current_students_df), 1)

    def geo_score_fn(country):
        share = current_country_counts.get(country, 0) / total_current
        return round(1.0 - share, 4)

    data["geo_score"] = data["mapped_nationality"].apply(geo_score_fn)
    data["accepted"] = False
    data["acceptance_reason"] = ""
    data["assigned_discipline"] = ""
    data["accepted_at_choice"] = 0

    accepted_set: set = set()
    seats_used = 0
    disc_counts: dict = {}  # tracks accepted-applicant discipline load (starts at 0, ignore existing)

    def find_best_disc(row):
        """Return (discipline, choice_rank) whose accepted count is lowest; prefer lower rank on tie."""
        choices = []
        for rank, col in enumerate(["disc1", "disc2", "disc3"], 1):
            disc = row[col]
            disc = str(disc).strip() if not pd.isna(disc) else ""
            if not disc:
                continue
            choices.append((disc_counts.get(disc, 0), rank, disc))
        if not choices:
            return "", 0
        choices.sort()  # ascending count, then ascending rank
        return choices[0][2], choices[0][1]

    def accept(idx, primary_reason):
        nonlocal seats_used
        row = data.loc[idx]
        disc, rank = find_best_disc(row)
        disc_counts[disc] = disc_counts.get(disc, 0) + 1
        # If a non-first choice was needed to balance disciplines, note it
        if rank > 1:
            final_reason = "توازن تخصصات"
        else:
            final_reason = primary_reason
        data.at[idx, "accepted"] = True
        data.at[idx, "acceptance_reason"] = final_reason
        data.at[idx, "assigned_discipline"] = disc
        data.at[idx, "accepted_at_choice"] = rank
        accepted_set.add(idx)
        seats_used += 1

    # ── Phase 1: Country targets
    mapped_targets = {map_country(en): cnt for en, cnt in country_targets_en.items()}

    for country, target in mapped_targets.items():
        if seats_used >= intl_seats:
            break
        quota = min(target, intl_seats - seats_used)
        candidates = data[
            (data["mapped_nationality"] == country) &
            (~data.index.isin(accepted_set))
        ]
        count = 0
        for idx in candidates.index:
            if count >= quota:
                break
            accept(idx, "هدف جنسية محددة")
            count += 1

    # ── Phase 2: Geographical balance + discipline balance
    # Process in geo-score order; discipline is assigned dynamically per accepted applicant
    remaining_seats = intl_seats - seats_used
    if remaining_seats > 0:
        remaining = data[~data.index.isin(accepted_set)].sort_values(
            "geo_score", ascending=False
        )
        count = 0
        for idx in remaining.index:
            if count >= remaining_seats:
                break
            accept(idx, "توازن جغرافي")
            count += 1

    return data


def compute_grant_allocations(
    forecast_years: list,
    external_grants: dict,
    reservations: list,
    country_hist: pd.DataFrame,
    cont_lookup: dict,
    continents_list: list,
) -> dict:
    """
    Compute per-country external grant allocation for each forecast year.

    Parameters
    ----------
    forecast_years   : [int, …]  ordered list of forecast Hijri years
    external_grants  : {year: int}  number of external grants per year
    reservations     : list of {"region": str, "seats": {year: int}}
                       region is either a continent name (Arabic) or a country name (Arabic)
    country_hist     : DataFrame with columns ['country', 'hist_5yr_total', 'hist_annual_avg']
    cont_lookup      : {country_ar: continent_ar}
    continents_list  : [str, …] list of known continent names (Arabic)

    Returns
    -------
    {year: {country_ar: seats_int}}
    """
    allocations = {}

    for yr in forecast_years:
        ext = external_grants.get(yr, 0)

        # --- Resolve reservations into per-country counts -----------------
        country_res: dict = {}   # {country_ar: reserved_seats}
        continent_res: dict = {}  # {continent_ar: reserved_seats}

        for res in reservations:
            region = res.get("region", "")
            seats = res.get("seats", {}).get(yr, 0)
            if not region or seats == 0:
                continue
            if region in continents_list:
                continent_res[region] = continent_res.get(region, 0) + seats
            else:
                country_res[region] = country_res.get(region, 0) + seats

        # Expand continent reservations proportionally among countries in that continent
        # Uses floor + distribute-remainder to guarantee sum == cont_seats
        for cont, cont_seats in continent_res.items():
            cont_df = country_hist[
                country_hist["country"].apply(lambda c: cont_lookup.get(c, "") == cont)
            ].copy()
            if cont_df.empty:
                continue
            ct = cont_df["hist_5yr_total"].sum()
            n_c = len(cont_df)
            if ct > 0:
                cont_df["raw_share"] = cont_df["hist_5yr_total"] / ct * cont_seats
            else:
                cont_df["raw_share"] = cont_seats / n_c
            cont_df["floor_alloc"] = cont_df["raw_share"].apply(np.floor).astype(int)
            cont_leftover = cont_seats - cont_df["floor_alloc"].sum()
            if cont_leftover > 0:
                top_cont_idx = (cont_df["raw_share"] - cont_df["floor_alloc"]).nlargest(
                    min(int(cont_leftover), n_c)
                ).index
                cont_df.loc[top_cont_idx, "floor_alloc"] += 1
            for country_c, alloc_c in zip(
                cont_df["country"].tolist(), cont_df["floor_alloc"].tolist()
            ):
                country_res[country_c] = country_res.get(country_c, 0) + alloc_c

        reserved_total = sum(country_res.values())
        remaining = max(0, ext - reserved_total)

        # --- Balance remaining seats among non-reserved countries ----------
        non_res = country_hist[~country_hist["country"].isin(country_res)].copy()
        balanced: dict = {}

        if remaining > 0 and not non_res.empty:
            n = len(non_res)
            total_hist = non_res["hist_5yr_total"].sum()

            if total_hist > 0:
                non_res["share"] = non_res["hist_5yr_total"] / total_hist
                # Inverse share: underrepresented countries get more seats
                non_res["inv_score"] = 1.0 - non_res["share"]
                inv_sum = non_res["inv_score"].sum()
                if inv_sum > 0:
                    non_res["raw_alloc"] = non_res["inv_score"] / inv_sum * remaining
                else:
                    non_res["raw_alloc"] = remaining / n
            else:
                non_res["raw_alloc"] = remaining / n

            # Floor + distribute leftover seats to top fractional remainders
            non_res["alloc"] = non_res["raw_alloc"].apply(np.floor).astype(int)
            leftover = remaining - non_res["alloc"].sum()
            if leftover > 0:
                top_idx = (non_res["raw_alloc"] - non_res["alloc"]).nlargest(int(leftover)).index
                non_res.loc[top_idx, "alloc"] += 1

            balanced = dict(
                zip(non_res["country"].tolist(), non_res["alloc"].tolist())
            )

        allocations[yr] = {**country_res, **balanced}

    return allocations


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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
        ["📈 نظرة عامة", "🌍 التحليل الجغرافي", "📊 الأداء الأكاديمي", "📋 جدول البيانات",
         "🎯 خطة القبول", "🌐 معدلات القبول المتوقعة"])

    with tab5:
        st.subheader("خطة القبول")

        # ── Step 1: local students ──────────────────────────────────────────
        st.markdown("### 1) عدد الطلاب المحليين المقبولين")
        local_students = st.number_input(
            "أدخل عدد الطلاب المحليين المقبولين هذا العام",
            min_value=0, value=2000, step=50, key="local_students_input"
        )
        intl_seats = round(local_students * 0.05)

        c1, c2 = st.columns(2)
        c1.metric("الطلاب المحليون المقبولون", f"{local_students:,}")
        c2.metric("مقاعد الطلاب الدوليين (5%)", f"{intl_seats:,}")

        st.markdown("---")

        # ── Step 2: optional nationality targets ───────────────────────────
        st.markdown("### 2) أهداف الجنسيات (اختياري)")
        st.caption("حدد حداً أدنى من المقبولين لجنسيات بعينها.")

        all_countries_ar = sorted(
            {k for k in ARABIC_TO_ENGLISH if k and k != "غير محدد"}
        )

        # Dynamic add-row nationality targets using session state
        if "nat_targets" not in st.session_state:
            st.session_state.nat_targets = []

        to_delete = None
        for i, entry in enumerate(st.session_state.nat_targets):
            r1, r2, r3 = st.columns([4, 2, 1])
            chosen = r1.selectbox(
                f"الجنسية {i + 1}",
                options=[""] + all_countries_ar,
                index=([""] + all_countries_ar).index(entry["country"])
                if entry["country"] in all_countries_ar else 0,
                key=f"nat_country_{i}",
            )
            tgt_val = r2.number_input(
                "العدد المستهدف",
                min_value=0,
                value=entry["target"],
                step=10,
                key=f"nat_target_{i}",
            )
            if r3.button("حذف", key=f"nat_del_{i}"):
                to_delete = i
            st.session_state.nat_targets[i] = {"country": chosen, "target": tgt_val}

        if to_delete is not None:
            st.session_state.nat_targets.pop(to_delete)
            st.rerun()

        if st.button("+ أضف جنسية"):
            st.session_state.nat_targets.append({"country": "", "target": 50})
            st.rerun()

        country_targets_en: dict = {
            e["country"]: e["target"]
            for e in st.session_state.nat_targets
            if e["country"] and e["target"] > 0
        }

        if country_targets_en:
            total_targets = sum(country_targets_en.values())
            if total_targets > intl_seats > 0:
                st.warning(
                    f"مجموع الأهداف ({total_targets:,}) يتجاوز المقاعد المتاحة ({intl_seats:,}). "
                    "سيتم تطبيق الأهداف بالترتيب حتى اكتمال المقاعد."
                )

        st.markdown("---")

        # ── Step 3: upload applicants ──────────────────────────────────────
        st.markdown("### 3) رفع ملف المتقدمين")
        st.markdown(
            "**الأعمدة المطلوبة:** `ID` · `Nationality` · "
            "`1st Discipline` · `2nd Discipline` · `3rd Discipline`"
        )

        uploaded = st.file_uploader(
            "ارفع ملف المتقدمين (CSV)", type=["csv"], key="applicants_upload"
        )

        if uploaded is None:
            st.info("ارفع ملف المتقدمين للحصول على اقتراحات القبول.")
        else:
            raw_df = pd.read_csv(uploaded)
            raw_df.columns = [c.strip() for c in raw_df.columns]
            lower_cols = {c.lower(): c for c in raw_df.columns}

            def find_col(patterns):
                for p in patterns:
                    if p in lower_cols:
                        return lower_cols[p]
                return None

            id_col  = find_col(["id"])
            nat_col = find_col(["nationality", "national", "nation"])
            d1_col  = find_col(["1st discipline", "1st desired discipline",
                                 "disc1", "discipline1", "discipline_1", "first discipline"])
            d2_col  = find_col(["2nd discipline", "2nd desired discipline",
                                 "disc2", "discipline2", "discipline_2", "second discipline"])
            d3_col  = find_col(["3rd discipline", "3rd desired discipline",
                                 "disc3", "discipline3", "discipline_3", "third discipline"])

            missing_cols = []
            if not id_col:  missing_cols.append("ID")
            if not nat_col: missing_cols.append("Nationality")
            if not d1_col:  missing_cols.append("1st Discipline")
            if not d2_col:  missing_cols.append("2nd Discipline")
            if not d3_col:  missing_cols.append("3rd Discipline")

            if missing_cols:
                st.error(f"الملف يفتقد الأعمدة التالية: {', '.join(missing_cols)}")
            elif intl_seats == 0:
                st.warning("عدد المقاعد الدولية صفر. يرجى إدخال عدد الطلاب المحليين.")
            else:
                adf = raw_df.rename(columns={
                    id_col:  "applicant_id",
                    nat_col: "nationality",
                    d1_col:  "disc1",
                    d2_col:  "disc2",
                    d3_col:  "disc3",
                })[["applicant_id", "nationality", "disc1", "disc2", "disc3"]].copy()

                results_df = suggest_applicants(
                    applicants_df=adf,
                    current_students_df=df,
                    intl_seats=intl_seats,
                    country_targets_en=country_targets_en,
                )

                accepted_df = results_df[results_df["accepted"]].copy()
                n_total    = len(results_df)
                n_accepted = len(accepted_df)
                acceptance_rate = n_accepted / n_total if n_total else 0.0

                # ── KPIs
                st.markdown("#### النتائج")
                k1, k2, k3, k4 = st.columns(4)
                k1.metric("إجمالي المتقدمين",        f"{n_total:,}")
                k2.metric("المقاعد الدولية المتاحة", f"{intl_seats:,}")
                k3.metric("المقبولون المقترحون",      f"{n_accepted:,}")
                k4.metric("معدل القبول",               f"{acceptance_rate:.1%}")

                # ── Charts
                if not accepted_df.empty:
                    ch1, ch2 = st.columns(2)

                    with ch1:
                        st.markdown("##### المقبولون حسب الجنسية")
                        nat_counts = (
                            accepted_df["mapped_nationality"]
                            .value_counts()
                            .reset_index()
                        )
                        nat_counts.columns = ["الجنسية", "العدد"]
                        fig_nat = px.bar(
                            nat_counts, x="الجنسية", y="العدد",
                            labels={"الجنسية": "الجنسية", "العدد": "العدد"}
                        )
                        fig_nat.update_traces(marker_color="#0d6efd", name="")
                        fig_nat.update_layout(showlegend=False)
                        st.plotly_chart(fig_nat, use_container_width=True)

                    with ch2:
                        st.markdown("##### المقبولون حسب التخصص المُسنَد")
                        disc_chart_counts = (
                            accepted_df["assigned_discipline"]
                            .value_counts()
                            .reset_index()
                        )
                        disc_chart_counts.columns = ["التخصص", "العدد"]
                        fig_disc = px.bar(
                            disc_chart_counts, x="التخصص", y="العدد",
                            labels={"التخصص": "التخصص", "العدد": "العدد"}
                        )
                        fig_disc.update_traces(marker_color="#198754", name="")
                        fig_disc.update_layout(showlegend=False)
                        st.plotly_chart(fig_disc, use_container_width=True)

                # ── Accepted table
                choice_label = {1: "الخيار الأول", 2: "الخيار الثاني", 3: "الخيار الثالث", 0: "—"}
                st.markdown("#### قائمة المقبولين المقترحين")
                show_accepted = accepted_df[[
                    "applicant_id", "nationality", "mapped_nationality",
                    "disc1", "disc2", "disc3",
                    "assigned_discipline", "accepted_at_choice",
                    "acceptance_reason"
                ]].copy()
                show_accepted["accepted_at_choice"] = show_accepted["accepted_at_choice"].map(choice_label)
                show_accepted = show_accepted.rename(columns={
                    "applicant_id":        "رقم المتقدم",
                    "nationality":         "الجنسية (الملف)",
                    "mapped_nationality":  "الجنسية (معيارية)",
                    "disc1":               "التخصص الأول",
                    "disc2":               "التخصص الثاني",
                    "disc3":               "التخصص الثالث",
                    "assigned_discipline": "التخصص المُسنَد",
                    "accepted_at_choice":  "رتبة الخيار",
                    "acceptance_reason":   "سبب القبول",
                })
                st.dataframe(show_accepted, use_container_width=True, hide_index=True)

                # ── Full results table
                st.markdown("#### جدول كامل المتقدمين")
                show_all = results_df[[
                    "applicant_id", "nationality", "mapped_nationality",
                    "disc1", "disc2", "disc3",
                    "geo_score", "accepted",
                    "assigned_discipline", "accepted_at_choice",
                    "acceptance_reason"
                ]].copy()
                show_all["accepted"] = show_all["accepted"].map(
                    {True: "مقبول", False: "غير مقبول"}
                )
                show_all["accepted_at_choice"] = show_all["accepted_at_choice"].map(choice_label)
                show_all = show_all.rename(columns={
                    "applicant_id":        "رقم المتقدم",
                    "nationality":         "الجنسية (الملف)",
                    "mapped_nationality":  "الجنسية (معيارية)",
                    "disc1":               "التخصص الأول",
                    "disc2":               "التخصص الثاني",
                    "disc3":               "التخصص الثالث",
                    "geo_score":           "نقاط التوازن الجغرافي",
                    "accepted":            "الحالة",
                    "assigned_discipline": "التخصص المُسنَد",
                    "accepted_at_choice":  "رتبة الخيار",
                    "acceptance_reason":   "السبب",
                })
                st.dataframe(show_all, use_container_width=True, hide_index=True)

                # ── Download
                csv_out = show_all.to_csv(index=False).encode("utf-8-sig")
                st.download_button(
                    "📥 تنزيل النتائج (CSV)",
                    data=csv_out,
                    file_name="acceptance_plan.csv",
                    mime="text/csv",
                )

    with tab6:
        st.subheader("معدلات القبول المتوقعة للدول — السنوات الخمس القادمة")
        st.caption(
            "يستند الحساب إلى بيانات القبول الفعلية خلال السنوات الخمس الماضية. "
            "أدخل إجمالي المنح لكل سنة وسيتم تقسيمها تلقائياً: 25% منح داخلية و75% منح خارجية. "
            "المنح الخارجية تنقسم إلى مقاعد محجوزة ومقاعد موزعة لتحقيق التوازن."
        )

        # ── Build historical data ───────────────────────────────────────────────
        all_timeline_years = df["timeline_year"].dropna().astype(int)
        if all_timeline_years.empty:
            st.warning("لا توجد بيانات تاريخية كافية لإجراء الحساب.")
        else:
            base_year_fc = int(all_timeline_years.max())
            hist_years_fc = list(range(base_year_fc - 4, base_year_fc + 1))
            forecast_years_fc = [base_year_fc + i for i in range(1, 6)]

            hist_df_fc = df[
                df["timeline_year"].isin(hist_years_fc) & (df["country"] != "غير محدد")
            ].copy()

            # Per-country totals and annual averages over the last 5 years
            country_hist_fc = (
                hist_df_fc.groupby("country")
                .size()
                .reset_index(name="hist_5yr_total")
            )
            country_hist_fc["hist_annual_avg"] = (
                country_hist_fc["hist_5yr_total"] / 5
            ).round(2)
            country_hist_fc = country_hist_fc.sort_values(
                "hist_5yr_total", ascending=False
            ).reset_index(drop=True)

            # Continent lookup and option lists
            cont_lookup_fc = {
                v["country_ar"]: v["continent"]
                for v in NATIONALITY_MAPPING.values()
                if v["country_ar"] != "غير محدد"
            }
            continents_fc = sorted(
                {
                    v["continent"]
                    for v in NATIONALITY_MAPPING.values()
                    if v["continent"] != "غير محدد"
                }
            )
            countries_fc = sorted(
                {
                    v["country_ar"]
                    for v in NATIONALITY_MAPPING.values()
                    if v["country_ar"] != "غير محدد"
                }
            )

            # ── Section 1: Grant configuration ─────────────────────────────────
            st.markdown("### 1) إعداد المنح")
            st.caption(
                "أدخل إجمالي المنح لكل سنة — سيتم توزيعها تلقائياً: "
                "**25% منح داخلية** و **75% منح خارجية**."
            )
            total_yr_cols = st.columns(5)
            total_grants_fc = {}
            for i, yr in enumerate(forecast_years_fc):
                with total_yr_cols[i]:
                    total_grants_fc[yr] = st.number_input(
                        f"إجمالي {yr}هـ",
                        min_value=0,
                        value=52,
                        step=1,
                        key=f"fc_total_yr_{yr}",
                    )

            # Compute the 25 / 75 split for each year
            internal_grants_fc_by_year = {
                yr: round(total_grants_fc[yr] * 0.25) for yr in forecast_years_fc
            }
            external_grants_fc = {
                yr: total_grants_fc[yr] - internal_grants_fc_by_year[yr]
                for yr in forecast_years_fc
            }

            # Use a single representative value for internal grants
            # (shown in the results table; all years share the same formula)
            internal_grants_fc = internal_grants_fc_by_year[forecast_years_fc[0]]

            # Show computed split
            split_cols = st.columns(5)
            for i, yr in enumerate(forecast_years_fc):
                split_cols[i].info(
                    f"داخلي: **{internal_grants_fc_by_year[yr]}**  \n"
                    f"خارجي: **{external_grants_fc[yr]}**"
                )

            st.markdown("---")

            # ── Section 2: Reserved seats ───────────────────────────────────────
            st.markdown("### 2) المقاعد المحجوزة (اختياري)")
            st.caption(
                "أضف حجوزات لدول بعينها أو لمناطق جغرافية (مثال: أمريكا اللاتينية، أفريقيا). "
                "يمكن تحديد المقاعد كعدد ثابت أو كنسبة مئوية من المنح الخارجية. "
                "تُحسم المقاعد المحجوزة من المنح الخارجية ثم يُوزَّع الباقي لتحقيق التوازن."
            )

            if "fc_reservations" not in st.session_state:
                st.session_state.fc_reservations = []

            to_del_fc = None
            region_options_fc = [""] + continents_fc + countries_fc
            for i, res_item in enumerate(st.session_state.fc_reservations):
                res_cols = st.columns([2, 1] + [1] * 5 + [1])
                current_region = res_item.get("region", "")
                sel_idx = (
                    region_options_fc.index(current_region)
                    if current_region in region_options_fc
                    else 0
                )
                chosen_region = res_cols[0].selectbox(
                    f"المنطقة / الدولة {i + 1}",
                    options=region_options_fc,
                    index=sel_idx,
                    key=f"fc_res_region_{i}",
                )
                current_type = res_item.get("seat_type", "flat")
                chosen_type = res_cols[1].selectbox(
                    "النوع",
                    options=["flat", "pct"],
                    format_func=lambda x: "عدد ثابت" if x == "flat" else "نسبة %",
                    index=0 if current_type == "flat" else 1,
                    key=f"fc_res_type_{i}",
                )
                yr_seats_res = {}
                for j, yr in enumerate(forecast_years_fc):
                    yr_seats_res[yr] = res_cols[j + 2].number_input(
                        f"{yr}هـ" if chosen_type == "flat" else f"{yr}هـ (%)",
                        min_value=0,
                        max_value=None if chosen_type == "flat" else 100,
                        value=res_item.get("seats", {}).get(yr, 0),
                        step=1,
                        key=f"fc_res_s_{i}_{yr}",
                    )
                if res_cols[-1].button("حذف", key=f"fc_res_del_{i}"):
                    to_del_fc = i
                st.session_state.fc_reservations[i] = {
                    "region": chosen_region,
                    "seat_type": chosen_type,
                    "seats": yr_seats_res,
                }

            if to_del_fc is not None:
                st.session_state.fc_reservations.pop(to_del_fc)
                st.rerun()

            if st.button("+ أضف حجز", key="fc_add_res"):
                st.session_state.fc_reservations.append(
                    {"region": "", "seat_type": "flat", "seats": {yr: 0 for yr in forecast_years_fc}}
                )
                st.rerun()

            # Warn if reservations exceed external grants in any year
            for yr in forecast_years_fc:
                total_res_yr = sum(
                    round(res.get("seats", {}).get(yr, 0) / 100 * external_grants_fc[yr])
                    if res.get("seat_type") == "pct"
                    else res.get("seats", {}).get(yr, 0)
                    for res in st.session_state.fc_reservations
                    if res.get("region")
                )
                if total_res_yr > external_grants_fc[yr]:
                    st.warning(
                        f"إجمالي المقاعد المحجوزة ({total_res_yr}) "
                        f"يتجاوز المنح الخارجية ({external_grants_fc[yr]}) لسنة {yr}هـ."
                    )

            st.markdown("---")

            # ── Section 3: Results table ────────────────────────────────────────
            st.markdown("### 3) جدول توزيع المنح")
            st.caption(
                "نسبة التوزيع = حصة المنطقة / الدولة من إجمالي المنح الخارجية لتلك السنة."
            )

            table_rows_fc = []

            # Row: Internal grants
            int_row_fc = {
                "الدولة / المنطقة": "🏫 المنح الداخلية",
                "النوع": "داخلي",
            }
            for yr in forecast_years_fc:
                int_row_fc[f"مقاعد {yr}هـ"] = internal_grants_fc_by_year[yr]
                int_row_fc[f"نسبة التوزيع {yr}هـ"] = "—"
            table_rows_fc.append(int_row_fc)

            # Row: External grants total
            ext_total_row_fc = {
                "الدولة / المنطقة": "🌐 إجمالي المنح الخارجية",
                "النوع": "خارجي (إجمالي)",
            }
            for yr in forecast_years_fc:
                ext_total_row_fc[f"مقاعد {yr}هـ"] = external_grants_fc[yr]
                ext_total_row_fc[f"نسبة التوزيع {yr}هـ"] = "100%"
            table_rows_fc.append(ext_total_row_fc)

            # Rows: one per reservation entry
            valid_reservations_fc = [
                r for r in st.session_state.fc_reservations if r.get("region")
            ]
            for res in valid_reservations_fc:
                region_label = res["region"]
                res_row = {
                    "الدولة / المنطقة": f"📌 {region_label}",
                    "النوع": "محجوز",
                }
                for yr in forecast_years_fc:
                    raw = res.get("seats", {}).get(yr, 0)
                    ext_yr = external_grants_fc[yr]
                    if res.get("seat_type") == "pct":
                        seats = round(raw / 100 * ext_yr)
                        res_row[f"مقاعد {yr}هـ"] = f"{seats} ({raw}%)"
                    else:
                        seats = raw
                        res_row[f"مقاعد {yr}هـ"] = seats
                    res_row[f"نسبة التوزيع {yr}هـ"] = (
                        f"{seats / ext_yr:.1%}" if ext_yr > 0 else "—"
                    )
                table_rows_fc.append(res_row)

            # Row: "Other" — remaining external seats after reservations
            other_row_fc = {
                "الدولة / المنطقة": "🌍 أخرى (توزيع متوازن)",
                "النوع": "توازن",
            }
            for yr in forecast_years_fc:
                ext_yr = external_grants_fc[yr]
                reserved_total_yr = sum(
                    round(r.get("seats", {}).get(yr, 0) / 100 * ext_yr)
                    if r.get("seat_type") == "pct"
                    else r.get("seats", {}).get(yr, 0)
                    for r in valid_reservations_fc
                )
                other_seats = max(0, ext_yr - reserved_total_yr)
                other_row_fc[f"مقاعد {yr}هـ"] = other_seats
                other_row_fc[f"نسبة التوزيع {yr}هـ"] = (
                    f"{other_seats / ext_yr:.1%}" if ext_yr > 0 else "—"
                )
            table_rows_fc.append(other_row_fc)

            result_table_fc = pd.DataFrame(table_rows_fc)
            st.dataframe(result_table_fc, use_container_width=True, hide_index=True)

            # ── Summary metrics per year ────────────────────────────────────────
            st.markdown("#### ملخص المنح لكل سنة")
            sum_cols = st.columns(5)
            for i, yr in enumerate(forecast_years_fc):
                grand_total = internal_grants_fc_by_year[yr] + external_grants_fc[yr]
                sum_cols[i].metric(
                    label=f"{yr}هـ",
                    value=f"{grand_total} منحة",
                    delta=f"{external_grants_fc[yr]} خارجي",
                )

            # ── Bar chart: reserved areas + Other for year 1 ───────────────────
            yr1_fc = forecast_years_fc[0]
            chart_rows_fc = []
            for res in valid_reservations_fc:
                raw = res.get("seats", {}).get(yr1_fc, 0)
                ext_yr1 = external_grants_fc[yr1_fc]
                seats = round(raw / 100 * ext_yr1) if res.get("seat_type") == "pct" else raw
                if seats > 0:
                    chart_rows_fc.append(
                        {"المنطقة": res["region"], "المقاعد": seats}
                    )
            reserved_total_yr1 = sum(
                round(r.get("seats", {}).get(yr1_fc, 0) / 100 * external_grants_fc[yr1_fc])
                if r.get("seat_type") == "pct"
                else r.get("seats", {}).get(yr1_fc, 0)
                for r in valid_reservations_fc
            )
            other_yr1 = max(0, external_grants_fc[yr1_fc] - reserved_total_yr1)
            if other_yr1 > 0:
                chart_rows_fc.append({"المنطقة": "أخرى", "المقاعد": other_yr1})

            chart_data_fc = pd.DataFrame(chart_rows_fc).sort_values(
                "المقاعد", ascending=False
            )

            if not chart_data_fc.empty:
                st.markdown(
                    f"#### توزيع المقاعد الخارجية — {yr1_fc}هـ"
                )
                fig_fc = px.bar(
                    chart_data_fc,
                    x="المنطقة",
                    y="المقاعد",
                    color="المقاعد",
                    color_continuous_scale="Blues",
                    labels={"المنطقة": "المنطقة / الدولة", "المقاعد": "المقاعد المخصصة"},
                )
                fig_fc.update_layout(
                    showlegend=False, coloraxis_showscale=False
                )
                st.plotly_chart(format_plot(fig_fc), use_container_width=True)

            # ── Download ────────────────────────────────────────────────────────
            csv_fc = result_table_fc.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 تنزيل جدول التوزيع (CSV)",
                data=csv_fc,
                file_name="acceptance_forecast.csv",
                mime="text/csv",
                key="fc_download_btn",
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
            # GPA Distribution by College
            st.subheader("توزيع المعدل التراكمي حسب الكلية")
            fig_gpa_box = px.box(
                filtered_df,
                x='college',
                y='gpa',
                labels={'gpa': 'المعدل التراكمي', 'college': 'الكلية'}
            )
            fig_gpa_box.update_traces(marker_color='#0d6efd')
            fig_gpa_box.update_layout(showlegend=False)
            st.plotly_chart(format_plot(fig_gpa_box), use_container_width=True)

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
        csv = display_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="📥 تحميل البيانات كملف CSV",
            data=csv,
            file_name=f"international_students_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
