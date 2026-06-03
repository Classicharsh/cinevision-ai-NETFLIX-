import pandas as pd
import plotly.express as px
from collections import Counter

def plot_geo_map(df: pd.DataFrame):
    """
    Renders a Plotly choropleth map of Netflix content distribution by country.
    """
    country_list = []
    for val in df['country'].dropna():
        if val != 'Unknown':
            for c in val.split(','):
                c_clean = c.strip()
                if c_clean:
                    country_list.append(c_clean)
                    
    counts = Counter(country_list)
    geo_df = pd.DataFrame(counts.most_common(), columns=['Country', 'Titles Count'])
    
    # Render choropleth map
    fig = px.choropleth(
        geo_df,
        locations="Country",
        locationmode="country names",
        color="Titles Count",
        hover_name="Country",
        color_continuous_scale=["#221F1F", "#E50914"] # Netflix theme colors
    )
    
    # Styling layout with Netflix dark theme
    fig.update_layout(
        title=dict(
            text="🌍 Global Netflix Content Distribution",
            font=dict(family="Outfit, sans-serif", size=18, color="#FFFFFF"),
            yanchor="top",
            y=0.95
        ),
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular',
            bgcolor='rgba(0,0,0,0)',
            lakecolor='#000000',
            landcolor='#141414',
            subunitcolor='#222222',
            coastlinecolor='#333333'
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#E5E5E5"),
        margin=dict(l=0, r=0, t=50, b=0),
        coloraxis_colorbar=dict(
            title=dict(text="Titles", font=dict(color="#E5E5E5")),
            tickfont=dict(color="#E5E5E5")
        )
    )
    return fig
