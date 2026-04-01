import streamlit as st
import pandas as pd

st.set_page_config(page_title="AI Watchlist Recommendations", layout="wide")

# ---------- AUTH CHECK ----------
if "user_id" not in st.session_state:
    st.switch_page("main.py")

movies = pd.read_csv("movies.csv")
watchlist = pd.read_csv("watchlist.csv")

user_id = st.session_state["user_id"]

# ---------- UI STYLES (MATCH OTHER PAGES) ----------
st.markdown("""
<style>
.movie-card {
    background: #1e1e2f;
    padding: 18px;
    border-radius: 14px;
    border: 1px solid #2e2e3e;
    margin-bottom: 10px;
    transition: all 0.25s ease;
}

.movie-card:hover {
    transform: translateY(-5px);
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

# ---------- TITLE ----------
st.title("🎬 AI Watchlist Recommendations")

# ---------- USER WATCHLIST ----------
user_watchlist = watchlist[watchlist["user_id"] == user_id]

if user_watchlist.empty:
    st.warning("Your watchlist is empty")
    st.stop()

# ---------- EXTRACT TOP GENRES ----------
genres = []

for title in user_watchlist["title"]:
    movie = movies[movies["title"] == title]

    if not movie.empty:
        genres += movie.iloc[0]["genres"].split("|")

top_genres = pd.Series(genres).value_counts().head(2).index

# ---------- GET RECOMMENDATIONS ----------
recs = movies[
    movies["genres"].str.contains("|".join(top_genres))
].head(12).reset_index(drop=True)

# ---------- DISPLAY ----------
st.markdown("### Recommended For You")

for i in range(0, len(recs), 3):

    cols = st.columns(3)

    for j in range(3):
        if i + j < len(recs):

            row = recs.iloc[i + j]
            genres = row["genres"].replace("|", " • ")

            with cols[j]:
                st.markdown(f"""
                <div class="movie-card">
                    <div class="movie-title">{row['title']}</div>
                    <div class="movie-genre">{genres}</div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)