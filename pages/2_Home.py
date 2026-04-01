import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Home", layout="wide")

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
prefs = pd.read_csv("user_preferences.csv")

if not os.path.exists("watchlist.csv"):
    pd.DataFrame(columns=["user_id","movieId","title"]).to_csv("watchlist.csv",index=False)

watchlist = pd.read_csv("watchlist.csv")

# ---------------- PAGE TITLE ----------------
st.title("🎬 Movies Recommended For You")

# ---------------- GET USER PREFERENCES ----------------
preferred_titles = prefs[prefs["user_id"] == user_id]["movie_title"].tolist()

# ---------------- RECOMMENDER FUNCTION ----------------
def recommend_from_preferences(preferred_titles, n=15):

    preferred_movies = movies[movies["title"].isin(preferred_titles)]

    genres = set()

    for g in preferred_movies["genres"]:
        genres.update(g.split("|"))

    def score(row):
        return len(genres.intersection(row["genres"].split("|")))

    temp = movies.copy()
    temp["score"] = temp.apply(score, axis=1)

    return (
        temp[~temp["title"].isin(preferred_titles)]
        .sort_values("score", ascending=False)
        .head(n)
        .reset_index(drop=True)
    )

# ---------------- GET RECOMMENDATIONS ----------------
recs = recommend_from_preferences(preferred_titles, 15)

# ---------------- DISPLAY GRID ----------------
cols = st.columns(3)

for i, row in recs.iterrows():

    with cols[i % 3]:

        st.markdown(f"""
        <div style="
        padding:18px;
        border-radius:12px;
        background:#f5f7fb;
        box-shadow:0 4px 10px rgba(0,0,0,0.08);
        color:black;
        ">
        <h4 style="color:black;">{row['title']}</h4>
        <p style="color:#333;"><b>Genres:</b> {row['genres']}</p>
        </div>
        """, unsafe_allow_html=True)

        in_watchlist = (
            (watchlist["user_id"] == user_id) &
            (watchlist["movieId"] == row["movieId"])
        ).any()

        if in_watchlist:
            st.success("In Watchlist")
        else:
            if st.button("⭐ Add to Watchlist", key=f"home_add_{row['movieId']}"):

                new_row = pd.DataFrame([{
                    "user_id": user_id,
                    "movieId": row["movieId"],
                    "title": row["title"]
                }])

                watchlist = pd.concat([watchlist,new_row],ignore_index=True)
                watchlist.to_csv("watchlist.csv",index=False)

                st.success("Added to Watchlist ⭐")
                st.rerun()

st.divider()

if st.button("🔍 Explore More Movies"):
    st.switch_page("pages/3_Explore.py")

if st.button("⭐ My Watchlist"):
    st.switch_page("pages/4_Watchlist.py")