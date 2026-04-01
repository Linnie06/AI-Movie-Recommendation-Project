import streamlit as st
import pandas as pd

st.set_page_config(page_title="My Watchlist", layout="wide")

# ---------- AUTH CHECK ----------
if "user_id" not in st.session_state:
    st.switch_page("main.py")

user_id = st.session_state["user_id"]

# ---------- TOP BAR ----------
col1, col2 = st.columns([6, 1])
with col2:
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.switch_page("main.py")

# ---------- LOAD DATA ----------
watchlist = pd.read_csv("watchlist.csv")
user_watchlist = watchlist[watchlist["user_id"] == user_id]

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
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ---------- UI ----------
st.title("⭐ My Watchlist")

if user_watchlist.empty:
    st.info("Your watchlist is empty.")
else:
    watchlist_list = user_watchlist.reset_index(drop=True)

    for i in range(0, len(watchlist_list), 3):

        cols = st.columns(3)

        for j in range(3):
            if i + j < len(watchlist_list):

                row = watchlist_list.iloc[i + j]

                with cols[j]:

                    # movie card
                    st.markdown(f"""
                    <div class="movie-card">
                        <div class="movie-title">{row['title']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # remove button
                    if st.button("Remove", key=f"remove_{row['movieId']}"):
                        watchlist = watchlist[
                            ~(
                                (watchlist["user_id"] == user_id) &
                                (watchlist["movieId"] == row["movieId"])
                            )
                        ]
                        watchlist.to_csv("watchlist.csv", index=False)
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

# ---------- NAVIGATION ----------
st.divider()

if st.button("⬅ Back to Home"):
    st.switch_page("pages/2_Home.py")