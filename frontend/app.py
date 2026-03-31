"""Retail Chat Agent Streamlit Frontend."""

import base64
import os

import requests
import streamlit as st


def _render_products(products: list[dict]) -> None:
    """Render product cards (image + name + link) below an assistant message."""
    if not products:
        return
    cols = st.columns(min(len(products), 3))
    for i, p in enumerate(products):
        image_url = p.get("image_url")
        name = p.get("name") or "Product"
        product_url = p.get("product_url")
        with cols[i % 3]:
            if image_url:
                st.image(image_url, use_container_width=True)
            if product_url:
                st.markdown(f"[{name}]({product_url})")
            else:
                st.caption(name)


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


def fetch_history(session_id: str) -> list[dict]:
    try:
        r = requests.get(f"{BACKEND_URL}/api/v1/sessions/{session_id}", timeout=10)
        if r.ok:
            return r.json().get("messages", [])
    except requests.RequestException:
        pass
    return []


if "session_id" not in st.session_state:
    # Re-hydrate from the URL on refresh
    qp_session = st.query_params.get("session_id")
    if qp_session:
        history = fetch_history(qp_session)
        if history:
            st.session_state.session_id = qp_session
            st.session_state.messages = history
        else:
            st.session_state.session_id = None
            st.session_state.messages = []
    else:
        st.session_state.session_id = None
        st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("image"):
            st.image(base64.b64decode(msg["image"]), width=260)
        st.markdown(msg["content"])
        _render_products(msg.get("products", []))

with st.sidebar:
    st.header("Options")
    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.session_state.session_id = None
        st.query_params.clear()
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

    products: list[dict] = []
    with st.chat_message("assistant"):
        with st.spinner("Thinking…"):
            try:
                data = send_message(prompt, image_b64, st.session_state.session_id)
                if st.session_state.session_id != data["session_id"]:
                    st.session_state.session_id = data["session_id"]
                    st.query_params["session_id"] = data["session_id"]
                reply = data["response"]
                products = data.get("products", [])
            except requests.HTTPError as e:
                reply = f"Error {e.response.status_code}: {e.response.text}"
            except requests.RequestException as e:
                reply = f"Request failed: {e}"
        st.markdown(reply)
        _render_products(products)

    st.session_state.messages.append({"role": "assistant", "content": reply, "products": products})
