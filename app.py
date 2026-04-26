import streamlit as st
import pandas as pd
import requests
import os

# 🔑 API KEY (use Streamlit Secrets)
API_KEY = os.getenv("API_KEY")

st.set_page_config(page_title="Eco Advisor", layout="wide")

# 🌿 ECO UI CSS
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #081c15, #1b4332, #2d6a4f);
}
[data-testid="stHeader"] {
    background: transparent !important;
}
section[data-testid="stSidebar"] {
    background-color: #081c15 !important;
}
div[style*="background-color:#ffffff"] {
    background-color: #d8f3dc !important;
}
div[style*="background-color:#ffffff"] * {
    color: black !important;
    opacity: 1 !important;
}
h1, h2, h3 {
    color: #ffffff !important;
    opacity: 1 !important;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# 📊 LOAD DATA
data = pd.read_csv("products.csv")
data["Name_clean"] = data["Name"].str.lower()

st.title("🌱 Sustainable Shopping Advisor")
st.markdown("### Smart Eco-Friendly Product Recommendations 🌍")

# 🔍 SIDEBAR
st.sidebar.header("🔍 Smart Filters")
category = st.sidebar.selectbox("Category", data["Category"].unique())
budget = st.sidebar.slider("Budget (₹)", 100, 5000, 1000)
search = st.sidebar.text_input("Search Product")
eco_filter = st.sidebar.checkbox("High Eco Score (>=7)")
organic_filter = st.sidebar.checkbox("Only Organic")

# FILTER LOGIC
if search:
    filtered = data[data["Name"].str.contains(search, case=False)]
    filtered = filtered[filtered["Price"] <= budget]
else:
    filtered = data[(data["Category"] == category) & (data["Price"] <= budget)]

if eco_filter:
    filtered = filtered[filtered["EcoScore"] >= 7]

if organic_filter:
    filtered = filtered[filtered["Organic"] == "Yes"]

filtered["Score"] = (filtered["EcoScore"] * 0.7) + ((5000 - filtered["Price"]) * 0.3 / 5000)
result = filtered.sort_values(by="Score", ascending=False)

# 🛍️ PRODUCTS
st.subheader("🌟 Top Recommendations")
cols = st.columns(3)

def reason(row):
    r = []
    if row["EcoScore"] >= 8:
        r.append("🌱 Highly Sustainable")
    if row["Organic"] == "Yes":
        r.append("🌿 Organic")
    if row["Recyclable"] == "Yes":
        r.append("♻️ Recyclable")
    return " | ".join(r)

def eco_badge(score):
    if score >= 8:
        return "🟢 Eco Friendly"
    elif score >= 5:
        return "🟡 Moderate"
    else:
        return "🔴 Not Eco"

for idx, (_, row) in enumerate(result.head(9).iterrows()):
    with cols[idx % 3]:
        st.markdown(f"""
        <div style="border-radius:20px;padding:20px;margin:10px 0;
        box-shadow: 0 6px 15px rgba(0,0,0,0.2);background-color:#ffffff;">
        <h4>🛍️ {row['Name']}</h4>
        <p><b>{eco_badge(row['EcoScore'])}</b></p>
        <p>💰 ₹{row['Price']}</p>
        <p>🌱 Eco Score: {row['EcoScore']}</p>
        <p>✅ {reason(row)}</p>
        </div>
        """, unsafe_allow_html=True)

# ================= CHATBOT =================
st.markdown("---")
st.subheader("💬 Ask Eco Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about sustainable shopping...")

def get_ai_response(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": "You are a STRICT Sustainable Shopping Advisor 🌱. Only answer eco-related queries."},
            {"role": "user", "content": user_input}
        ]
    }

    res = requests.post(url, headers=headers, json=payload)
    return res.json()["choices"][0]["message"]["content"]

def is_valid_query(user_input):
    allowed = ["eco","sustainable","organic","product","soap","clothes","gift","shoes","environment","green"]
    return any(word in user_input.lower() for word in allowed)

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    if not is_valid_query(user_input):
        reply = "❌ I only help with sustainable shopping 🌱"
    else:
        reply = get_ai_response(user_input)

    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant"):
        st.markdown(reply)