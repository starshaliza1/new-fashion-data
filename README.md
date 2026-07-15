# Fashion Insights Dashboard

A comprehensive Streamlit dashboard for exploring `fashion_dataset_complete.csv` (10,500 sessions, 39 fields).

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app will open at `http://localhost:8501`. Make sure `data/fashion_dataset_complete.csv` stays in the `data/` folder next to `app.py` (already included).

## What's inside

**Sidebar filters** — date range, gender, age group, body type, style preference, clothing type, brand, budget level, occasion, season, price range, and purchase status. All charts update live.

**Six tabs:**
1. **Overview** — KPI cards (sessions, users, avg. price, purchase rate, avg. scores), sessions-over-time trend, recommendation priority breakdown, score correlation heatmap, total score distribution.
2. **Demographics** — gender/age/body type/skin tone distributions, plus a segment explorer comparing purchase rate and satisfaction across any demographic dimension.
3. **Style & Product** — style preference, clothing type, color, and brand popularity; style-vs-occasion heatmap; fabric mix; price by budget tier.
4. **Engagement** — views/likes/shares/saves metrics, views-vs-likes scatter, engagement by clothing type and mood, try-on distribution, monthly trend/comfort score lines.
5. **Purchase Behavior** — purchase rate by budget level, occasion, and recommendation priority; score comparison (purchased vs. not); price distribution by purchase outcome.
6. **Data Explorer** — searchable, sortable raw data table with column picker and CSV export of the current filtered view.

## Notes

- Charts are built with Plotly for interactivity (hover, zoom, pan).
- `@st.cache_data` is used on the data loader so filtering stays fast.
- To point at a different CSV, edit the `load_data()` path in `app.py`.
