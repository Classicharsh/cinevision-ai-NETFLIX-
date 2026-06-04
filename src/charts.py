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

def plot_top_genres(df: pd.DataFrame):
    """
    Renders a horizontal bar chart of the Top 10 Genres.
    """
    genre_list = []
    for val in df['listed_in'].dropna():
        for g in val.split(','):
            g_clean = g.strip()
            if g_clean:
                genre_list.append(g_clean)
                
    counts = Counter(genre_list)
    top_10 = pd.DataFrame(counts.most_common(10), columns=['Genre', 'Titles Count'])
    
    # Sort for horizontal bar chart (largest at top)
    top_10 = top_10.sort_values(by='Titles Count', ascending=True)
    
    fig = px.bar(
        top_10,
        x='Titles Count',
        y='Genre',
        orientation='h',
        color_discrete_sequence=['#E50914']
    )
    
    fig = apply_luxury_layout(fig, "🎭 Top 10 Genres")
    fig.update_layout(
        height=350,
        xaxis=dict(showgrid=True, gridcolor='#222222', title="Total Titles"),
        yaxis=dict(showgrid=False, title="")
    )
    fig.update_traces(marker_line_color='#000000', marker_line_width=1)
    return fig

def plot_growth_timeline(df: pd.DataFrame):
    """
    Renders a line chart showing catalog growth over release years.
    """
    counts = df['release_year'].value_counts().sort_index()
    timeline_df = pd.DataFrame({'Year': counts.index, 'Titles Count': counts.values})
    
    fig = px.line(
        timeline_df,
        x='Year',
        y='Titles Count',
        color_discrete_sequence=['#E50914']
    )
    
    # Apply premium line and marker configurations
    fig.update_traces(
        line=dict(width=3, color='#E50914'),
        mode='lines+markers',
        marker=dict(size=6, color='#E50914', line=dict(width=1, color='#FFFFFF')),
        hovertemplate="<b>Year %{x}</b><br>Titles: %{y}<extra></extra>"
    )
    
    # Area fill under the line for a premium glow/area effect
    fig.update_traces(
        fill='tozeroy',
        fillcolor='rgba(229, 9, 20, 0.1)'
    )
    
    fig = apply_luxury_layout(fig, "🕒 Content Growth Timeline")
    
    # Determine step spacing for year labels based on dynamic range
    year_range_span = timeline_df['Year'].max() - timeline_df['Year'].min() if not timeline_df.empty else 0
    dtick_val = 5 if year_range_span > 20 else 1
    
    fig.update_layout(
        height=350,
        xaxis=dict(
            showgrid=True, 
            gridcolor='#222222', 
            title="Release Year",
            dtick=dtick_val
        ),
        yaxis=dict(showgrid=True, gridcolor='#222222', title="Titles Count")
    )
    return fig

def plot_talent_network(selected_actor: str, df: pd.DataFrame):
    """
    Renders an interactive circular collaboration graph for a selected actor and their top co-stars.
    """
    import numpy as np
    import plotly.graph_objects as go
    from collections import Counter
    
    # 1. Filter movies featuring the selected actor
    actor_df = df[df['cast'].str.contains(selected_actor, na=False, case=False)]
    
    if actor_df.empty:
        # Return empty figure with warning title
        fig = go.Figure()
        fig = apply_luxury_layout(fig, f"No collaborations found for {selected_actor}")
        return fig
        
    # 2. Extract co-stars
    co_stars = []
    for cast_str in actor_df['cast'].dropna():
        for actor in cast_str.split(','):
            actor_clean = actor.strip()
            if actor_clean and actor_clean.lower() != selected_actor.lower() and actor_clean != 'Unknown':
                co_stars.append(actor_clean)
                
    if not co_stars:
        # Only the actor itself exists
        fig = go.Figure(data=[go.Scatter(x=[0], y=[0], mode='markers+text', text=[selected_actor], marker=dict(size=20, color='#E50914'))])
        fig = apply_luxury_layout(fig, f"🤝 Collaboration Map for {selected_actor} (No co-stars)")
        return fig
        
    # 3. Get top 10 co-stars by co-occurrence count
    top_co_stars = Counter(co_stars).most_common(10)
    num_nodes = len(top_co_stars)
    
    # 4. Define node coordinates (Circular layout)
    # Center node (Selected Actor)
    x_nodes = [0.0]
    y_nodes = [0.0]
    node_labels = [selected_actor]
    node_sizes = [24]
    node_colors = ['#E50914'] # Netflix Red for target actor
    node_text = [f"<b>{selected_actor}</b><br>Collaborations: {len(actor_df)}"]
    
    # Border nodes (Co-stars)
    for i, (star, count) in enumerate(top_co_stars):
        angle = (2 * np.pi * i) / num_nodes
        x_nodes.append(np.cos(angle))
        y_nodes.append(np.sin(angle))
        node_labels.append(star)
        node_sizes.append(12 + count * 2) # Size scaled by collaboration count
        node_colors.append('#B3B3B3') # Silver for co-stars
        node_text.append(f"<b>{star}</b><br>Co-starred in {count} titles")
        
    # 5. Build edges (line coordinates)
    edge_x = []
    edge_y = []
    for i in range(1, num_nodes + 1):
        edge_x.extend([0.0, x_nodes[i], None])
        edge_y.extend([0.0, y_nodes[i], None])
        
    # 6. Create Plotly traces
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#333333'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_trace = go.Scatter(
        x=x_nodes, y=y_nodes,
        mode='markers+text',
        hoverinfo='text',
        text=node_labels,
        textposition="top center",
        hovertext=node_text,
        marker=dict(
            showscale=False,
            color=node_colors,
            size=node_sizes,
            line=dict(width=2, color='#000000')
        ),
        textfont=dict(family="Inter, sans-serif", size=10, color="#FFFFFF")
    )
    
    # 7. Layout styling
    fig = go.Figure(data=[edge_trace, node_trace])
    fig = apply_luxury_layout(fig, f"🤝 Talent Collaboration Map for {selected_actor}")
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        height=450
    )
    return fig

