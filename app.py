import sys
import os
import urllib.parse
import requests
import numpy as np
import pandas as pd
import streamlit as st

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
from src.charts import (
    plot_type_pie, plot_top_countries, plot_top_ratings, 
    plot_top_genres, plot_growth_timeline, plot_talent_network, 
    plot_genre_forecast
)
from src.recommender import (
    build_similarity_matrix, get_recommendations, 
    classify_mood, get_hybrid_recommendations
)
from src.geo_analytics import plot_geo_map
from src.insights import render_enhanced_insights, generate_insights
from src.report_generator import generate_pdf_report, generate_watchlist_pdf

# 3. Initialize session state
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = set()
if 'ratings' not in st.session_state:
    st.session_state.ratings = {}

# 4. TMDb API Helper
@st.cache_data(show_spinner=False)
def get_tmdb_metadata(title, tmdb_api_key=None):
    """
    Queries the TMDb API to retrieve movie poster URL and YouTube trailer key.
    """
    if not tmdb_api_key or tmdb_api_key.strip() == "":
        return None, None
        
    try:
        # Search multi endpoint
        query_encoded = urllib.parse.quote(title.strip())
        search_url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api_key}&query={query_encoded}&language=en-US"
        r = requests.get(search_url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            results = data.get('results', [])
            if results:
                match = results[0]
                media_type = match.get('media_type', 'movie')
                # If search returns something else, fallback
                if media_type not in ['movie', 'tv']:
                    media_type = 'movie'
                    
                tmdb_id = match.get('id')
                poster_path = match.get('poster_path')
                poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None
                
                # Fetch videos endpoint
                video_url = None
                video_endpoint = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/videos?api_key={tmdb_api_key}&language=en-US"
                v_r = requests.get(video_endpoint, timeout=5)
                if v_r.status_code == 200:
                    v_data = v_r.json()
                    v_results = v_data.get('results', [])
                    for video in v_results:
                        if video.get('site') == 'YouTube' and video.get('type') in ['Trailer', 'Teaser']:
                            video_url = f"https://www.youtube.com/watch?v={video.get('key')}"
                            break
                return poster_url, video_url
    except Exception:
        pass
    return None, None

# 5. Load dataset
data_path = os.path.join(os.path.dirname(__file__), 'data', 'datanetflix_titles.csv')
if not os.path.exists(data_path):
    st.error(f"Dataset not found at {data_path}. Please check your path.")
    st.stop()

# Load and enrich data with moods
@st.cache_data
def get_enriched_data(path):
    df = load_data(path)
    # Apply rule-based mood categorizer
    df['mood'] = df['description'].apply(classify_mood)
    return df

df = get_enriched_data(data_path)

# Extract actors list for network explorer
@st.cache_data
def get_unique_actors(dataframe):
    actors = set()
    for val in dataframe['cast'].dropna():
        if val != 'Unknown':
            for actor in val.split(','):
                a_clean = actor.strip()
                if a_clean and a_clean != 'Unknown':
                    actors.add(a_clean)
    return sorted(list(actors))

unique_actors_list = get_unique_actors(df)

# Cache similarity matrix computation
@st.cache_resource
def load_similarity_matrix(_df):
    return build_similarity_matrix(_df)

cosine_sim = load_similarity_matrix(df)

# 6. Render Sidebar Header
st.sidebar.markdown("""
<div style="text-align: center; padding: 10px 0 10px 0;">
    <h1 style="color: #E50914; font-family: 'Outfit', sans-serif; font-size: 28px; font-weight: 700; margin: 0; text-shadow: 0 0 10px rgba(229, 9, 20, 0.3);">🎬 CineVision AI</h1>
    <p style="color: #666666; font-size: 12px; margin: 5px 0 0 0;">Netflix Intelligence Dashboard</p>
</div>
<hr style="margin: 0 0 15px 0; border: none; border-top: 1px solid #141414;" />
""", unsafe_allow_html=True)

# 7. Render Sidebar Filters
content_type, selected_country, selected_rating, year_range = render_sidebar_filters(df)
filtered_df = filter_data(df, content_type, selected_country, selected_rating, year_range)

# 8. Render Sidebar PDF Export
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

# 9. Render Integrations Section
st.sidebar.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #141414;' />", unsafe_allow_html=True)
st.sidebar.markdown("<h4 style='color: #FFFFFF; font-family: \"Outfit\", sans-serif; margin-bottom: 10px;'>🔑 Integrations</h4>", unsafe_allow_html=True)
tmdb_api_key = st.sidebar.text_input("TMDb API Key", type="password", help="Enter a free TMDb API Key to enable real-time movie poster fetching and official trailers.")

# 10. Render App Headers
st.markdown("""
<div style="padding: 10px 0 20px 0;">
    <h1 style="font-size: 38px; margin: 0;">🎬 CineVision AI</h1>
    <p style="color: #808080; font-size: 16px; margin: 5px 0 0 0;">Intelligent Netflix Streaming Analytics Platform</p>
</div>
""", unsafe_allow_html=True)

# 11. Create Tabs layout
tab_analytics, tab_recommender, tab_talent, tab_explorer, tab_watchlist = st.tabs([
    "📊 Platform Analytics", 
    "🤖 AI Recommendations", 
    "🤝 Talent Collaboration Graph", 
    "🍿 Explore Catalog", 
    "📑 My Watchlist"
])

# ==================== TAB 1: PLATFORM ANALYTICS ====================
with tab_analytics:
    st.markdown("### 📊 Platform Executive Performance")
    render_kpi_cards(filtered_df)
    
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
    render_enhanced_insights(filtered_df)
    
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🌍 Global Netflix Content Map")
    fig_map = plot_geo_map(filtered_df)
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)
    
    # Visualizations layout grid
    c1, c2 = st.columns([4, 6])
    with c1:
        fig_pie = plot_type_pie(filtered_df)
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_countries = plot_top_countries(filtered_df)
        st.plotly_chart(fig_countries, use_container_width=True)
        
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    c3, c4 = st.columns([6, 4])
    with c3:
        fig_genres = plot_top_genres(filtered_df)
        st.plotly_chart(fig_genres, use_container_width=True)
    with c4:
        fig_ratings = plot_top_ratings(filtered_df)
        st.plotly_chart(fig_ratings, use_container_width=True)
        
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
    
    c5, c6 = st.columns([6, 4])
    with c5:
        fig_growth = plot_growth_timeline(filtered_df)
        st.plotly_chart(fig_growth, use_container_width=True)
    with c6:
        # Genre production forecast using Linear Regression
        fig_forecast = plot_genre_forecast(filtered_df)
        st.plotly_chart(fig_forecast, use_container_width=True)

