import streamlit as st
import pandas as pd
import os
import hashlib

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# -------- HIDE MAIN PAGE FROM SIDEBAR --------

st.markdown("""
<style>

/* Hide first sidebar item */

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

    </div>

    <hr>
    """,
    unsafe_allow_html=True
)

# ==============================
# USER DATABASE
# ==============================

USERS_FILE = "users.csv"

# Create users file if missing
if not os.path.exists(USERS_FILE):

    users_df = pd.DataFrame(
        columns=[
            "user_id",
            "username",
            "password"
        ]
    )

    users_df.to_csv(USERS_FILE, index=False)

# ==============================
# HELPER FUNCTIONS
# ==============================

def load_users():
    return pd.read_csv(USERS_FILE)

# Password hashing
def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()

# ==============================
# SIGNUP
# ==============================

def create_user(username, password):

    users = load_users()

    # Username exists
    if username in users["username"].values:
        return False, "Username already exists"

    # Generate new ID
    new_id = (
        1 if users.empty
        else users["user_id"].max() + 1
    )

    # Hash password
    hashed_password = hash_password(password)

    # Save user
    users.loc[len(users)] = [
        new_id,
        username,
        hashed_password
    ]

    users.to_csv(USERS_FILE, index=False)

    return True, new_id

# ==============================
# LOGIN
# ==============================

def login_user(username, password):

    users = load_users()

    hashed_password = hash_password(password)

    user = users[
        (users["username"] == username)
        &
        (users["password"] == hashed_password)
    ]

    if user.empty:
        return False, None

    return True, int(user.iloc[0]["user_id"])

# ==============================
# CHECK PREFERENCES
# ==============================

def user_has_preferences(user_id):

    if not os.path.exists(
        "user_preferences.csv"
    ):
        return False

    prefs = pd.read_csv(
        "user_preferences.csv"
    )

    return user_id in prefs["user_id"].values

# ==============================
# LOGIN / SIGNUP UI
# ==============================

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    tab1, tab2 = st.tabs([
        "Login",
        "Sign Up"
    ])

    # ==============================
    # LOGIN TAB
    # ==============================

    with tab1:

        st.markdown("### Login")

        login_username = st.text_input(
            "Username",
            key="login_username"
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password"
        )

        if st.button(
            "🚀 Login",
            use_container_width=True
        ):

            if (
                login_username.strip() == ""
                or
                login_password.strip() == ""
            ):

                st.warning(
                    "⚠️ Please fill all fields"
                )

            else:

                success, user_id = login_user(
                    login_username,
                    login_password
                )

                if success:

                    st.session_state["user_id"] = user_id

                    st.session_state["username"] = (
                        login_username
                    )

                    st.success(
                        "Login successful"
                    )

                    # Redirect
                    if user_has_preferences(user_id):

                        st.switch_page(
                            "pages/2_Home.py"
                        )

                    else:

                        st.switch_page(
                            "pages/1_Select_Movies.py"
                        )

                else:

                    st.error(
                        "Invalid username or password"
                    )

    # ==============================
    # SIGNUP TAB
    # ==============================

    with tab2:

        st.markdown("### Create Account")

        signup_username = st.text_input(
            "Choose Username",
            key="signup_username"
        )

        signup_password = st.text_input(
            "Choose Password",
            type="password",
            key="signup_password"
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password"
        )

        if st.button(
            "Sign Up",
            use_container_width=True
        ):

            if (
                signup_username.strip() == ""
                or
                signup_password.strip() == ""
                or
                confirm_password.strip() == ""
            ):

                st.warning(
                    "⚠️ Please fill all fields"
                )

            elif signup_password != confirm_password:

                st.error(
                    "❌ Passwords do not match"
                )

            elif len(signup_password) < 6:

                st.warning(
                    "⚠️ Password must be at least 6 characters"
                )

            else:

                success, result = create_user(
                    signup_username,
                    signup_password
                )

                if success:

                    # Store session
                    st.session_state["user_id"] = result
                    st.session_state["username"] = signup_username

                    st.success(
                        "Account created successfully"
                    )

                    # Redirect new users to preference selection
                    st.switch_page(
                        "pages/1_Select_Movies.py"
                    )

                else:

                    st.error(f"❌ {result}")