def plot_genre_forecast(df: pd.DataFrame):
    """
    Fits a simple linear regression model using pure Python/NumPy to predict the next 5 years 
    of production volume for the top 5 genres, avoiding external scikit-learn DLL checks.
    """
    import numpy as np
    import plotly.graph_objects as go
    
    # 1. Extract genres and find top 5
    genres = []
    for val in df['listed_in'].dropna():
        for g in val.split(','):
            g_clean = g.strip()
            if g_clean:
                genres.append(g_clean)
                
    from collections import Counter
    top_5_genres = [item[0] for item in Counter(genres).most_common(5)]
    
    fig = go.Figure()
    
    # Harmonized color palette for the top 5 genres
    genre_colors = ['#E50914', '#E15A97', '#975AE1', '#5ABCE1', '#5AE197']
    
    max_year = int(df['release_year'].max())
    min_year = max(1995, int(df['release_year'].min())) # restrict start year for stable regression
    
    historical_years = np.arange(min_year, max_year + 1)
    future_years = np.arange(max_year + 1, max_year + 6)
    
    for idx, genre in enumerate(top_5_genres):
        # Count releases per year for this genre
        genre_df = df[df['listed_in'].str.contains(genre, na=False, case=False)]
        yearly_counts = genre_df['release_year'].value_counts()
        
        # Build historic counts array
        hist_counts = []
        for y in historical_years:
            hist_counts.append(yearly_counts.get(y, 0))
            
        hist_counts = np.array(hist_counts)
        
        # Pure NumPy Simple Linear Regression
        mean_x = np.mean(historical_years)
        mean_y = np.mean(hist_counts)
        
        num = np.sum((historical_years - mean_x) * (hist_counts - mean_y))
        den = np.sum((historical_years - mean_x) ** 2)
        
        slope = num / den if den != 0 else 0.0
        intercept = mean_y - slope * mean_x
        
        # Predict future counts (ensure predictions don't go below 0)
        future_pred = slope * future_years + intercept
        future_pred = np.clip(future_pred, 0, None)
        
        color = genre_colors[idx % len(genre_colors)]
        
        # Plot Historical Line
        fig.add_trace(go.Scatter(
            x=historical_years,
            y=hist_counts,
            mode='lines',
            name=genre,
            line=dict(color=color, width=2.5),
            hovertemplate=f"<b>{genre} (Historical)</b><br>Year: %{{x}}<br>Count: %{{y}}<extra></extra>"
        ))
        
        # Plot Forecasted Line (dashed extension)
        fig.add_trace(go.Scatter(
            x=np.concatenate(([historical_years[-1]], future_years)),
            y=np.concatenate(([hist_counts[-1]], future_pred)),
            mode='lines',
            name=f"{genre} (Forecast)",
            line=dict(color=color, width=2, dash='dash'),
            showlegend=False,
            hovertemplate=f"<b>{genre} (Forecasted)</b><br>Year: %{{x}}<br>Count: %{{y:.1f}}<extra></extra>"
        ))
        
    fig = apply_luxury_layout(fig, "🔮 5-Year Genre Production Forecast")
    fig.update_layout(
        height=400,
        xaxis=dict(showgrid=True, gridcolor='#222222', title="Year"),
        yaxis=dict(showgrid=True, gridcolor='#222222', title="Releases Count")
    )
    return fig


