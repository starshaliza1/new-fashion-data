"""
Fashion Insights Dashboard
A comprehensive Streamlit dashboard for exploring the fashion recommendation dataset.
Run with: streamlit run app.py
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Directory this script lives in — used to build a path that works regardless
# of the working directory the app is launched from (this trips up Streamlit
# Cloud in particular, since it doesn't always run from the repo root).
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(APP_DIR, "data", "fashion_dataset_complete.csv")

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Fashion Insights Dashboard",
    page_icon="👗",
    layout="wide",
    initial_sidebar_state="expanded",
)

PRIMARY = "#B8336A"
ACCENT = "#5C4B99"
PALETTE = ["#B8336A", "#5C4B99", "#E88C7D", "#3E7CB1", "#F2C14E", "#57A773", "#8E7DBE", "#D4A5A5"]

px.defaults.color_discrete_sequence = PALETTE
px.defaults.template = "plotly_white"

# ----------------------------------------------------------------------------
# DATA LOADING
# ----------------------------------------------------------------------------
@st.cache_data
def load_data(path: str = DATA_PATH) -> pd.DataFrame:
    if not os.path.exists(path):
        st.error(
            f"Couldn't find the data file at `{path}`.\n\n"
            "Make sure the `data/fashion_dataset_complete.csv` file was uploaded "
            "alongside `app.py` (same folder structure as the zip you downloaded)."
        )
        st.stop()
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["month_name"] = df["timestamp"].dt.month_name()
    df["week"] = df["timestamp"].dt.isocalendar().week
    df["engagement"] = df["views"] + df["likes"] * 2 + df["shares"] * 3 + df["saves"] * 2
    df["engagement_rate"] = (df["likes"] + df["shares"] + df["saves"]) / df["views"].replace(0, np.nan)
    df["purchased_label"] = df["purchased"].map({1: "Purchased", 0: "Not purchased"})
    return df

df_raw = load_data()

# ----------------------------------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------------------------------
st.sidebar.title("👗 Filters")
st.sidebar.caption(f"{len(df_raw):,} sessions in the full dataset")

def multiselect_filter(label, col, default_all=True):
    options = sorted(df_raw[col].dropna().unique().tolist())
    return st.sidebar.multiselect(label, options, default=options if default_all else [])

with st.sidebar.expander("Date range", expanded=True):
    min_d, max_d = df_raw["timestamp"].min().date(), df_raw["timestamp"].max().date()
    date_range = st.date_input("Session date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)

with st.sidebar.expander("Demographics", expanded=True):
    genders = multiselect_filter("Gender", "gender")
    ages = multiselect_filter("Age group", "age_group")
    body_types = multiselect_filter("Body type", "body_type")

with st.sidebar.expander("Product & Style"):
    styles = multiselect_filter("Style preference", "style_preference")
    clothing_types = multiselect_filter("Clothing type", "clothing_type")
    brands = multiselect_filter("Brand", "preferred_brand")
    budgets = multiselect_filter("Budget level", "budget_level")

with st.sidebar.expander("Context"):
    occasions = multiselect_filter("Occasion", "occasion")
    seasons = multiselect_filter("Season", "season")

price_min, price_max = float(df_raw.price_usd.min()), float(df_raw.price_usd.max())
price_sel = st.sidebar.slider("Price range (USD)", price_min, price_max, (price_min, price_max))

purchased_filter = st.sidebar.radio("Purchase status", ["All", "Purchased only", "Not purchased only"], index=0)

if st.sidebar.button("Reset all filters"):
    st.rerun()

# Apply filters
mask = (
    df_raw["gender"].isin(genders)
    & df_raw["age_group"].isin(ages)
    & df_raw["body_type"].isin(body_types)
    & df_raw["style_preference"].isin(styles)
    & df_raw["clothing_type"].isin(clothing_types)
    & df_raw["preferred_brand"].isin(brands)
    & df_raw["budget_level"].isin(budgets)
    & df_raw["occasion"].isin(occasions)
    & df_raw["season"].isin(seasons)
    & df_raw["price_usd"].between(price_sel[0], price_sel[1])
)

if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    mask &= df_raw["timestamp"].dt.date.between(start, end)

if purchased_filter == "Purchased only":
    mask &= df_raw["purchased"] == 1
elif purchased_filter == "Not purchased only":
    mask &= df_raw["purchased"] == 0

df = df_raw[mask].copy()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.title("👗 Fashion Insights Dashboard")
st.caption("Exploring style preferences, engagement, and purchase behavior across fashion recommendation sessions")

if df.empty:
    st.warning("No data matches the current filter selection. Try widening your filters in the sidebar.")
    st.stop()

st.markdown(f"**Showing {len(df):,} of {len(df_raw):,} sessions** ({len(df)/len(df_raw):.1%} of dataset)")

tab_overview, tab_demo, tab_style, tab_engagement, tab_purchase, tab_explorer = st.tabs(
    ["📊 Overview", "🧑‍🤝‍🧑 Demographics", "👚 Style & Product", "📈 Engagement", "💰 Purchase Behavior", "🔍 Data Explorer"]
)

# ----------------------------------------------------------------------------
# TAB 1 — OVERVIEW
# ----------------------------------------------------------------------------
with tab_overview:
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total sessions", f"{len(df):,}")
    c2.metric("Unique users", f"{df['user_id'].nunique():,}")
    c3.metric("Avg. price", f"${df['price_usd'].mean():,.2f}")
    c4.metric("Purchase rate", f"{df['purchased'].mean():.1%}")
    c5.metric("Avg. satisfaction", f"{df['satisfaction_score'].mean():.2f} / 1.0")

    c6, c7, c8, c9, c10 = st.columns(5)
    c6.metric("Avg. trend score", f"{df['trend_score'].mean():.2f}")
    c7.metric("Avg. comfort score", f"{df['comfort_score'].mean():.2f}")
    c8.metric("Avg. sustainability", f"{df['sustainability_score'].mean():.2f}")
    c9.metric("Avg. quality score", f"{df['quality_score'].mean():.2f}")
    c10.metric("Avg. fit score", f"{df['fit_score'].mean():.2f}")

    st.divider()

    col_a, col_b = st.columns([2, 1])
    with col_a:
        st.subheader("Sessions over time")
        daily = df.set_index("timestamp").resample("W")["user_id"].count().reset_index(name="sessions")
        fig = px.area(daily, x="timestamp", y="sessions")
        fig.update_layout(height=350, xaxis_title="Week", yaxis_title="Sessions")
        st.plotly_chart(fig, use_container_width=True)
    with col_b:
        st.subheader("Recommendation priority")
        prio = df["recommendation_priority"].value_counts().reset_index()
        prio.columns = ["priority", "count"]
        order = ["Top Priority", "High", "Medium", "Low"]
        prio["priority"] = pd.Categorical(prio["priority"], categories=order, ordered=True)
        prio = prio.sort_values("priority")
        fig = px.pie(prio, names="priority", values="count", hole=0.5)
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    col_c, col_d = st.columns(2)
    with col_c:
        st.subheader("Score correlations")
        score_cols = ["satisfaction_score", "trend_score", "comfort_score", "sustainability_score",
                      "quality_score", "fit_score", "total_score"]
        corr = df[score_cols].corr()
        fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1, aspect="auto")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    with col_d:
        st.subheader("Total score distribution")
        fig = px.histogram(df, x="total_score", nbins=40, color="purchased_label",
                            barmode="overlay", opacity=0.65)
        fig.update_layout(height=400, xaxis_title="Total score", yaxis_title="Sessions")
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 2 — DEMOGRAPHICS
# ----------------------------------------------------------------------------
with tab_demo:
    st.subheader("Who is engaging with the platform?")

    col1, col2 = st.columns(2)
    with col1:
        g = df["gender"].value_counts().reset_index()
        g.columns = ["gender", "count"]
        fig = px.bar(g, x="gender", y="count", color="gender", text="count")
        fig.update_layout(height=350, showlegend=False, title="Gender distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        a = df["age_group"].value_counts().reset_index()
        a.columns = ["age_group", "count"]
        order = ["18-24", "25-34", "35-44", "45-54", "55+"]
        a["age_group"] = pd.Categorical(a["age_group"], categories=order, ordered=True)
        a = a.sort_values("age_group")
        fig = px.bar(a, x="age_group", y="count", color="age_group", text="count")
        fig.update_layout(height=350, showlegend=False, title="Age group distribution")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        bt = df["body_type"].value_counts().reset_index()
        bt.columns = ["body_type", "count"]
        fig = px.bar(bt.sort_values("count"), x="count", y="body_type", orientation="h",
                     color="body_type", text="count")
        fig.update_layout(height=350, showlegend=False, title="Body type distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        st_tone = df["skin_tone"].value_counts().reset_index()
        st_tone.columns = ["skin_tone", "count"]
        fig = px.bar(st_tone.sort_values("count"), x="count", y="skin_tone", orientation="h",
                     color="skin_tone", text="count")
        fig.update_layout(height=350, showlegend=False, title="Skin tone distribution")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Satisfaction & purchase rate by segment")
    seg_choice = st.selectbox("Segment by", ["gender", "age_group", "body_type", "skin_tone", "height"])
    seg = df.groupby(seg_choice, observed=True).agg(
        sessions=("user_id", "count"),
        avg_satisfaction=("satisfaction_score", "mean"),
        purchase_rate=("purchased", "mean"),
        avg_price=("price_usd", "mean"),
    ).reset_index().sort_values("sessions", ascending=False)

    fig = go.Figure()
    fig.add_trace(go.Bar(x=seg[seg_choice], y=seg["purchase_rate"], name="Purchase rate", marker_color=PRIMARY, yaxis="y"))
    fig.add_trace(go.Scatter(x=seg[seg_choice], y=seg["avg_satisfaction"], name="Avg satisfaction",
                              mode="lines+markers", marker_color=ACCENT, yaxis="y2"))
    fig.update_layout(
        height=420,
        yaxis=dict(title="Purchase rate", tickformat=".0%"),
        yaxis2=dict(title="Avg satisfaction", overlaying="y", side="right", range=[0, 1]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(seg.style.format({"avg_satisfaction": "{:.2f}", "purchase_rate": "{:.1%}", "avg_price": "${:.2f}"}),
                 use_container_width=True, hide_index=True)

# ----------------------------------------------------------------------------
# TAB 3 — STYLE & PRODUCT
# ----------------------------------------------------------------------------
with tab_style:
    st.subheader("Style preferences & product attributes")

    col1, col2 = st.columns(2)
    with col1:
        sp = df["style_preference"].value_counts().reset_index()
        sp.columns = ["style", "count"]
        fig = px.bar(sp.sort_values("count"), x="count", y="style", orientation="h", color="style", text="count")
        fig.update_layout(height=380, showlegend=False, title="Style preference popularity")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        ct = df["clothing_type"].value_counts().reset_index()
        ct.columns = ["type", "count"]
        fig = px.bar(ct.sort_values("count"), x="count", y="type", orientation="h", color="type", text="count")
        fig.update_layout(height=380, showlegend=False, title="Clothing type popularity")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        clr = df["primary_color"].value_counts().reset_index()
        clr.columns = ["color", "count"]
        fig = px.bar(clr.sort_values("count"), x="count", y="color", orientation="h", color="color", text="count")
        fig.update_layout(height=420, showlegend=False, title="Primary color popularity")
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        br = df["preferred_brand"].value_counts().reset_index()
        br.columns = ["brand", "count"]
        fig = px.bar(br.sort_values("count"), x="count", y="brand", orientation="h", color="brand", text="count")
        fig.update_layout(height=420, showlegend=False, title="Brand popularity")
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Style preference vs. occasion heatmap")
    heat = pd.crosstab(df["style_preference"], df["occasion"])
    fig = px.imshow(heat, text_auto=True, aspect="auto", color_continuous_scale="Purples")
    fig.update_layout(height=450)
    st.plotly_chart(fig, use_container_width=True)

    col5, col6 = st.columns(2)
    with col5:
        st.subheader("Fabric distribution")
        fb = df["fabric"].value_counts().reset_index()
        fb.columns = ["fabric", "count"]
        fig = px.pie(fb, names="fabric", values="count", hole=0.4)
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)
    with col6:
        st.subheader("Price by budget level")
        fig = px.box(df, x="budget_level", y="price_usd", color="budget_level",
                     category_orders={"budget_level": ["Budget", "Mid-range", "Premium", "Luxury"]})
        fig.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 4 — ENGAGEMENT
# ----------------------------------------------------------------------------
with tab_engagement:
    st.subheader("Engagement metrics")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Avg. views", f"{df['views'].mean():.1f}")
    c2.metric("Avg. likes", f"{df['likes'].mean():.1f}")
    c3.metric("Avg. shares", f"{df['shares'].mean():.1f}")
    c4.metric("Avg. saves", f"{df['saves'].mean():.1f}")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Views vs. Likes")
        sample = df.sample(min(2000, len(df)), random_state=42)
        fig = px.scatter(sample, x="views", y="likes", color="purchased_label", opacity=0.5,
                          trendline="ols" if len(sample) < 5000 else None)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Engagement by clothing type")
        eng = df.groupby("clothing_type", observed=True)[["views", "likes", "shares", "saves"]].mean().reset_index()
        eng_melt = eng.melt(id_vars="clothing_type", var_name="metric", value_name="avg_value")
        fig = px.bar(eng_melt, x="clothing_type", y="avg_value", color="metric", barmode="group")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Try-on count distribution")
        fig = px.histogram(df, x="tryon_count", nbins=20, color="purchased_label", barmode="overlay", opacity=0.65)
        fig.update_layout(height=380)
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        st.subheader("Engagement score by mood")
        mood_eng = df.groupby("mood", observed=True)["engagement"].mean().reset_index().sort_values("engagement")
        fig = px.bar(mood_eng, x="engagement", y="mood", orientation="h", color="mood")
        fig.update_layout(height=380, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Monthly trend & comfort scores")
    monthly = df.groupby(df["timestamp"].dt.to_period("M").astype(str)).agg(
        trend_score=("trend_score", "mean"),
        comfort_score=("comfort_score", "mean"),
        sessions=("user_id", "count"),
    ).reset_index().rename(columns={"timestamp": "month"})
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["trend_score"], name="Trend score", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=monthly["month"], y=monthly["comfort_score"], name="Comfort score", mode="lines+markers"))
    fig.update_layout(height=380, yaxis_title="Score", legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 5 — PURCHASE BEHAVIOR
# ----------------------------------------------------------------------------
with tab_purchase:
    st.subheader("What drives a purchase?")

    c1, c2, c3 = st.columns(3)
    c1.metric("Overall purchase rate", f"{df['purchased'].mean():.1%}")
    c2.metric("Purchases in view", f"{int(df['purchased'].sum()):,}")
    c3.metric("Avg. price (purchased)", f"${df.loc[df.purchased==1,'price_usd'].mean():,.2f}" if df.purchased.sum() else "N/A")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Purchase rate by budget level")
        pr = df.groupby("budget_level", observed=True)["purchased"].mean().reset_index()
        order = ["Budget", "Mid-range", "Premium", "Luxury"]
        pr["budget_level"] = pd.Categorical(pr["budget_level"], categories=order, ordered=True)
        pr = pr.sort_values("budget_level")
        fig = px.bar(pr, x="budget_level", y="purchased", color="budget_level", text_auto=".1%")
        fig.update_layout(height=380, showlegend=False, yaxis_tickformat=".0%", yaxis_title="Purchase rate")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader("Purchase rate by occasion")
        pr2 = df.groupby("occasion", observed=True)["purchased"].mean().reset_index().sort_values("purchased")
        fig = px.bar(pr2, x="purchased", y="occasion", orientation="h", color="occasion", text_auto=".1%")
        fig.update_layout(height=420, showlegend=False, xaxis_tickformat=".0%", xaxis_title="Purchase rate")
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Score comparison: purchased vs not")
        score_cols = ["satisfaction_score", "trend_score", "comfort_score", "sustainability_score", "quality_score", "fit_score"]
        comp = df.groupby("purchased_label")[score_cols].mean().reset_index().melt(id_vars="purchased_label",
                                                                                     var_name="score", value_name="value")
        fig = px.bar(comp, x="score", y="value", color="purchased_label", barmode="group")
        fig.update_layout(height=420, xaxis_tickangle=-30)
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        st.subheader("Price distribution: purchased vs not")
        fig = px.violin(df, x="purchased_label", y="price_usd", color="purchased_label", box=True, points=False)
        fig.update_layout(height=420, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()
    st.subheader("Recommendation priority vs. purchase rate")
    prio_pr = df.groupby("recommendation_priority", observed=True)["purchased"].agg(["mean", "count"]).reset_index()
    prio_pr.columns = ["priority", "purchase_rate", "sessions"]
    order = ["Top Priority", "High", "Medium", "Low"]
    prio_pr["priority"] = pd.Categorical(prio_pr["priority"], categories=order, ordered=True)
    prio_pr = prio_pr.sort_values("priority")
    fig = px.bar(prio_pr, x="priority", y="purchase_rate", color="priority", text_auto=".1%",
                 hover_data=["sessions"])
    fig.update_layout(height=380, showlegend=False, yaxis_tickformat=".0%")
    st.plotly_chart(fig, use_container_width=True)

# ----------------------------------------------------------------------------
# TAB 6 — DATA EXPLORER
# ----------------------------------------------------------------------------
with tab_explorer:
    st.subheader("Raw data explorer")
    st.caption("Browse and search the filtered dataset. Use the sidebar to narrow results, or search below.")

    search = st.text_input("Search outfit descriptions", "")
    show_df = df.copy()
    if search:
        show_df = show_df[show_df["outfit_description"].str.contains(search, case=False, na=False)]

    cols_default = ["user_id", "gender", "age_group", "style_preference", "clothing_type",
                     "primary_color", "occasion", "price_usd", "satisfaction_score",
                     "purchased_label", "outfit_description"]
    cols_to_show = st.multiselect("Columns to display", df.columns.tolist(), default=cols_default)

    st.dataframe(show_df[cols_to_show], use_container_width=True, height=450)
    st.caption(f"Showing {len(show_df):,} rows")

    csv = show_df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download filtered data as CSV", csv, "fashion_filtered.csv", "text/csv")

# ----------------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------------
st.divider()
st.caption("Fashion Insights Dashboard · Built with Streamlit & Plotly")
