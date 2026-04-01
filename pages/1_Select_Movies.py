import streamlit as st
import pandas as pd
from recommender import load_data

st.set_page_config(page_title="Select Movies", layout="wide")

# SESSION GUARD
if "user_id" not in st.session_state:
    st.switch_page("main.py")

# CSS
st.markdown("""
<style>
.main { background-color: #0f1117; color: white; }
.stButton > button {
    background-color: #e50914;
    color: white;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

st.title("🎞 Tell us what you like")
st.write("Select at least 5 movies to personalize your experience")

movies, ratings = load_data()

selected_movies = st.multiselect(
    "Choose your favorite movies:",
    movies["title"].values
)

if st.button("Save Preferences"):
    if len(selected_movies) < 5:
        st.warning("Please select at least 5 movies")
    else:
        prefs = pd.read_csv("user_preferences.csv")
        user_id = st.session_state["user_id"]

        for movie in selected_movies:
            prefs.loc[len(prefs)] = [user_id, movie]

        prefs.to_csv("user_preferences.csv", index=False)
        st.success("Preferences saved!")
        st.switch_page("pages/2_Home.py")