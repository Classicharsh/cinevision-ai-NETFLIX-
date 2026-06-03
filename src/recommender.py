import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def build_similarity_matrix(df):
    """
    Cleans the dataset and builds the TF-IDF cosine similarity matrix.
    Uses title, director, cast, country, listed_in, description, rating, type.
    """
    cols = ['title', 'director', 'cast', 'country', 'listed_in', 'description', 'rating', 'type']
    
    # Fill missing text values with "Unknown"
    df_temp = df[cols].copy()
    for col in cols:
        df_temp[col] = df_temp[col].astype(str).fillna('Unknown').replace('nan', 'Unknown')
        
    # Combine features into a single metadata soup string
    soup = (
        df_temp['title'] + " " +
        df_temp['director'] + " " +
        df_temp['cast'] + " " +
        df_temp['country'] + " " +
        df_temp['listed_in'] + " " +
        df_temp['description'] + " " +
        df_temp['rating'] + " " +
        df_temp['type']
    )
    
    # Vectorize and calculate cosine similarity
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(soup)
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
    
    return cosine_sim

def get_recommendations(title, df, cosine_sim, top_n=5):
    """
    Returns top_n recommended titles for the given title.
    Works with exact title selection.
    """
    # Create index mapping
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()
    
    if title not in indices:
        return pd.DataFrame()
        
    idx = indices[title]
    if isinstance(idx, pd.Series):
        idx = idx.iloc[0]
        
    # Get pairwise similarity scores
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort by similarity scores descending
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Exclude the selected title itself
    sim_scores = [score for score in sim_scores if score[0] != idx]
    
    # Get top_n titles
    top_scores = sim_scores[:top_n]
    movie_indices = [i[0] for i in top_scores]
    
    return df.iloc[movie_indices]
