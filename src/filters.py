import streamlit as st
import pandas as pd

def render_sidebar_filters(df: pd.DataFrame):
    """
    Renders sidebar filters for the dashboard and returns the selections.
    """
    st.sidebar.markdown("<h3 style='color: #E50914; font-family: \"Outfit\", sans-serif; margin-bottom: 15px;'>🔍 Catalog Filters</h3>", unsafe_allow_html=True)
    
    # 1. Content Type Filter
    content_type = st.sidebar.selectbox(
        "Content Type",
        options=["All", "Movie", "TV Show"],
        index=0
    )
    
    # 2. Country Filter
    # Extract unique countries from the comma-separated strings
    countries_set = set()
    for countries_str in df['country'].dropna():
        for c in countries_str.split(','):
            c_clean = c.strip()
            if c_clean and c_clean != 'Unknown':
                countries_set.add(c_clean)
    sorted_countries = ["All"] + sorted(list(countries_set))
    
    selected_country = st.sidebar.selectbox(
        "Country",
        options=sorted_countries,
        index=0
    )
    
    # 3. Rating Filter
    # Get unique ratings (NR for Not Rated if filled during load_data)
    ratings_list = ["All"] + sorted(df['rating'].dropna().unique().tolist())
    selected_rating = st.sidebar.selectbox(
        "Age Rating",
        options=ratings_list,
        index=0
    )
    
    # 4. Release Year Range Filter
    min_year = int(df['release_year'].min())
    max_year = int(df['release_year'].max())
    
    year_range = st.sidebar.slider(
        "Release Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    
    return content_type, selected_country, selected_rating, year_range

def filter_data(df: pd.DataFrame, content_type: str, country: str, rating: str, year_range: tuple) -> pd.DataFrame:
    """
    Filters the catalog DataFrame based on user selections.
    """
    filtered_df = df.copy()
    
    # Apply Content Type filter
    if content_type != "All":
        filtered_df = filtered_df[filtered_df['type'] == content_type]
        
    # Apply Country filter
    if country != "All":
        filtered_df = filtered_df[filtered_df['country'].str.contains(country, na=False, case=False)]
        
    # Apply Rating filter
    if rating != "All":
        filtered_df = filtered_df[filtered_df['rating'] == rating]
        
    # Apply Release Year Range filter
    filtered_df = filtered_df[
        (filtered_df['release_year'] >= year_range[0]) & 
        (filtered_df['release_year'] <= year_range[1])
    ]
    
    return filtered_df
