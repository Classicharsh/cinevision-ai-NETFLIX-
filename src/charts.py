import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from collections import Counter

def apply_luxury_layout(fig, title_text: str):
    """
    Applies custom luxury dark theme styling to a Plotly figure.
    """
    fig.update_layout(
        title=dict(
            text=title_text,
            font=dict(family="Outfit, sans-serif", size=18, color="#FFFFFF"),
            yanchor="top",
            y=0.95
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Inter, sans-serif", color="#E5E5E5"),
        margin=dict(l=40, r=20, t=60, b=40),
        legend=dict(
            font=dict(color="#E5E5E5"),
            bgcolor='rgba(0,0,0,0)'
        )
    )
    return fig

def plot_type_pie(df: pd.DataFrame):
    """
    Renders Movie vs TV Show composition donut/pie chart.
    """
    counts = df['type'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=counts.index, 
        values=counts.values, 
        hole=0.5,
        marker=dict(colors=['#E50914', '#221F1F'], line=dict(color='#000000', width=2)),
        textinfo='percent+label',
        textfont=dict(size=12, color='#FFFFFF'),
        hoverinfo='label+value'
    )])
    
    fig = apply_luxury_layout(fig, "📊 Catalog Composition (Type)")
    fig.update_layout(height=350)
    return fig

def plot_top_countries(df: pd.DataFrame):
    """
    Renders a horizontal bar chart of the Top 10 producing countries.
    """
    # Parse countries (splitting comma-separated entries)
    country_list = []
    for val in df['country'].dropna():
        if val != 'Unknown':
            for c in val.split(','):
                c_clean = c.strip()
                if c_clean:
                    country_list.append(c_clean)
                    
    # Count occurrences
    counts = Counter(country_list)
    top_10 = pd.DataFrame(counts.most_common(10), columns=['Country', 'Titles Count'])
    
    # Sort for horizontal bar chart (so largest is at top)
    top_10 = top_10.sort_values(by='Titles Count', ascending=True)
    
    fig = px.bar(
        top_10,
        x='Titles Count',
        y='Country',
        orientation='h',
        color_discrete_sequence=['#E50914']
    )
    
    fig = apply_luxury_layout(fig, "🌍 Top 10 Producing Countries")
    fig.update_layout(
        height=350,
        xaxis=dict(showgrid=True, gridcolor='#222222', title="Total Titles"),
        yaxis=dict(showgrid=False, title="")
    )
    # Style bars
    fig.update_traces(marker_line_color='#000000', marker_line_width=1)
    return fig

def plot_top_ratings(df: pd.DataFrame):
    """
    Renders a bar chart of the Top 10 Content Ratings.
    """
    counts = df['rating'].value_counts().head(10)
    ratings_df = pd.DataFrame({'Rating': counts.index, 'Count': counts.values})
    
    fig = px.bar(
        ratings_df,
        x='Rating',
        y='Count',
        color_discrete_sequence=['#B3B3B3'] # Silver/Gray for ratings, keeping Red for main focus
    )
    
    fig = apply_luxury_layout(fig, "🏷️ Top 10 Age Ratings")
    fig.update_layout(
        height=350,
        xaxis=dict(showgrid=False, title="Age Rating"),
        yaxis=dict(showgrid=True, gridcolor='#222222', title="Titles Count")
    )
    # Highlight the top rating bar in Netflix Red
    colors = ['#E50914'] + ['#221F1F'] * 9  # highlight first bar
    fig.update_traces(
        marker_color=colors,
        marker_line_color='#000000', 
        marker_line_width=1
    )
    return fig
