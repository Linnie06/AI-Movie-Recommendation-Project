import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="AI Movie Search", layout="wide")

# -------- AUTH CHECK --------
if "user_id" not in st.session_state:
    st.switch_page("main.py")

# -------- LOAD DATA --------
movies = pd.read_csv("movies.csv")

movies["genres_clean"] = movies["genres"].str.replace("|", " ", regex=False)
movies["search_text"] = movies["title"] + " " + movies["genres_clean"]

# -------- TF-IDF MODEL --------
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(movies["search_text"])

# -------- CUSTOM UI CSS --------
st.markdown("""
<style>
.movie-card {
    background: #1e1e2f;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #2e2e3e;
    margin-bottom: 18px;
    transition: all 0.25s ease;
}

.movie-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.6);
}

.movie-title {
    font-size: 18px;
    font-weight: 600;
    color: #ffffff;
    margin-bottom: 6px;
}

.movie-genre {
    font-size: 13px;
    color: #bbbbbb;
}
</style>
""", unsafe_allow_html=True)

# -------- TITLE --------
st.title("🔎 AI Movie Search")
query = st.text_input("Describe the movie you want")

# -------- SEARCH FUNCTION --------
def search_movies(query):
    query_vec = vectorizer.transform([query])
    similarity = cosine_similarity(query_vec, tfidf_matrix)
    scores = similarity.flatten()
    indices = scores.argsort()[-12:][::-1]
    return movies.iloc[indices]


# -------- DISPLAY RESULTS --------
if query:

    results = search_movies(query)

    st.markdown("### 🎬 Search Results")

    results_list = results.reset_index(drop=True)

    for i in range(0, len(results_list), 3):

        cols = st.columns(3)

        for j in range(3):
            if i + j < len(results_list):

                row = results_list.iloc[i + j]
                genres = row["genres"].replace("|", " • ")

                with cols[j]:
                    st.markdown(f"""
                    <div class="movie-card">
                        <div class="movie-title">{row['title']}</div>
                        <div class="movie-genre">{genres}</div>
                    </div>
                    """, unsafe_allow_html=True)

        # spacing between rows
        st.markdown("<br>", unsafe_allow_html=True)