import streamlit as st
import requests
import re
import os
from dotenv import load_dotenv
from pathlib import Path
from decouple import config


# env_path=Path(__file__).resolve().parent.parent.parent/"hw.py"
# # print(env_path)
# # load_dotenv(dotenv_path=env_path)
# print(env_path)

#S_accessCode=os.getenv('access_code')
S_accessCode=config('access_code')
print(f"SAccess: {S_accessCode}")

# --- Session State Setup ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "api_url" not in st.session_state:
    st.session_state.api_url = ""

if "url_set" not in st.session_state:
    st.session_state.url_set = False

if "show_settings" not in st.session_state:
    st.session_state.show_settings = True  

# --- AUTH PAGE ---
if not st.session_state.authenticated:
    st.title("🔐 Enter Access Code to Continue")
    access_code = st.text_input("Access Code", type="password")
    if st.button("Unlock"):
        if access_code == S_accessCode:  
            st.session_state.authenticated = True
            st.success("Access granted. Click Unlock again to be redirected")
        else:
            st.error("Invalid code.")
    st.stop()

# --- HEADER ---
st.title("🤖 Stock Price Agent")


if st.session_state.show_settings or not st.session_state.url_set:
    with st.expander("🔧 Set API Endpoint (Required)", expanded=True):
        new_url = st.text_input("Enter new API URL (Required):", value=st.session_state.api_url)
        if st.button("Save Endpoint"):
            if new_url.strip().startswith("http"):
                st.session_state.api_url = new_url.strip()
                st.session_state.url_set = True
                st.session_state.show_settings = False
                st.success("✅ Endpoint saved. Click Save Endpoint again to fold the Expander")
            else:
                st.warning("⚠️ Please enter a valid URL starting with http or https.")
else:
    with st.container():
        col1, col2 = st.columns([0.85, 0.15])
        with col2:
            if st.button("⚙️"):
                st.session_state.show_settings = True

# --- MAIN CHAT INTERFACE ---
if st.session_state.url_set:
    prompt = st.text_input("💬 Enter your prompt")

    if st.button("Submit"):
        try:
            response = requests.post(
                st.session_state.api_url,
                json={"prompt": prompt}
            )

            if response.ok:
                result = response.json()
                answer = result.get("AI Result", "No Result")
                cleanedAnswer = re.sub(r"<thinking>.*?</thinking>", "", answer, flags=re.DOTALL)
                st.write(cleanedAnswer.strip())
            else:
                st.error(f"❌ Request failed: {response.status_code}")
        except Exception as e:
            st.error(f"⚠️ Error: {e}")
else:
    st.info("Please enter a valid API endpoint to continue.")
