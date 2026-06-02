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
