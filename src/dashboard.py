import streamlit as st
import pandas as pd

@st.cache_data
def load_data(file_path: str) -> pd.DataFrame:
    """
    Loads, cleans, and caches the Netflix titles dataset.
    """
    df = pd.read_csv(file_path)
    
    # Fill missing values properly
    df['director'] = df['director'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    df['rating'] = df['rating'].fillna('NR')
    df['duration'] = df['duration'].fillna('Unknown')
    
    # Simple duration cleaning for consistency
    df['duration'] = df['duration'].str.strip()
    
    return df

def render_kpi_cards(df: pd.DataFrame):
    """
    Calculates and renders 4 responsive Netflix-style metric KPI cards.
    """
    total_titles = len(df)
    movies_count = len(df[df['type'] == 'Movie'])
    tv_shows_count = len(df[df['type'] == 'TV Show'])
    
    # Extract unique countries (excluding 'Unknown')
    countries_set = set()
    for countries_str in df['country'].dropna():
        for c in countries_str.split(','):
            c_clean = c.strip()
            if c_clean and c_clean != 'Unknown':
                countries_set.add(c_clean)
    countries_count = len(countries_set)
    
    # Columns layout
    col1, col2, col3, col4 = st.columns(4)
    
    metrics = [
        ("🎬 Total Titles", f"{total_titles:,}", "Full catalog size", col1),
        ("🎥 Movies", f"{movies_count:,}", f"{movies_count/max(1, total_titles)*100:.1f}% ratio", col2),
        ("📺 TV Shows", f"{tv_shows_count:,}", f"{tv_shows_count/max(1, total_titles)*100:.1f}% ratio", col3),
        ("🌍 Countries", f"{countries_count:,}", "Production hubs", col4)
    ]
    
    for title, value, subtitle, col in metrics:
        with col:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
                <div class="kpi-subtitle">{subtitle}</div>
            </div>
            """, unsafe_allow_html=True)

def render_insights_panel(df: pd.DataFrame):
    """
    Calculates and renders AI insights based on the filtered dataset.
    """
    st.markdown("### 🤖 CineVision AI Insights Panel")
    
    if df.empty:
        st.warning("No data available for the current filters.")
        return
        
    total_titles = len(df)
    
    # 1. Top Genre
    genre_list = []
    for val in df['listed_in'].dropna():
        for g in val.split(','):
            g_clean = g.strip()
            if g_clean:
                genre_list.append(g_clean)
    from collections import Counter
    top_genre = Counter(genre_list).most_common(1)[0][0] if genre_list else 'N/A'
    
    # 2. Top Country
    country_list = []
    for val in df['country'].dropna():
        if val != 'Unknown':
            for c in val.split(','):
                c_clean = c.strip()
                if c_clean:
                    country_list.append(c_clean)
    top_country = Counter(country_list).most_common(1)[0][0] if country_list else 'N/A'
    
    # 3. Top Rating
    top_rating = df['rating'].mode()[0] if not df['rating'].empty else 'N/A'
    if top_rating == 'NR':
        top_rating = 'Not Rated'
        
    # 4. Most Active Year
    top_year = df['release_year'].mode()[0] if not df['release_year'].empty else 'N/A'
    
    # 5. Movie vs TV Show Ratio
    movies_count = len(df[df['type'] == 'Movie'])
    tv_shows_count = len(df[df['type'] == 'TV Show'])
    movie_pct = (movies_count / total_titles) * 100 if total_titles > 0 else 0
    tv_pct = (tv_shows_count / total_titles) * 100 if total_titles > 0 else 0
    ratio_insight = f"{movie_pct:.1f}% Movie / {tv_pct:.1f}% TV"
    
    # Render in 5 columns for a clean one-row layout
    col1, col2, col3, col4, col5 = st.columns(5)
    
    insights = [
        ("🎭 Top Genre", top_genre, col1),
        ("🌍 Top Country", top_country, col2),
        ("🏷️ Top Rating", top_rating, col3),
        ("📅 Most Active Year", str(top_year), col4),
        ("📊 Movie vs TV Ratio", ratio_insight, col5)
    ]
    
    for label, val, col in insights:
        with col:
            st.markdown(f"""
            <div class="insight-card">
                <div class="insight-label">{label}</div>
                <div class="insight-val" title="{val}">{val}</div>
            </div>
            """, unsafe_allow_html=True)


