import streamlit as st
import pandas as pd
import re
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="AI Movie Chatbot", layout="wide")

# -------- AUTH CHECK --------
if "user_id" not in st.session_state:
    st.switch_page("main.py")

# -------- LOAD DATA --------
movies = pd.read_csv("movies.csv")

movies["genres_clean"] = movies["genres"].str.replace("|", " ", regex=False)
movies["search_text"] = movies["title"] + " " + movies["genres_clean"]

# -------- NLP MODEL --------
vectorizer = TfidfVectorizer(stop_words="english")
tfidf_matrix = vectorizer.fit_transform(movies["search_text"])

# -------- GROQ SETUP --------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

st.title("🤖 AI Movie Assistant")
st.write("Ask me anything about movies!")

# -------- CHAT MEMORY --------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_recs" not in st.session_state:
    st.session_state.last_recs = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# -------- ML SEARCH --------
def search_movies(query):
    query_vec = vectorizer.transform([query])
    similarity = cosine_similarity(query_vec, tfidf_matrix)
    scores = similarity.flatten()
    indices = scores.argsort()[-10:][::-1]
    return movies.iloc[indices]


# -------- RECOMMENDER --------
def recommend_movies(title, n=5):
    match = movies[movies["title"] == title]

    if match.empty:
        return []

    base = match.iloc[0]
    base_genres = set(base["genres"].split("|"))

    def score(row):
        g = set(row["genres"].split("|"))
        inter = len(base_genres.intersection(g))
        union = len(base_genres.union(g))
        return inter / union if union != 0 else 0

    temp = movies.copy()
    temp["score"] = temp.apply(score, axis=1)

    recs = (
        temp[temp["title"] != title]
        .sort_values("score", ascending=False)
        .head(n)
    )

    return recs["title"].tolist()


# -------- AI EXPLANATION --------
def explain(context, recs):

    prompt = f"""
You are a movie recommendation assistant.

STRICT RULES:
- ONLY talk about the movies given below.
- DO NOT suggest any new movies.
- DO NOT add extra recommendations.
- Explain each movie in 2-3 lines.
- Keep it short and clear.

User query: {context}

Movies:
{recs}

Now explain why EACH of these movies matches.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content


# -------- USER INPUT --------
prompt = st.chat_input("Ask about movies...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()

    # -------- FOLLOW-UP HANDLING --------
    if st.session_state.last_recs and any(
        word in prompt_lower for word in ["explain", "elaborate", "details"]
    ):
        recs = st.session_state.last_recs

        reply = "### Movie details:\n\n"
        explanation = explain("previous recommendations", recs)
        reply += explanation

    else:
        # -------- DETECT MOVIE NAME --------
        movie_found = None

        for title in movies["title"]:
            if len(title) < 2:
                continue

            pattern = r"\b" + re.escape(title.lower()) + r"\b"

            if re.search(pattern, prompt_lower):
                movie_found = title
                break

        # -------- MOVIE SIMILARITY --------
        if movie_found:
            recs = recommend_movies(movie_found)

            st.session_state.last_recs = recs  # save context

            explanation = explain(movie_found, recs)

            reply = f"### Movies similar to **{movie_found}**\n\n"

            for m in recs:
                reply += f"• {m}\n"

            reply += f"\n\n**Why these movies?**\n{explanation}"

        # -------- SEARCH / GENRE --------
        else:
            results = search_movies(prompt)
            recs = results["title"].tolist()[:5]

            st.session_state.last_recs = recs  # save context

            reply = "### Here are movies matching your request:\n\n"

            for m in recs:
                reply += f"• {m}\n"

            explanation = explain(prompt, recs)
            reply += f"\n\n**Why these movies?**\n{explanation}"

    # -------- DISPLAY --------
    with st.chat_message("assistant"):
        st.markdown(reply)

    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )