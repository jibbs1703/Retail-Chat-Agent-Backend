"""Retail Chat Agent Streamlit Frontend."""

import base64
import os

import requests
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


def check_health() -> bool:
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/healthcheck", timeout=5)
        return r.ok
    except requests.RequestException:
        return False


def send_message(message: str, image_b64: str | None, session_id: str | None) -> dict:
    payload = {"message": message, "image_b64": image_b64, "session_id": session_id}
    r = requests.post(f"{BACKEND_URL}/api/v1/chat", json=payload, timeout=120)
    r.raise_for_status()
    return r.json()


st.set_page_config(page_title="Retail Chat Agent", page_icon="🛍️", layout="centered")
st.title("🛍️ Retail Chat Agent")

healthy = check_health()
st.caption(f"Backend: {'🟢 Connected' if healthy else '🔴 Disconnected'} — {BACKEND_URL}")

if not healthy:
    st.error("Cannot reach the backend. Check that the backend service is running.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image"):
            st.image(base64.b64decode(msg["image"]), width=260)
        st.markdown(msg["content"])

with st.sidebar:
    st.header("Options")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.rerun()
    if st.session_state.session_id:
        st.caption(f"Session: `{st.session_state.session_id}`")

uploaded = st.file_uploader(
    "📎 Attach a product image (optional)",
    type=["jpg", "jpeg", "png", "webp", "gif"],
    label_visibility="collapsed",
    help="Attach a product image to search by visual similarity",
)

image_b64 = None
if uploaded:
    image_b64 = base64.b64encode(uploaded.read()).decode()
    st.image(
        base64.b64decode(image_b64), width=120, caption="Image attached — will be searched on send"
    )

if prompt := st.chat_input("Describe a product or ask a question…", disabled=not healthy):
    user_entry = {"role": "user", "content": prompt}
    if image_b64:
        user_entry["image"] = image_b64
    st.session_state.messages.append(user_entry)

    with st.chat_message("user"):
        if image_b64:
            st.image(base64.b64decode(image_b64), width=260)
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                data = send_message(prompt, image_b64, st.session_state.session_id)
                st.session_state.session_id = data["session_id"]
                reply = data["response"]
            except requests.HTTPError as e:
                reply = f"Error {e.response.status_code}: {e.response.text}"
            except requests.RequestException as e:
                reply = f"Request failed: {e}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
