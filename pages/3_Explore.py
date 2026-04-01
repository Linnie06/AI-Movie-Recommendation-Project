import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Explore Movies", layout="wide")

# ---------------- AUTH CHECK ----------------
if "user_id" not in st.session_state:
    st.switch_page("main.py")

user_id = st.session_state["user_id"]

# ---------------- LOGOUT ----------------
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("main.py")

# ---------------- LOAD DATA ----------------
movies = pd.read_csv("movies.csv")

if not os.path.exists("watchlist.csv"):
    pd.DataFrame(
        columns=["user_id", "movieId", "title"]
    ).to_csv("watchlist.csv", index=False)

watchlist = pd.read_csv("watchlist.csv")

# ---------------- UI STYLES (MATCH SEARCH PAGE) ----------------
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
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ----------------
st.title("🔍 Explore Movies")

# ---------------- INPUTS ----------------
movie_title = st.selectbox(
    "🎬 Select a movie",
    movies["title"].sort_values().tolist()
)

num_recs = st.slider(
    "🎯 Number of recommendations",
    1, 20, 5
)

# ---------------- RECOMMENDER ----------------
def recommend_movies(title, n):

    base = movies[movies["title"] == title].iloc[0]
    base_genres = set(base["genres"].split("|"))

    def score(row):
        movie_genres = set(row["genres"].split("|"))

        intersection = len(base_genres.intersection(movie_genres))
        union = len(base_genres.union(movie_genres))

        return intersection / union if union != 0 else 0

    temp = movies.copy()
    temp["score"] = temp.apply(score, axis=1)

    return (
        temp[temp["title"] != title]
        .sort_values("score", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )

# ---------------- GET RECOMMENDATIONS ----------------
if st.button("✨ Get Recommendations"):
    st.session_state["explore_recs"] = recommend_movies(
        movie_title, num_recs
    )

# ---------------- SHOW RECOMMENDATIONS ----------------
if "explore_recs" in st.session_state:

    st.markdown("### 🎬 Recommended for You")

    recs = st.session_state["explore_recs"]

    recs_list = recs.reset_index(drop=True)

    for i in range(0, len(recs_list), 3):

        cols = st.columns(3)

        for j in range(3):
            if i + j < len(recs_list):

                row = recs_list.iloc[i + j]
                genres = row["genres"].replace("|", " • ")

                in_watchlist = (
                    (watchlist["user_id"] == user_id) &
                    (watchlist["movieId"] == row["movieId"])
                ).any()

                with cols[j]:

                    st.markdown(f"""
                    <div class="movie-card">
                        <div class="movie-title">{row['title']}</div>
                        <div class="movie-genre">{genres}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    if in_watchlist:
                        st.success("In Watchlist")
                    else:
                        if st.button(
                            "⭐ Add to Watchlist",
                            key=f"add_{row['movieId']}"
                        ):

                            new_row = pd.DataFrame([{
                                "user_id": user_id,
                                "movieId": row["movieId"],
                                "title": row["title"]
                            }])

                            watchlist = pd.concat(
                                [watchlist, new_row],
                                ignore_index=True
                            )

                            watchlist.to_csv(
                                "watchlist.csv",
                                index=False
                            )

                            st.success("Added to Watchlist ⭐")
                            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

# ---------------- NAVIGATION ----------------
st.divider()

if st.button("⬅ Back to Home"):
    st.switch_page("pages/2_Home.py")