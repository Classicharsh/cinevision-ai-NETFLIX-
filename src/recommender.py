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

def classify_mood(desc):
    """
    Classifies a plot description into one of five main moods using a rule-based keyword matcher.
    """
    if not isinstance(desc, str) or desc == 'Unknown':
        return "Drama/Emotional"
        
    desc_lower = desc.lower()
    
    # Define keyword lexicons for different moods
    thrilling_dark = ['dark', 'murder', 'killer', 'death', 'crime', 'cop', 'detective', 'mystery', 'conspiracy', 'terror', 'revenge', 'prison', 'jail', 'deadly', 'fear', 'scary', 'blood', 'monster', 'witch', 'ghost', 'haunted', 'psycho', 'serial', 'thriller', 'horror', 'suspense', 'kidnap', 'heist', 'robbery']
    sci_fi_mystery = ['alien', 'space', 'robot', 'future', 'futuristic', 'galaxy', 'sci-fi', 'science', 'technology', 'time travel', 'portal', 'dimension', 'universe', 'planet', 'laboratory', 'secret', 'discovery', 'clue', 'solve']
    feel_good_comedy = ['comedy', 'funny', 'laugh', 'humor', 'joke', 'hilarious', 'satire', 'stand-up', 'rom-com', 'romantic comedy', 'fun', 'happy', 'dog', 'pet', 'friendship', 'cartoon', 'animated', 'magic', 'magical', 'fairy', 'toy', 'cheerful']
    action_adventure = ['action', 'fight', 'martial', 'ninja', 'kung fu', 'chase', 'explosion', 'battle', 'war', 'soldier', 'army', 'weapon', 'gun', 'agent', 'spy', 'hero', 'superhero', 'survival', 'race', 'racing', 'car', 'stunt']
    drama_emotional = ['drama', 'love', 'romance', 'romantic', 'emotional', 'heartwarming', 'tear', 'sad', 'family', 'relationship', 'marriage', 'divorce', 'loss', 'grief', 'historical', 'biography', 'true story', 'inspired', 'struggle', 'father', 'mother', 'son', 'daughter', 'life', 'career']
    
    # Count matches
    scores = {
        "Thrilling/Dark": sum(1 for w in thrilling_dark if w in desc_lower),
        "Sci-Fi/Mystery": sum(1 for w in sci_fi_mystery if w in desc_lower),
        "Feel-Good/Comedy": sum(1 for w in feel_good_comedy if w in desc_lower),
        "Action/Adventure": sum(1 for w in action_adventure if w in desc_lower),
        "Drama/Emotional": sum(1 for w in drama_emotional if w in desc_lower)
    }
    
    # Find the mood with the highest score
    max_mood = max(scores, key=scores.get)
    if scores[max_mood] == 0:
        return "Drama/Emotional"  # default fallback
    return max_mood

def get_hybrid_recommendations(user_ratings, df, cosine_sim, top_n=5):
    """
    Generates personalized recommendations based on active user ratings in the session state.
    Calculates a weighted user profile vector from the cosine similarity matrix.
    user_ratings: dict where key is title (str) and value is rating (int, 1-5)
    """
    if not user_ratings:
        return pd.DataFrame()
        
    # Get index mappings
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()
    
    # Initialize user profile vector with zeros
    user_profile = np_zeros = [0.0] * len(df)
    
    import numpy as np
    user_profile = np.zeros(len(df))
    
    rated_indices = []
    for title, rating in user_ratings.items():
        if title in indices:
            idx = indices[title]
            if isinstance(idx, pd.Series):
                idx = idx.iloc[0]
            rated_indices.append(idx)
            
            # Weight: scale ratings around a midpoint of 3.0
            # 4 & 5 stars give positive weight, 1 & 2 stars give negative weight, 3 is neutral
            weight = rating - 3.0
            user_profile += weight * cosine_sim[idx]
            
    if len(rated_indices) == 0:
        return pd.DataFrame()
        
    # Find similarity scores for the user profile
    # Exclude already rated items by setting their score to -inf
    for idx in rated_indices:
        user_profile[idx] = -np.inf
        
    # Get top_n matching titles
    top_indices = np.argsort(user_profile)[::-1][:top_n]
    
    # Check if we got valid scores (not all -inf)
    if user_profile[top_indices[0]] == -np.inf:
        return pd.DataFrame()
        
    return df.iloc[top_indices]

