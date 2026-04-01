import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds

# Load the datasets
def load_data():
    movies = pd.read_csv("movies.csv")
    ratings = pd.read_csv("ratings.csv")
    print("✅ Datasets loaded successfully!")
    return movies, ratings

# Content-based recommender
def content_based_recommender(movies, title, top_n=10):
    tfidf = TfidfVectorizer(stop_words='english')
    movies['genres'] = movies['genres'].fillna('')
    tfidf_matrix = tfidf.fit_transform(movies['genres'])
    cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

    if title not in movies['title'].values:
        print(f"❌ Movie '{title}' not found.")
        return []

    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    top_movies = [movies['title'].iloc[i[0]] for i in sim_scores[1:top_n + 1]]
    return top_movies

# Collaborative filtering recommender
def collaborative_filtering(ratings):
    user_item_matrix = ratings.pivot(index='userId', columns='movieId', values='rating').fillna(0)
    matrix = user_item_matrix.values
    user_ratings_mean = np.mean(matrix, axis=1)
    matrix_norm = matrix - user_ratings_mean.reshape(-1, 1)

    k = min(50, min(matrix_norm.shape) - 1)
    U, sigma, Vt = svds(matrix_norm, k=k)
    sigma = np.diag(sigma)

    predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_ratings_mean.reshape(-1, 1)
    predictions = pd.DataFrame(predicted_ratings, index=user_item_matrix.index, columns=user_item_matrix.columns)
    return predictions

# Hybrid recommender (combines both)
def hybrid_recommender(movies, ratings, title, top_n=10):
    content_recs = content_based_recommender(movies, title, top_n)
    predictions = collaborative_filtering(ratings)

    # Pick a random user (for simplicity)
    user_id = np.random.choice(ratings['userId'].unique())
    user_predictions = predictions.loc[user_id].sort_values(ascending=False)

    movie_ids = user_predictions.index[:top_n]
    collaborative_titles = movies[movies['movieId'].isin(movie_ids)]['title'].tolist()

    hybrid_recs = list(set(content_recs + collaborative_titles))
    return hybrid_recs[:top_n]

# For CLI testing
if __name__ == "__main__":
    movies, ratings = load_data()
    print("Example movies:\n", movies['title'].head(10).to_string(index=False))
    movie_title = input("\n🎥 Enter a movie you like: ")
    recs = hybrid_recommender(movies, ratings, movie_title)
    print("\n🎬 Recommended Movies:")
    for i, movie in enumerate(recs, 1):
        print(f"{i}. {movie}")