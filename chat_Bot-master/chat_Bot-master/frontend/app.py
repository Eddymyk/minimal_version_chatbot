import streamlit as st
import requests

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="Chatbot Platform", layout="centered")

# ---------------- SESSION STATE ----------------
if "token" not in st.session_state:
    st.session_state.token = None

# ---------------- AUTH ----------------
st.title("🔐 Chatbot Login/Register")

if not st.session_state.token:
    choice = st.radio("Choose Action", ["Login", "Register"])

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        if st.button("Register"):
            r = requests.post(f"{API_BASE}/register", params={"username": username, "password": password})
            if r.status_code == 200:
                st.success("✅ Registered! Please login now.")
            else:
                st.error(r.json()["detail"])
    else:
        if st.button("Login"):
            r = requests.post(f"{API_BASE}/login", data={"username": username, "password": password})
            if r.status_code == 200:
                st.session_state.token = r.json()["access_token"]
                st.success("✅ Logged in successfully!")
                st.rerun()
            else:
                st.error(r.json()["detail"])
else:
    # ---------------- CHAT ----------------
    st.title("💬 Chat with Gemini")

    prompt = st.text_input("Enter your message")
    if st.button("Send") and prompt:
        r = requests.post(
            f"{API_BASE}/chat",
            params={"prompt": prompt},
            headers={"Authorization": f"Bearer {st.session_state.token}"}
        )
        if r.status_code == 200:
            st.write("🤖 Gemini:", r.json()["response"])
        else:
            st.error("Error: " + r.text)

    if st.button("Logout"):
        st.session_state.token = None
        st.rerun()
