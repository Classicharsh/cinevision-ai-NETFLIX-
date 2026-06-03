import streamlit as st
import pandas as pd
from collections import Counter

def generate_insights(df: pd.DataFrame):
    """
    Dynamically analyzes the filtered dataset to generate business insights
    and a strategic catalog recommendation.
    """
    if df.empty:
        return [], {}
        
    total_titles = len(df)
    
    # 1. Top Country
    country_list = []
    for val in df['country'].dropna():
        if val != 'Unknown':
            for c in val.split(','):
                c_clean = c.strip()
                if c_clean:
                    country_list.append(c_clean)
    top_country = Counter(country_list).most_common(1)[0][0] if country_list else 'Unknown'
    
    # 2. Dominant Genre
    genre_list = []
    for val in df['listed_in'].dropna():
        for g in val.split(','):
            g_clean = g.strip()
            if g_clean:
                genre_list.append(g_clean)
    top_genre = Counter(genre_list).most_common(1)[0][0] if genre_list else 'Unknown'
    
    # 3. Common Rating
    top_rating = df['rating'].mode()[0] if not df['rating'].empty else 'NR'
    if top_rating == 'NR':
        top_rating = 'Not Rated'
        
    # 4. Peak Year
    top_year = df['release_year'].mode()[0] if not df['release_year'].empty else 'Unknown'
    
    # 5. Movie vs TV Show Ratio
    movies_count = len(df[df['type'] == 'Movie'])
    tv_shows_count = len(df[df['type'] == 'TV Show'])
    movie_pct = (movies_count / total_titles) * 100 if total_titles > 0 else 0
    tv_pct = (tv_shows_count / total_titles) * 100 if total_titles > 0 else 0
    
    # Build 5 business insights
    insights = [
        {
            "title": "🌍 Geographic Dominance",
            "desc": f"The primary content hub in this selection is **{top_country}**, which leads production. Expanding regional partnerships here remains key to catalog growth."
        },
        {
            "title": "🎭 Audience Affinity & Genres",
            "desc": f"**{top_genre}** is the dominant genre. This highlights strong viewer interest in storytelling in this category. Content acquisition should prioritize these themes."
        },
        {
            "title": "🏷️ Age Demographics",
            "desc": f"The most frequent content rating is **{top_rating}**. This indicates that the selected catalog segment targets this specific age group's consumption preferences."
        },
        {
            "title": "📅 Peak Production Velocity",
            "desc": f"Content release velocity peaked in **{top_year}**. Analyzing historical release patterns around this peak offers valuable scheduling insights."
        },
        {
            "title": "📊 Catalog Composition",
            "desc": f"The selection features a **{movie_pct:.1f}% Movie vs {tv_pct:.1f}% TV Show** distribution. This balance determines subscriber retention patterns."
        }
    ]
    
    # Strategic recommendation
    if tv_pct < 35.0:
        rec_text = f"TV Shows represent only {tv_pct:.1f}% of this catalog. We recommend investing in serialized drama franchises in **{top_country}** to improve long-term subscriber retention and reduce churn."
    elif movie_pct < 50.0:
        rec_text = f"Movies represent only {movie_pct:.1f}% of this catalog. To capture impulse evening viewers, we recommend acquiring high-impact indie films and blockbuster titles."
    else:
        rec_text = f"With **{top_genre}** leading the catalog, Netflix should license niche foreign-language titles in this genre, distributing them globally to unlock untapped market potential."
        
    strategic_rec = {
        "title": "💡 Catalog Strategic Path",
        "desc": rec_text
    }
    
    return insights, strategic_rec

def render_enhanced_insights(df: pd.DataFrame):
    """
    Renders the AI insights panel on the Streamlit dashboard in a premium card layout.
    """
    st.markdown("### 🤖 CineVision AI Insights Panel")
    
    insights, strategic_rec = generate_insights(df)
    if not insights:
        st.warning("No data available for the current filters.")
        return
        
    # Render 5 business insights in a 3-col and 2-col layout
    col1, col2, col3 = st.columns(3)
    col4, col5 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">{insights[0]['title']}</div>
            <div class="rec-desc">{insights[0]['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">{insights[1]['title']}</div>
            <div class="rec-desc">{insights[1]['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">{insights[2]['title']}</div>
            <div class="rec-desc">{insights[2]['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col4:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">{insights[3]['title']}</div>
            <div class="rec-desc">{insights[3]['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col5:
        st.markdown(f"""
        <div class="insight-card">
            <div class="insight-label">{insights[4]['title']}</div>
            <div class="rec-desc">{insights[4]['desc']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Full width Strategic recommendation card
    st.markdown(f"""
    <div class="insight-card" style="border-left: 4px solid #E50914 !important; border-top: 1px solid #222222 !important;">
        <div class="insight-label" style="color: #E50914 !important; font-weight: 700 !important;">{strategic_rec['title']}</div>
        <div style="font-size: 13px !important; color: #FFFFFF !important; line-height: 1.5 !important; padding-top: 5px;">
            {strategic_rec['desc']}
        </div>
    </div>
    """, unsafe_allow_html=True)
