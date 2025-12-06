import streamlit as st
from openai import OpenAI
from datetime import datetime
import random
import re

client = OpenAI(api_key="xxxxxxxxxxx")  # Apni API key yaha daalna
st.set_page_config(page_title="Chatbot", layout="wide")

# --- CSS ---
st.markdown("""
<style>
html, body { overflow: hidden !important; }
.stApp { background: pink; overflow: hidden; }

/* Chat area normal scroll (top → bottom) */
.chat-box {
    height: 80vh;
    overflow-y: auto;
    padding: 10px 15px;
    display: flex;
    flex-direction: column;
}

/* User bubble */
.user {
    max-width: 60%;
    padding: 10px 14px;
    background: #d6ffcb;
    border-radius: 12px;
    margin: 10px 0;
    float: right;
    clear: both;
    font-weight: 700;     /* BOLD */
}

/* Bot bubble */
.bot {
    max-width: 60%;
    padding: 10px 14px;
    background: #ffffff;
    border-radius: 12px;
    margin: 10px 0;
    float: left;
    clear: both;
    font-weight: 700;     /* BOLD */
}

/* Below input padding */
.block-container { padding-bottom: 70px !important; }

/* Input Box Colour Change (Soft English Blue) */
.stChatInput textarea {
    background-color: #e6f0ff !important;
    border-radius: 10px !important;
}

/* Small expander label fix */
.stExpanderHeader { font-size: 24px !important; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- SESSION ---
if "chat" not in st.session_state:
    st.session_state.chat = []
if "reminders" not in st.session_state:
    st.session_state.reminders = []

# --- CHAT AREA ---
st.markdown("<div class='chat-box'>", unsafe_allow_html=True)
for role, text in st.session_state.chat:
    bubble = "user" if role == "you" else "bot"
    st.markdown(f"<div class='{bubble}'>{text}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

# --- USER INPUT ---
user_msg = st.chat_input("Type your message...")

if user_msg:
    st.session_state.chat.append(("you", user_msg))
    
    # --- Advanced Reminder Feature ---
    if "remind me to" in user_msg.lower():
        match = re.search(r'remind me to (.+?) at (\d{1,2}:\d{2})', user_msg.lower())
        if match:
            task = match.group(1).strip()
            time = match.group(2)
        else:
            task = user_msg.split("remind me to")[-1].strip()
            time = datetime.now().strftime("%H:%M")

        st.session_state.reminders.append(f"{time} - {task}")
        reply = f"✅ Reminder set: {task} at {time}"

    # --- Joke Feature ---
    elif "tell me a joke" in user_msg.lower():
        jokes = [
            "Why did the computer go to the doctor? Because it caught a virus!",
            "Why was the math book sad? Because it had too many problems!",
            "Why don’t programmers like nature? Too many bugs."
        ]
        reply = random.choice(jokes)

    # --- Normal GPT reply ---
    else:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_msg}]
        )
        reply = res.choices[0].message.content

    st.session_state.chat.append(("bot", reply))
    st.rerun()

# --- EXPANDER FOR OPTIONS (Small 3 dots) ---
with st.expander("⋮", expanded=False):
    
    # Reminders display
    if st.session_state.reminders:
        st.markdown("### ⏰ Your Reminders:")
        for r in st.session_state.reminders:
            st.write(r)

    # Clear reminders button
    if st.button("❌ Clear Reminders"):
        st.session_state.reminders = []
        st.success("All reminders cleared!")

    # Export chat button
    if st.button("📥 Export Chat"):
        chat_text = "\n".join([f"{role}: {text}" for role, text in st.session_state.chat])
        st.download_button("Download Chat", data=chat_text, file_name="chat_history.txt")

    # Clean chat button
    if st.button("🧹 Clean Chat"):
        st.session_state.chat = []
        st.success("Chat cleared! Start fresh now.")
        st.rerun()