# ==================== TAB 2: AI RECOMMENDATIONS ====================
with tab_recommender:
    st.markdown("### 🧠 AI Recommendation Suite")
    
    c_rec1, c_rec2 = st.columns(2)
    
    with c_rec1:
        st.markdown("#### 🍿 Content-Based Finder")
        st.markdown("Select a title to discover 5 highly relevant recommendations powered by TF-IDF and Cosine Similarity.")
        all_titles = sorted(df['title'].unique())
        selected_title = st.selectbox(
            "Choose a Movie or TV Show:",
            options=all_titles,
            key="recommender_select_tab"
        )
        
        if st.button("Get Recommendations", key="recommender_btn_tab"):
            recommendations_df = get_recommendations(selected_title, df, cosine_sim, top_n=5)
            if not recommendations_df.empty:
                for idx, (_, rec_row) in enumerate(recommendations_df.iterrows()):
                    rec_title = rec_row.get('title', 'Unknown')
                    rec_type = rec_row.get('type', 'Unknown')
                    rec_rating = rec_row.get('rating', 'Unknown')
                    rec_desc = rec_row.get('description', 'No description available.')
                    poster_url, trailer_url = get_tmdb_metadata(rec_title, tmdb_api_key)
                    
                    # Card rendering
                    img_tag = f'<img src="{poster_url}" class="poster-img" style="height: 120px; width: 80px; float: left; margin-right: 15px; object-fit: cover; border-radius: 4px;" />' if poster_url else '<div style="height: 120px; width: 80px; float: left; margin-right: 15px; background: #222; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 20px;">🎬</div>'
                    
                    st.markdown(f"""
                    <div style="background-color: #141414; padding: 15px; border-radius: 6px; border: 1px solid #222; margin-bottom: 12px; min-height: 150px; overflow: auto;">
                        {img_tag}
                        <div style="font-weight: 700; color: #FFFFFF; font-size: 16px;">{rec_title}</div>
                        <div style="margin: 5px 0;">
                            <span class="rec-badge rec-badge-type">{rec_type}</span>
                            <span class="rec-badge rec-badge-rating">{rec_rating}</span>
                        </div>
                        <div style="font-size: 12px; color: #888888; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">{rec_desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Could not find recommendations for this title.")
                
    with c_rec2:
        st.markdown("#### 🧠 Collaborative Hybrid Recommendations")
        st.markdown("Your personalized taste index updates live as you rate movies in the **Explore Catalog** tab.")
        
        if not st.session_state.ratings:
            st.info("💡 **Rate titles first!** Go to the 'Explore Catalog' tab and give star ratings to titles to train your collaborative AI profile.")
        else:
            st.markdown(f"Curating suggestions based on **{len(st.session_state.ratings)}** rated titles:")
            hybrid_df = get_hybrid_recommendations(st.session_state.ratings, df, cosine_sim, top_n=5)
            
            if not hybrid_df.empty:
                for idx, (_, rec_row) in enumerate(hybrid_df.iterrows()):
                    rec_title = rec_row.get('title', 'Unknown')
                    rec_type = rec_row.get('type', 'Unknown')
                    rec_rating = rec_row.get('rating', 'Unknown')
                    rec_desc = rec_row.get('description', 'No description available.')
                    poster_url, trailer_url = get_tmdb_metadata(rec_title, tmdb_api_key)
                    
                    img_tag = f'<img src="{poster_url}" class="poster-img" style="height: 120px; width: 80px; float: left; margin-right: 15px; object-fit: cover; border-radius: 4px;" />' if poster_url else '<div style="height: 120px; width: 80px; float: left; margin-right: 15px; background: #222; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 20px;">🎬</div>'
                    
                    st.markdown(f"""
                    <div style="background-color: #141414; padding: 15px; border-radius: 6px; border: 1px solid #222; margin-bottom: 12px; min-height: 150px; overflow: auto;">
                        {img_tag}
                        <div style="font-weight: 700; color: #FFFFFF; font-size: 16px;">{rec_title}</div>
                        <div style="margin: 5px 0;">
                            <span class="rec-badge rec-badge-type">{rec_type}</span>
                            <span class="rec-badge rec-badge-rating">{rec_rating}</span>
                        </div>
                        <div style="font-size: 12px; color: #888888; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;">{rec_desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("Please rate more movies to calculate collaborative weights.")

# ==================== TAB 3: TALENT COLLABORATION GRAPH ====================
with tab_talent:
    st.markdown("### 🤝 Talent Connection Map")
    st.markdown("Visualize networking and co-star relations in our catalog database.")
    
    selected_actor = st.selectbox(
        "Select or Search for an Actor:",
        options=unique_actors_list,
        index=0 if unique_actors_list else None,
        key="talent_actor_select"
    )
    
    if selected_actor:
        fig_network = plot_talent_network(selected_actor, df)
        st.plotly_chart(fig_network, use_container_width=True)

# ==================== TAB 4: EXPLORE CATALOG ====================
with tab_explorer:
    st.markdown("### 🍿 Explore Catalog Grid")
    
    # Explorer search filters row
    c_f1, c_f2 = st.columns([7, 3])
    with c_f1:
        search_query = st.text_input(
            "Search catalog by title, director, cast, country, or genre:",
            placeholder="e.g. Stranger Things, Christopher Nolan, Cillian Murphy...",
            key="catalog_search_tab"
        )
    with c_f2:
        selected_mood = st.selectbox(
            "Filter by Plot Mood (NLP):",
            options=["All", "Thrilling/Dark", "Sci-Fi/Mystery", "Feel-Good/Comedy", "Action/Adventure", "Drama/Emotional"],
            key="mood_filter"
        )
        
    # Apply filters
    explorer_df = filtered_df.copy()
    if selected_mood != "All":
        explorer_df = explorer_df[explorer_df['mood'] == selected_mood]
        
    if search_query:
        keywords = [kw.strip().lower() for kw in search_query.split() if kw.strip()]
        if keywords:
            mask = pd.Series(True, index=explorer_df.index)
            for kw in keywords:
                kw_mask = (
                    explorer_df['title'].str.lower().str.contains(kw, na=False) |
                    explorer_df['director'].str.lower().str.contains(kw, na=False) |
                    explorer_df['cast'].str.lower().str.contains(kw, na=False) |
                    explorer_df['country'].str.lower().str.contains(kw, na=False) |
                    explorer_df['listed_in'].str.lower().str.contains(kw, na=False)
                )
                mask = mask & kw_mask
            search_results = explorer_df[mask]
        else:
            search_results = explorer_df
    else:
        search_results = explorer_df
        
    st.markdown(f"<p style='color: #E50914; font-weight: 600;'>Showing {min(12, len(search_results))} out of {len(search_results):,} matches.</p>", unsafe_allow_html=True)
    
    # Render Grid
    grid_df = search_results.head(12)
    if grid_df.empty:
        st.warning("No matches found for active filters.")
    else:
        cols = st.columns(3)
        for i, (_, row) in enumerate(grid_df.iterrows()):
            col_idx = i % 3
            title = row['title']
            
            with cols[col_idx]:
                # Fetch posters & trailers
                poster_url, trailer_url = get_tmdb_metadata(title, tmdb_api_key)
                
                # Check Watchlist status
                is_in_watchlist = title in st.session_state.watchlist
                watchlist_btn_label = "➖ Remove Watchlist" if is_in_watchlist else "➕ Add to Watchlist"
                
                # Fetch rating
                saved_rating = st.session_state.ratings.get(title, 3)
                
                # Poster HTML template
                if poster_url:
                    poster_html = f'<img class="poster-img" src="{poster_url}" />'
                else:
                    initials = "".join([w[0] for w in title.split()[:2] if w]).upper()
                    poster_html = f"""
                    <div class="poster-placeholder">
                        <div class="poster-placeholder-icon">🎬</div>
                        <div class="poster-placeholder-text">{initials}</div>
                    </div>
                    """
                    
                st.markdown(f"""
                <div class="catalog-card">
                    {poster_html}
                    <div class="catalog-title" title="{title}">{title}</div>
                    <div class="catalog-badges">
                        <span class="catalog-badge catalog-badge-type">{row['type']}</span>
                        <span class="catalog-badge catalog-badge-mood">{row['mood']}</span>
                        <span class="catalog-badge catalog-badge-rating">{row['rating']}</span>
                    </div>
                    <div class="catalog-desc" title="{row['description']}">{row['description']}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Actions UI Row
                c_act_btn, c_act_rate = st.columns([6, 4])
                with c_act_btn:
                    if st.button(watchlist_btn_label, key=f"watchlist_btn_{title}_{i}"):
                        if is_in_watchlist:
                            st.session_state.watchlist.remove(title)
                            st.toast(f"Removed {title} from watchlist!")
                        else:
                            st.session_state.watchlist.add(title)
                            st.toast(f"Added {title} to watchlist!")
                        st.rerun()
                        
                with c_act_rate:
                    new_rating = st.selectbox(
                        "⭐ Rating",
                        options=[1, 2, 3, 4, 5],
                        index=saved_rating - 1,
                        key=f"rating_select_{title}_{i}"
                    )
                    if new_rating != saved_rating:
                        st.session_state.ratings[title] = new_rating
                        st.toast(f"Rated {title} {new_rating}/5 stars!")
                        st.rerun()
                        
                if trailer_url:
                    st.markdown(f'<a href="{trailer_url}" target="_blank" style="font-size: 11px; color: #E50914; text-decoration: none; font-weight: bold; margin-top: 5px; display: inline-block;">▶ Watch YouTube Trailer</a>', unsafe_allow_html=True)

# ==================== TAB 5: MY WATCHLIST ====================
with tab_watchlist:
    st.markdown("### 📑 Personal Curated Watchlist")
    st.markdown("View saved titles and compile a custom PDF playlist report.")
    
    if not st.session_state.watchlist:
        st.info("Your watchlist is empty. Go to the 'Explore Catalog' tab to add movies or series.")
    else:
        # Action Header
        c_wl1, c_wl2 = st.columns([8, 2])
        
        with c_wl1:
            st.write(f"You have **{len(st.session_state.watchlist)}** titles saved in your watchlist.")
            
        with c_wl2:
            # Watchlist PDF download compiler
            wl_pdf_path = os.path.join(os.path.dirname(__file__), "reports", "watchlist_report.pdf")
            try:
                generate_watchlist_pdf(list(st.session_state.watchlist), df, wl_pdf_path)
                if os.path.exists(wl_pdf_path):
                    with open(wl_pdf_path, "rb") as wl_file:
                        wl_bytes = wl_file.read()
                    st.download_button(
                        label="📥 Export Watchlist PDF",
                        data=wl_bytes,
                        file_name="CineVision_AI_Watchlist_Playlist.pdf",
                        mime="application/pdf",
                        key="download_watchlist_report_btn"
                    )
            except Exception as e:
                st.error(f"Error compiling watchlist: {str(e)}")
                
        st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid #141414;' />", unsafe_allow_html=True)
        
        # Render Watchlist list layout
        watchlist_df = df[df['title'].isin(list(st.session_state.watchlist))]
        for idx, (_, row) in enumerate(watchlist_df.iterrows()):
            wl_title = row['title']
            wl_desc = row['description']
            wl_rating = row['rating']
            wl_type = row['type']
            wl_country = row['country']
            
            poster_url, trailer_url = get_tmdb_metadata(wl_title, tmdb_api_key)
            img_tag = f'<img src="{poster_url}" style="height: 110px; width: 75px; float: left; margin-right: 15px; object-fit: cover; border-radius: 4px;" />' if poster_url else '<div style="height: 110px; width: 75px; float: left; margin-right: 15px; background: #222; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-size: 20px;">🎬</div>'
            
            # Watchlist card
            c_wl_card, c_wl_remove = st.columns([9, 1])
            with c_wl_card:
                st.markdown(f"""
                <div style="background-color: #111113; padding: 15px; border-radius: 6px; border: 1px solid #222; margin-bottom: 12px; min-height: 140px; overflow: auto;">
                    {img_tag}
                    <div style="font-weight: 700; color: #FFFFFF; font-size: 16px;">{wl_title}</div>
                    <div style="margin: 5px 0;">
                        <span class="rec-badge rec-badge-type">{wl_type}</span>
                        <span class="rec-badge rec-badge-rating">{wl_rating}</span>
                        <span style="font-size: 11px; color: #808080; margin-left: 10px;">🌍 {wl_country}</span>
                    </div>
                    <div style="font-size: 12px; color: #888888; line-height: 1.4;">{wl_desc}</div>
                </div>
                """, unsafe_allow_html=True)
            with c_wl_remove:
                st.markdown("<div style='margin-top: 45px;'></div>", unsafe_allow_html=True)
                if st.button("❌ Remove", key=f"wl_rm_{wl_title}_{idx}"):
                    st.session_state.watchlist.remove(wl_title)
                    st.toast(f"Removed {wl_title} from watchlist!")
                    st.rerun()