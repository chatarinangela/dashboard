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

    if top_n:
        out = out.head(top_n)

    return out


def plot_bar(data, x, y="Count", title="", horizontal=False, color=None):
    if data.empty:
        st.info(f"No data available for {title}.")
        return

    if horizontal:
        fig = px.bar(data, x=y, y=x, text=y, orientation="h", color=color, title=title)
    else:
        fig = px.bar(data, x=x, y=y, text=y, color=color, title=title)

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
    fig.update_traces(textposition="outside")
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
    st.caption("This section summarises contact permissions, alumni support interests, accessibility needs, and qualitative feedback.")

    # Top KPI summary for community section
    net_yes = 0
    if "Networking Consent" in filtered_df.columns:
        net_yes = clean_series(filtered_df["Networking Consent"]).str.lower().eq("yes").sum()

    alumni_responses = 0
    if "Alumni Involvement Interest" in filtered_df.columns:
        alumni_responses = clean_series(filtered_df["Alumni Involvement Interest"]).shape[0]

    accessibility_responses = 0
    if "Accessibility Requirement" in filtered_df.columns:
        accessibility_responses = clean_series(filtered_df["Accessibility Requirement"]).shape[0]

    feedback_count = 0
    if "Feedback" in filtered_df.columns:
        feedback_count = clean_series(filtered_df["Feedback"]).shape[0]

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        metric_card("Open to Networking", net_yes)
    with m2:
        metric_card("Alumni Interest Responses", alumni_responses)
    with m3:
        metric_card("Accessibility Responses", accessibility_responses)
    with m4:
        metric_card("Feedback Responses", feedback_count)

    st.markdown("---")

    # Row 1: networking and alumni involvement
    col1, col2 = st.columns([1, 1.5])

    with col1:
        counts = count_values(filtered_df, "Networking Consent", "Networking Consent")
        plot_donut(counts, "Networking Consent", title="Networking Consent")

    with col2:
        # Multi-select answers should be split so the chart is readable
        counts = count_values(
            filtered_df,
            "Alumni Involvement Interest",
            "Alumni Involvement Interest",
            multi=True,
            top_n=12
        )
        plot_bar(
            counts,
            "Alumni Involvement Interest",
            title="Top Alumni Involvement Interests",
            horizontal=True
        )

    # Row 2: accessibility and feedback
    col3, col4 = st.columns([1, 1.5])

    with col3:
        counts = count_values(filtered_df, "Accessibility Requirement", "Accessibility Requirement")
        plot_bar(
            counts,
            "Accessibility Requirement",
            title="Accessibility Requirement Summary",
            horizontal=True
        )

    with col4:
        st.markdown("### Feedback Themes")
        if "Feedback" not in filtered_df.columns:
            st.info("No feedback column found.")
        else:
            feedback = clean_series(filtered_df["Feedback"])
            feedback = feedback[~feedback.str.lower().isin(["no", "none", "n/a", "na"])]

            if feedback.empty:
                st.info("No detailed feedback responses available.")
            else:
                for i, response in enumerate(feedback.head(10), start=1):
                    with st.expander(f"Feedback {i}"):
                        st.write(response)

                if len(feedback) > 10:
                    st.caption(f"Showing first 10 of {len(feedback)} detailed feedback responses.")

    st.markdown("---")
    st.info(
        "Raw response data has been removed from the dashboard view to keep the website cleaner and protect respondent privacy."
    )
