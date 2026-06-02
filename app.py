import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import streamlit as st
import os
import sys

# Ensure the project root is in sys.path so modules can be imported relative to it
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 1. Set page config as the very first Streamlit call
st.set_page_config(
    page_title="CineVision AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inject CSS style sheet for custom luxury Netflix theme
css_path = os.path.join(os.path.dirname(__file__), 'assets', 'style.css')
if os.path.exists(css_path):
    with open(css_path, 'r', encoding='utf-8') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Import modular components
from src.dashboard import load_data, render_kpi_cards
from src.filters import render_sidebar_filters, filter_data
from src.charts import plot_type_pie, plot_top_countries, plot_top_ratings

# 3. Load dataset
data_path = os.path.join(os.path.dirname(__file__), 'data', 'datanetflix_titles.csv')
if not os.path.exists(data_path):
    st.error(f"Dataset not found at {data_path}. Please check your path.")
    st.stop()

# Load full dataset
df = load_data(data_path)

# 4. Render Sidebar Header
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0 10px 0;">
    <h1 style="color: #E50914; font-family: 'Outfit', sans-serif; font-size: 28px; font-weight: 700; margin: 0; text-shadow: 0 0 10px rgba(229, 9, 20, 0.3);">🎬 CineVision AI</h1>
    <p style="color: #666666; font-size: 12px; margin: 5px 0 0 0;">Netflix Intelligence Dashboard</p>
</div>
<hr style="margin: 0 0 15px 0; border: none; border-top: 1px solid #141414;" />
""", unsafe_allow_html=True)

# 5. Render Sidebar Filters
content_type, selected_country, selected_rating, year_range = render_sidebar_filters(df)

# Apply filtering logic
filtered_df = filter_data(df, content_type, selected_country, selected_rating, year_range)

# 6. Render Dashboard Header
st.markdown("""
<div style="padding: 10px 0 20px 0;">
    <h1 style="font-size: 38px; margin: 0;">🎬 CineVision AI</h1>
    <p style="color: #808080; font-size: 16px; margin: 5px 0 0 0;">Intelligent Netflix Streaming Analytics Platform</p>
</div>
""", unsafe_allow_html=True)

# 7. Render KPI Cards
render_kpi_cards(filtered_df)

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# 8. Render Visualizations Layout
c1, c2 = st.columns([4, 6])

with c1:
    fig_pie = plot_type_pie(filtered_df)
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    fig_countries = plot_top_countries(filtered_df)
    st.plotly_chart(fig_countries, use_container_width=True)

st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

c3, = st.columns(1)
with c3:
    fig_ratings = plot_top_ratings(filtered_df)
    st.plotly_chart(fig_ratings, use_container_width=True)

st.markdown("<hr style='border: none; border-top: 1px solid #141414; margin: 30px 0;' />", unsafe_allow_html=True)

# 9. Filtered Dataset Preview Table
st.markdown("### 🍿 Catalog Dataset Preview")
st.markdown(f"<p style='color: #808080; font-size: 13px; margin-top: -10px;'>Showing first 10 entries out of {len(filtered_df):,} filtered results.</p>", unsafe_allow_html=True)

# Clean columns for display
display_cols = ['title', 'type', 'director', 'cast', 'country', 'release_year', 'rating', 'duration', 'listed_in']
display_df = filtered_df[display_cols].head(10)

st.dataframe(display_df, use_container_width=True)