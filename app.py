
import os
import streamlit as st
from groq import Groq

# ---------------- PAGE SETTINGS ----------------
st.set_page_config(
    page_title="Prompt Engineering AI",
    page_icon="🤖",
    layout="wide"
)

# ---------------- DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background-color: #f5f7fb;
}
.main-title {
    text-align: center;
    color: #4f46e5;
    font-size: 38px;
    font-weight: 800;
}
.subtitle {
    text-align: center;
    color: #64748b;
    font-size: 17px;
}
div.stButton > button {
    background-color: #4f46e5;
    color: white;
    border-radius: 10px;
    min-height: 45px;
    width: 100%;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="main-title">🤖 Prompt Engineering AI</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Turn simple ideas into '
    'professional prompts and useful AI answers.</div>',
    unsafe_allow_html=True
)

st.divider()

# ---------------- API CONFIGURATION ----------------
api_key = os.environ.get("GROQ_API_KEY", "")

try:
    if not api_key:
        api_key = st.secrets.get("GROQ_API_KEY", "")
except Exception:
    pass

if not api_key:
    st.error(
        "AI API key is missing. Add GROQ_API_KEY "
        "in Streamlit Cloud Settings > Secrets."
    )
    st.info(
        "Local testing: set GROQ_API_KEY in your "
        "terminal before starting the app."
    )
    st.stop()

client = Groq(api_key=api_key)

# Use a model available to your Groq account.

MODEL = "openai/gpt-oss-20b"



# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("⚙️ Settings")

    purpose = st.selectbox(
        "Choose your purpose",
        [
            "Education",
            "Coding",
            "Content Writing",
            "Research",
            "Business",
            "General"
        ]
    )

    level = st.selectbox(
        "Explanation level",
        ["Beginner", "Intermediate", "Advanced"]
    )

    language = st.selectbox(
        "Answer language",
        ["English", "Telugu", "Simple English"]
    )

    if st.button("🗑️ Clear Chat"):
        for key in [
            "original_prompt",
            "improved_prompt",
            "ai_answer"
        ]:
            st.session_state.pop(key, None)
        st.rerun()

# ---------------- USER INPUT ----------------
st.subheader("✍️ Enter Your Prompt")

user_prompt = st.text_area(
    "What do you want the AI to do?",
    placeholder=(
        "Example: Explain artificial intelligence "
        "with simple examples and applications."
    ),
    height=140
)

# ---------------- IMPROVE PROMPT ----------------
if st.button("✨ Improve Prompt and Get Answer"):
    if not user_prompt.strip():
        st.warning("Please enter a prompt first.")
    else:
        try:
            with st.spinner("Creating your professional prompt..."):
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert prompt engineer. "
                                "Rewrite the user's request into a "
                                "clear, detailed, effective prompt. "
                                "Include the role, objective, context, "
                                "constraints and expected output format "
                                "when appropriate. Preserve the original "
                                "intention. Return only the improved prompt."
                            )
                        },
                        {
                            "role": "user",
                            "content": (
                                f"Purpose: {purpose}\n"
                                f"Level: {level}\n"
                                f"Preferred answer language: {language}\n"
                                f"Original request: {user_prompt}"
                            )
                        }
                    ],
                    temperature=0.4
                )

            improved = (
                response.choices[0].message.content or ""
            ).strip()

            if not improved:
                st.error("The AI returned an empty prompt. Try again.")
            else:
                st.session_state["original_prompt"] = user_prompt
                st.session_state["improved_prompt"] = improved
                st.session_state["purpose"] = purpose
                st.session_state["level"] = level
                st.session_state["language"] = language
                st.session_state.pop("ai_answer", None)

        except Exception as error:
            st.error(f"Prompt generation failed: {error}")

# ---------------- SHOW IMPROVED PROMPT ----------------
if "improved_prompt" in st.session_state:
    st.divider()
    st.subheader("📝 1. Your Professional Prompt")

    st.code(
        st.session_state["improved_prompt"],
        language=None
    )

    st.download_button(
        "📥 Download Improved Prompt",
        data=st.session_state["improved_prompt"],
        file_name="improved_prompt.txt",
        mime="text/plain"
    )

    # ---------------- GENERATE ANSWER ----------------
    st.divider()
    st.subheader("💬 2. AI Answer")

    if st.button("🚀 Generate Answer"):
        try:
            with st.spinner("AI is generating your answer..."):
                answer_response = client.chat.completions.create(
                    model=MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful AI assistant. "
                                "Answer the supplied prompt clearly, "
                                "accurately and with useful details. "
                                "Use headings, steps and examples when "
                                "appropriate. Match this explanation "
                                "level: "
                                + st.session_state.get("level", "Beginner")
                                + ". Reply in this language: "
                                + st.session_state.get("language", "English")
                                + ". If uncertain, be honest."
                            )
                        },
                        {
                            "role": "user",
                            "content": st.session_state["improved_prompt"]
                        }
                    ],
                    temperature=0.5
                )

            answer = (
                answer_response.choices[0].message.content or ""
            ).strip()

            if answer:
                st.session_state["ai_answer"] = answer
            else:
                st.error("The AI returned an empty answer. Try again.")

        except Exception as error:
            st.error(f"Answer generation failed: {error}")

    # ---------------- SHOW ANSWER ----------------
    if "ai_answer" in st.session_state:
        st.markdown(st.session_state["ai_answer"])

        st.download_button(
            "📥 Download AI Answer",
            data=st.session_state["ai_answer"],
            file_name="ai_answer.txt",
            mime="text/plain"
        )

st.divider()
st.caption("Built with Python, Streamlit and Groq Cloud AI")
