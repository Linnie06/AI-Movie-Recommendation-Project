import streamlit as st
import pandas as pd
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="AI Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# -------- HIDE MAIN PAGE FROM SIDEBAR --------
st.markdown("""
<style>
/* Hide the first item in sidebar (main page) */
[data-testid="stSidebarNav"] ul li:first-child {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------
st.markdown(
    """
    <div style="text-align:center; margin-top:40px;">
        <h1>🎥 AI Movie Recommendation System</h1>
        <p style="font-size:18px; color:gray;">
            Personalized movie suggestions just for you
        </p>
    </div>
    <hr>
    """,
    unsafe_allow_html=True
)

# ---------------- HELPER FUNCTIONS ----------------

def load_users():
    if not os.path.exists("users.csv"):
        return pd.DataFrame(columns=["user_id", "username"])
    return pd.read_csv("users.csv")


def save_user(username):
    users = load_users()

    if username in users["username"].values:
        return users.loc[users["username"] == username, "user_id"].iloc[0]

    new_id = 1 if users.empty else users["user_id"].max() + 1
    users.loc[len(users)] = [new_id, username]
    users.to_csv("users.csv", index=False)
    return new_id


def user_has_preferences(user_id):
    if not os.path.exists("user_preferences.csv"):
        return False
    prefs = pd.read_csv("user_preferences.csv")
    return user_id in prefs["user_id"].values

# ---------------- LOGIN UI ----------------

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 👤 Login")
    username = st.text_input("Enter your username")

    if st.button("🚀 Login", use_container_width=True):
        if username.strip() == "":
            st.warning("⚠️ Please enter a username")
        else:
            user_id = save_user(username)

            st.session_state["user_id"] = user_id
            st.session_state["username"] = username

            if user_has_preferences(user_id):
                st.switch_page("pages/2_Home.py")
            else:
                st.switch_page("pages/1_Select_Movies.py")