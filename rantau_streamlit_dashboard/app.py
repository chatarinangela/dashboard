import streamlit as st
import pandas as pd
import plotly.express as px

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Rantau Connect Dashboard",
    page_icon="📊",
    layout="wide"
)

# =============================
# STYLING
# =============================
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #e5e7eb;
        border-radius: 16px;
        padding: 18px;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }
    .metric-value {
        font-size: 30px;
        font-weight: 700;
        color: #1f2937;
    }
    .metric-label {
        font-size: 14px;
        color: #6b7280;
    }
</style>
""", unsafe_allow_html=True)

# =============================
# LOAD DATA
# =============================
FILE_PATH = "Rantau Connect - PPI United Kingdom 2025_2026 (Responses).xlsx"

@st.cache_data
def load_data(file_path):
    df = pd.read_excel(file_path, sheet_name="Form responses 1")

    # Clean column names
    df.columns = (
        df.columns
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )

    # Rename long / repeated columns into cleaner names
    rename_map = {
        "University in the UK": "University",
        "If Other, please specify your university": "Other University",
        "Post-Graduation Pathway": "STEM Post-Graduation Pathway",
        "Industry Interest": "STEM Industry Interest",
        "Career Track Preference": "STEM Career Track Preference",
        "Location Intent": "STEM Location Intent",
        "Health & Medicine Sub-Field": "Health Sub-Field",
        "Professional Track": "Health Professional Track",
        "Intended Country of Practice": "Health Intended Country of Practice",
        "Sector Interest": "Health Sector Interest",
        "Social Studies Sub-Field": "Social Studies Sub-Field",
        "Intended Career Pathway": "Social Studies Career Pathway",
        "Sector Interest 2": "Social Studies Sector Interest",
        "Arts & Humanities Sub-Field": "Arts Sub-Field",
        "Intended Career Pathway 2": "Arts Career Pathway",
        "Portfolio-Based Career": "Arts Portfolio-Based Career",
        "Intended Country of Work 2": "Arts Intended Country of Work",
        "LinkedIn Profile URL (Optional)": "LinkedIn URL",
        "Alumni Involvement Interest": "Alumni Involvement Interest",
        'Feedback Do you have any feedback or suggestions for PPI UK? (Optional, please answer "-" if you do not have one)': "Feedback",
        "According to UU No. 8 of 2016 regarding Persons with Disabilities in Indonesia, disability is defined as a unique condition that stems from the interaction of physical, intellectual, mental, and sensory limitations. These limitations can impede an individual's ability to participate fully and effectively in social and economic activities. Do you have any accessibility requirements that PPI UK should be aware of?": "Accessibility Requirement",
        "If yes, please specify your accessibility requirements (Optional)": "Accessibility Details",
        "Networking Consent Are you open to being contacted for professional networking and alumni-related opportunities?": "Networking Consent"
    }

    df = df.rename(columns={k: v for k, v in rename_map.items() if k in df.columns})

    if "Timestamp" in df.columns:
        df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")

    return df

try:
    df = load_data(FILE_PATH)
except FileNotFoundError:
    st.error(
        "Excel file not found. Please place the Excel file in the same folder as app.py, "
        "or upload it using the uploader below."
    )
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])
    if uploaded_file is not None:
        df = load_data(uploaded_file)
    else:
        st.stop()

# =============================
# HELPER FUNCTIONS
# =============================
def clean_series(series):
    return (
        series.dropna()
        .astype(str)
        .str.strip()
        .replace(["", "-", "nan", "None"], pd.NA)
        .dropna()
    )


def split_multi_select(series):
    return (
        clean_series(series)
        .str.split(",")
        .explode()
        .str.strip()
        .replace("", pd.NA)
        .dropna()
    )


def count_values(df, column, label=None, multi=False, top_n=None):
    if column not in df.columns:
        return pd.DataFrame(columns=[label or column, "Count"])

    s = split_multi_select(df[column]) if multi else clean_series(df[column])
    out = s.value_counts().reset_index()
    out.columns = [label or column, "Count"]
    out = out.sort_values("Count", ascending=False)

    if top_n:
        out = out.head(top_n)

    return out


def plot_bar(data, x, y="Count", title="", horizontal=False, color=None):
    if data.empty:
        st.info(f"No data available for {title}.")
        return

    # Always show bars from biggest to smallest
    data = data.sort_values(y, ascending=False).copy()

    if horizontal:
        fig = px.bar(data, x=y, y=x, text=y, orientation="h", color=color, title=title)
        fig.update_yaxes(categoryorder="array", categoryarray=data[x].tolist(), autorange="reversed")
    else:
        fig = px.bar(data, x=x, y=y, text=y, color=color, title=title)
        fig.update_xaxes(categoryorder="array", categoryarray=data[x].tolist())

    fig.update_layout(
        title_font_size=20,
        title_x=0.02,
        height=460,
        margin=dict(l=20, r=20, t=60, b=30),
        xaxis_title=None,
        yaxis_title=None,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig, use_container_width=True)


def plot_donut(data, names, values="Count", title=""):
    if data.empty:
        st.info(f"No data available for {title}.")
        return

    fig = px.pie(data, names=names, values=values, hole=0.45, title=title)
    fig.update_layout(
        title_font_size=20,
        title_x=0.02,
        height=460,
        margin=dict(l=20, r=20, t=60, b=30),
    )
    st.plotly_chart(fig, use_container_width=True)


def metric_card(label, value):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-value">{value}</div>
            <div class="metric-label">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =============================
# HEADER
# =============================
st.title("📊 Rantau Connect Dashboard")
st.caption("PPI United Kingdom 2025/2026 Form Responses")

# =============================
# SIDEBAR FILTERS
# =============================
st.sidebar.header("Dashboard Filters")

filtered_df = df.copy()

if "Field of Study" in df.columns:
    field_options = sorted(clean_series(df["Field of Study"]).unique())
    selected_fields = st.sidebar.multiselect(
        "Field of Study",
        field_options,
        default=field_options
    )
    filtered_df = filtered_df[filtered_df["Field of Study"].isin(selected_fields)]

if "Level of Study" in df.columns:
    level_options = sorted(clean_series(df["Level of Study"]).unique())
    selected_levels = st.sidebar.multiselect(
        "Level of Study",
        level_options,
        default=level_options
    )
    filtered_df = filtered_df[filtered_df["Level of Study"].isin(selected_levels)]

if "Graduation Year" in df.columns:
    grad_options = sorted(clean_series(df["Graduation Year"].astype(str)).unique())
    selected_grads = st.sidebar.multiselect(
        "Graduation Year",
        grad_options,
        default=grad_options
    )
    filtered_df = filtered_df[filtered_df["Graduation Year"].astype(str).isin(selected_grads)]

# =============================
# KPI CARDS
# =============================
c1, c2, c3, c4 = st.columns(4)
with c1:
    metric_card("Total Responses", len(filtered_df))
with c2:
    metric_card("Universities", filtered_df["University"].nunique() if "University" in filtered_df.columns else "N/A")
with c3:
    metric_card("Fields of Study", filtered_df["Field of Study"].nunique() if "Field of Study" in filtered_df.columns else "N/A")
with c4:
    metric_card("Graduation Years", filtered_df["Graduation Year"].nunique() if "Graduation Year" in filtered_df.columns else "N/A")

st.markdown("---")

# =============================
# TABS
# =============================
tab1, tab2, tab3, tab4 = st.tabs([
    "Overview",
    "Study Profile",
    "Career Interests",
    "Community & Accessibility"
])

# =============================
# TAB 1: OVERVIEW
# =============================
with tab1:
    st.subheader("Overall Overview")

    col1, col2 = st.columns(2)

    with col1:
        field_counts = count_values(filtered_df, "Field of Study", "Field of Study")
        plot_donut(field_counts, "Field of Study", title="Field of Study Distribution")

    with col2:
        level_counts = count_values(filtered_df, "Level of Study", "Level of Study")
        plot_bar(level_counts, "Level of Study", title="Level of Study Distribution")

    col3, col4 = st.columns(2)

    with col3:
        grad_counts = count_values(filtered_df, "Graduation Year", "Graduation Year")
        plot_bar(grad_counts, "Graduation Year", title="Graduation Year Distribution")

    with col4:
        uni_counts = count_values(filtered_df, "University", "University", top_n=12)
        plot_bar(uni_counts, "University", title="Top 12 Universities", horizontal=True)

# =============================
# TAB 2: STUDY PROFILE
# =============================
with tab2:
    st.subheader("Academic and Study Profile")

    col1, col2 = st.columns(2)

    with col1:
        funding_counts = count_values(filtered_df, "Funding Sources", "Funding Source", multi=True)
        plot_bar(funding_counts, "Funding Source", title="Funding Sources", horizontal=True)

    with col2:
        if {"Graduation Year", "Field of Study"}.issubset(filtered_df.columns):
            grouped = (
                filtered_df
                .dropna(subset=["Graduation Year", "Field of Study"])
                .groupby(["Graduation Year", "Field of Study"])
                .size()
                .reset_index(name="Count")
            )
            fig = px.bar(
                grouped,
                x="Graduation Year",
                y="Count",
                color="Field of Study",
                barmode="group",
                title="Field of Study by Graduation Year"
            )
            fig.update_layout(height=460, title_font_size=20, title_x=0.02)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Sub-Field Breakdown")
    subfield_cols = [
        ("STEM Sub-Field", "STEM Sub-Field"),
        ("Health Sub-Field", "Health & Medicine Sub-Field"),
        ("Social Studies Sub-Field", "Social Studies Sub-Field"),
        ("Arts Sub-Field", "Arts & Humanities Sub-Field"),
    ]

    sub1, sub2 = st.columns(2)
    for i, (col, label) in enumerate(subfield_cols):
        target = sub1 if i % 2 == 0 else sub2
        with target:
            counts = count_values(filtered_df, col, label)
            plot_bar(counts, label, title=label, horizontal=True)

# =============================
# TAB 3: CAREER INTERESTS
# =============================
with tab3:
    st.subheader("Career Interests")

    col1, col2 = st.columns(2)

    with col1:
        counts = count_values(filtered_df, "STEM Industry Interest", "Industry Interest", multi=True)
        plot_bar(counts, "Industry Interest", title="STEM Industry Interests", horizontal=True)

    with col2:
        counts = count_values(filtered_df, "STEM Career Track Preference", "Career Track", multi=True)
        plot_bar(counts, "Career Track", title="STEM Career Track Preferences", horizontal=True)

    col3, col4 = st.columns(2)

    with col3:
        counts = count_values(filtered_df, "Health Professional Track", "Professional Track", multi=True)
        plot_bar(counts, "Professional Track", title="Health & Medicine Professional Tracks", horizontal=True)

    with col4:
        counts = count_values(filtered_df, "Health Sector Interest", "Sector Interest", multi=True)
        plot_bar(counts, "Sector Interest", title="Health & Medicine Sector Interests", horizontal=True)

    col5, col6 = st.columns(2)

    with col5:
        counts = count_values(filtered_df, "Social Studies Career Pathway", "Career Pathway")
        plot_bar(counts, "Career Pathway", title="Social Studies Career Pathways", horizontal=True)

    with col6:
        counts = count_values(filtered_df, "Arts Career Pathway", "Career Pathway")
        plot_bar(counts, "Career Pathway", title="Arts & Humanities Career Pathways", horizontal=True)

# =============================
# TAB 4: COMMUNITY & ACCESSIBILITY
# =============================
with tab4:
    st.subheader("Community, Networking, and Accessibility")

    col1, col2 = st.columns(2)

    with col1:
        counts = count_values(filtered_df, "Networking Consent", "Networking Consent")
        plot_donut(counts, "Networking Consent", title="Networking Consent")

    with col2:
        counts = count_values(
            filtered_df,
            "Accessibility Requirement",
            "Accessibility Requirement"
        )
        plot_bar(counts, "Accessibility Requirement", title="Accessibility Requirements", horizontal=True)

    st.markdown("### Alumni Involvement Interest")
    alumni_counts = count_values(
        filtered_df,
        "Alumni Involvement Interest",
        "Alumni Involvement Interest",
        multi=True
    )
    plot_bar(
        alumni_counts,
        "Alumni Involvement Interest",
        title="Alumni Involvement Interest",
        horizontal=True
    )
