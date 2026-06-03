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
from src.charts import plot_type_pie, plot_top_countries, plot_top_ratings, plot_top_genres, plot_growth_timeline
from src.recommender import build_similarity_matrix, get_recommendations
from src.geo_analytics import plot_geo_map
from src.insights import render_enhanced_insights, generate_insights
from src.report_generator import generate_pdf_report

# 3. Load dataset
data_path = os.path.join(os.path.dirname(__file__), 'data', 'datanetflix_titles.csv')
if not os.path.exists(data_path):
    st.error(f"Dataset not found at {data_path}. Please check your path.")
    st.stop()

# Load full dataset
df = load_data(data_path)

# Cache similarity matrix computation
@st.cache_resource
def load_similarity_matrix(_df):
    return build_similarity_matrix(_df)

cosine_sim = load_similarity_matrix(df)

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

# 5.5 Render Sidebar PDF Export
st.sidebar.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #141414;' />", unsafe_allow_html=True)
st.sidebar.markdown("<h4 style='color: #FFFFFF; font-family: \"Outfit\", sans-serif; margin-bottom: 10px;'>📊 Export Reports</h4>", unsafe_allow_html=True)

# Generate PDF report dynamically based on current filtered dataframe
insights_list, strategic_rec = generate_insights(filtered_df)
pdf_output_path = os.path.join(os.path.dirname(__file__), "reports", "executive_report.pdf")

try:
    generate_pdf_report(filtered_df, insights_list, strategic_rec, pdf_output_path)
    if os.path.exists(pdf_output_path):
        with open(pdf_output_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
        st.sidebar.download_button(
            label="📥 Download Executive PDF Report",
            data=pdf_bytes,
            file_name="CineVision_AI_Executive_Report.pdf",
            mime="application/pdf",
            key="download_pdf_report"
        )
except Exception as e:
    st.sidebar.error(f"Error compiling report: {str(e)}")

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

# Render Enhanced AI Insights Panel
render_enhanced_insights(filtered_df)

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# 7.5 Global Netflix Content Map
st.markdown("### 🌍 Global Netflix Content Map")
fig_map = plot_geo_map(filtered_df)
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

# 8. Render Visualizations Layout
# Row 1: Composition (40%) and Top Countries (60%)
c1, c2 = st.columns([4, 6])
with c1:
    fig_pie = plot_type_pie(filtered_df)
    st.plotly_chart(fig_pie, use_container_width=True)
with c2:
    fig_countries = plot_top_countries(filtered_df)
    st.plotly_chart(fig_countries, use_container_width=True)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# Row 2: Top Genres (60%) and Top Ratings (40%)
c3, c4 = st.columns([6, 4])
with c3:
    fig_genres = plot_top_genres(filtered_df)
    st.plotly_chart(fig_genres, use_container_width=True)
with c4:
    fig_ratings = plot_top_ratings(filtered_df)
    st.plotly_chart(fig_ratings, use_container_width=True)

st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

# Row 3: Growth Timeline (100%)
c5, = st.columns(1)
with c5:
    fig_growth = plot_growth_timeline(filtered_df)
    st.plotly_chart(fig_growth, use_container_width=True)

st.markdown("<hr style='border: none; border-top: 1px solid #141414; margin: 30px 0;' />", unsafe_allow_html=True)

# 8.5 AI Recommendation Engine
st.markdown("### 🤖 AI Recommendation Engine")
st.markdown("<p style='color: #808080; font-size: 14px; margin-top: -10px;'>Select any title from the Netflix catalog to discover 5 highly relevant recommendations powered by TF-IDF and Cosine Similarity.</p>", unsafe_allow_html=True)

all_titles = sorted(df['title'].unique())
selected_title = st.selectbox(
    "Choose a Movie or TV Show:",
    options=all_titles,
    key="recommendation_select"
)

if st.button("Get Recommendations", key="recommendation_btn"):
    recommendations_df = get_recommendations(selected_title, df, cosine_sim, top_n=5)
    
    if not recommendations_df.empty:
        rec_cols = st.columns(5)
        for i, (_, rec_row) in enumerate(recommendations_df.iterrows()):
            if i >= 5:
                break
            
            rec_title = rec_row.get('title', 'Unknown')
            rec_type = rec_row.get('type', 'Unknown')
            rec_country = rec_row.get('country', 'Unknown')
            rec_rating = rec_row.get('rating', 'Unknown')
            rec_listed_in = rec_row.get('listed_in', 'Unknown')
            rec_desc = rec_row.get('description', 'No description available.')
            
            with rec_cols[i]:
                st.markdown(f"""
                <div class="rec-card">
                    <div class="rec-title" title="{rec_title}">{rec_title}</div>
                    <div class="rec-badge-row">
                        <span class="rec-badge rec-badge-type">{rec_type}</span>
                        <span class="rec-badge rec-badge-rating">{rec_rating}</span>
                    </div>
                    <div class="rec-meta" title="{rec_country} • {rec_listed_in}">
                        🌍 {rec_country}<br>
                        🎭 {rec_listed_in}
                    </div>
                    <div class="rec-desc" title="{rec_desc}">{rec_desc}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Could not find recommendations for this title.")

st.markdown("<hr style='border: none; border-top: 1px solid #141414; margin: 30px 0;' />", unsafe_allow_html=True)

# 9. Search Engine & Preview Table
st.markdown("### 🍿 Search & Explore Catalog")
search_query = st.text_input(
    "Search catalog by title, director, cast, country, or genre:",
    placeholder="e.g. Stranger Things, Christopher Nolan, Cillian Murphy, France, Sci-Fi...",
    key="catalog_search"
)

# Apply search filter within current filtered selection
if search_query:
    keywords = [kw.strip().lower() for kw in search_query.split() if kw.strip()]
    if keywords:
        import pandas as pd
        mask = pd.Series(True, index=filtered_df.index)
        for kw in keywords:
            kw_mask = (
                filtered_df['title'].str.lower().str.contains(kw, na=False) |
                filtered_df['director'].str.lower().str.contains(kw, na=False) |
                filtered_df['cast'].str.lower().str.contains(kw, na=False) |
                filtered_df['country'].str.lower().str.contains(kw, na=False) |
                filtered_df['listed_in'].str.lower().str.contains(kw, na=False)
            )
            mask = mask & kw_mask
        search_results = filtered_df[mask]
    else:
        search_results = filtered_df
    st.markdown(f"<p style='color: #E50914; font-size: 14px; font-weight: 600; margin-top: -10px;'>Found {len(search_results):,} matching results.</p>", unsafe_allow_html=True)
else:
    search_results = filtered_df
    st.markdown(f"<p style='color: #808080; font-size: 13px; margin-top: -10px;'>Showing first 10 entries out of {len(filtered_df):,} filtered results.</p>", unsafe_allow_html=True)

# Clean columns for display
display_cols = ['title', 'type', 'director', 'cast', 'country', 'release_year', 'rating', 'duration', 'listed_in']
if search_query:
    st.dataframe(search_results[display_cols], use_container_width=True)
else:
    st.dataframe(search_results[display_cols].head(10), use_container_width=True)