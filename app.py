import streamlit as st
import google.generativeai as genai
import random

st.set_page_config(page_title="할까말까 챗봇", page_icon="💭")

# --- 스타일 ---
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Nanum Gothic', sans-serif !important;
        background: #f7f7f7;
        color: #222;
    }
    .result-box {
        background: #fff;
        border-radius: 12px;
        border: 1.5px solid #eee;
        padding: 1.5em 1.2em;
        margin: 1.5em 0 1.2em 0;
        font-size: 1.08em;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    .vote-btn {
        width: 100%;
        font-size: 1.1em;
        font-weight: 600;
        border-radius: 8px;
        margin-bottom: 0.5em;
    }
    .vote-metric {
        font-size: 1.2em;
        font-weight: bold;
        color: #d32f2f;
        margin-top: 0.2em;
    }
    .comment-box {
        background: #fff0f0;
        border-radius: 8px;
        padding: 1em 1em;
        margin-top: 1.2em;
        color: #b22222;
        font-style: italic;
        font-size: 1.05em;
    }
    .stTextArea textarea {
        min-height: 120px;
        font-size: 1.08em;
    }
    </style>
    <link href="https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700&display=swap" rel="stylesheet">
    """,
    unsafe_allow_html=True
)

st.title("💭 할까말까 챗봇")
st.write("고민이 될 땐, AI에게 털어놔보세요!")

# --- 세션 상태 초기화 ---
if "yes_count" not in st.session_state:
    st.session_state["yes_count"] = 7
if "no_count" not in st.session_state:
    st.session_state["no_count"] = 5
if "vote_open" not in st.session_state:
    st.session_state["vote_open"] = False
if "last_comment" not in st.session_state:
    st.session_state["last_comment"] = ""
if "result" not in st.session_state:
    st.session_state["result"] = ""

# --- 랜덤 코멘트 리스트 ---
RANDOM_COMMENTS = [
    "고백은 해도 후회, 안 해도 후회래요. 그럼 고백하자!",
    "기다림도 답일 수 있어요.",
    "지금 아니면 언제 하겠어요?"
]

# --- Gemini API 키 설정 ---
genai.configure(api_key=st.secrets["gemini"]["api_key"])

def analyze_worry(worry_text):
    prompt = f"""
    사용자의 고민: {worry_text}

    아래 세 가지 항목에 대해 분석해줘:
    📍 현재 상황
    🧠 고민 핵심
    🎯 추천 조치

    각각 명확하게 구분해서 출력해줘.
    """
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip() if hasattr(response, "text") else str(response)

# --- 고민 입력 ---
user_input = st.text_area(
    "당신의 고민을 입력해주세요",
    placeholder="예: 썸남이 2일째 답이 없는데 고백할까?",
    key="worry_input"
)

analyze_btn = st.button("고민 분석하기", use_container_width=True)

if analyze_btn and user_input.strip():
    with st.spinner("AI가 고민을 분석 중입니다..."):
        st.session_state["result"] = analyze_worry(user_input)
        st.session_state["vote_open"] = False
        st.session_state["yes_count"] = 7
        st.session_state["no_count"] = 5
        st.session_state["last_comment"] = ""

# --- 분석 결과 출력 ---
if st.session_state["result"]:
    st.subheader("🔍 고민 분석 결과")
    st.markdown(f"<div class='result-box'>{st.session_state['result'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)

    # --- 고민 공개 및 투표 ---
    if not st.session_state["vote_open"]:
        if st.button("내 고민을 공개해서 남의 생각 들어보기 👀", use_container_width=True):
            st.session_state["vote_open"] = True
            st.session_state["last_comment"] = random.choice(RANDOM_COMMENTS)

    if st.session_state["vote_open"]:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            if st.button("✅ YES", key="yes_btn", use_container_width=True):
                st.session_state["yes_count"] += 1
            st.markdown(f"<div class='vote-metric'>YES: {st.session_state['yes_count']}</div>", unsafe_allow_html=True)
        with col2:
            if st.button("❌ NO", key="no_btn", use_container_width=True):
                st.session_state["no_count"] += 1
            st.markdown(f"<div class='vote-metric'>NO: {st.session_state['no_count']}</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='comment-box'>💬 {st.session_state['last_comment']}</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:2em;'></div>", unsafe_allow_html=True)
    if st.button("🔄 다시 입력하기", use_container_width=True):
        st.session_state["result"] = ""
        st.session_state["vote_open"] = False
        st.session_state["worry_input"] = ""
        st.session_state["yes_count"] = 7
        st.session_state["no_count"] = 5
        st.session_state["last_comment"] = ""
        st.experimental_rerun()
