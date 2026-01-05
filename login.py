import streamlit as st
from db.auth import create_user, authenticate_user

# session state
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id:
    st.info("✅ You are already logged in!")
    st.stop()  # prevent access to login page

st.title("🔐 Login / Register")

tab1, tab2 = st.tabs(["Login", "Register"])

# -------- LOGIN --------
with tab1:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_id = authenticate_user(email, password)
        if user_id:
            st.session_state.user_id = user_id
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid email or password")

# -------- REGISTER --------
with tab2:
    new_email = st.text_input("Email", key="reg_email")
    new_password = st.text_input("Password", type="password", key="reg_pass")

    if st.button("Register"):
        create_user(new_email, new_password)
        st.success("Account created! Please login.")
