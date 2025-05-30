import streamlit as st
import os
from typing import List

# 1. set_page_config()는 무조건 가장 먼저 호출해야 합니다.
st.set_page_config(page_title="Gemini 3단계 조언 챗봇", layout="centered")

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# Gemini API 키 가져오기 (환경변수 or streamlit secrets)
def get_gemini_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if not key and "GEMINI_API_KEY" in st.secrets:
        key = st.secrets["GEMINI_API_KEY"]
    return key

# Gemini 모델 호출 함수
def gemini_generate(prompt: str, previous_ideas: List[str] = None) -> str:
    api_key = get_gemini_api_key()
    if not api_key:
        st.error("🔑 Gemini API 키가 설정되어 있지 않습니다. 환경변수 또는 secrets.toml에 등록해주세요.")
        st.stop()
    if genai is None:
        st.error("📦 google-generativeai 패키지가 설치되어 있지 않습니다. 'pip install google-generativeai'를 실행하세요.")
        st.stop()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    if previous_ideas:
        prompt += f"\n\n이미 제안된 아이디어: {previous_ideas}\n이와 중복되지 않는 새로운 관점 또는 아이디어를 제안해 주세요."
    response = model.generate_content(prompt)
    return response.text.strip() if hasattr(response, "text") else str(response)

# 3단계 조언 프롬프트 생성
def build_advice_prompt(user_input: str) -> str:
    return f"""
아래 사용자의 고민/상황에 대해 3단계로 조언을 해주세요.
1. 상황 해석: 사용자의 상황을 객관적으로 해석
2. 감정 파악: 사용자의 감정이나 심리적 상태를 추론
3. 추천 액션: 실질적으로 도움이 될 만한 구체적 행동이나 시각을 제안

고민/상황: {user_input}

각 단계별로 제목과 내용을 명확히 구분해서 작성해 주세요.
"""

# CSS 스타일 (UI 꾸미기)
st.markdown(
    """
    <style>
    @font-face {
            font-family: 'GmarketSansMedium';
            src: url('https://fastly.jsdelivr.net/gh/projectnoonnu/noonfonts_2001@1.1/GmarketSansMedium.woff') format('woff');
            font-weight: normal;
            font-style: normal;
        }

        html, body {
        font-family: 'GmarketSansMedium', 'Nanum Gothic', 'Malgun Gothic', 'Apple SD Gothic Neo', Arial, sans-serif !important;
        }
        .main {
            background-color: #fff9f5;
            color: #4b3b2b;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        }
        .title {
            color: #d2691e;
            font-weight: 700;
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        textarea {
            border-radius: 8px;
            border: 1.5px solid #d2691e;
            padding: 10px;
            font-size: 1.1rem;
            color: #5a3e1b;
        }
        .stButton > button {
            background-color: #d2691e;
            color: white;
            font-weight: 600;
            border-radius: 8px;
            padding: 0.6rem 1rem;
            border: none;
            transition: background-color 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #b05214;
            cursor: pointer;
        }
        .reset-btn > button {
            background-color: #e04e00 !important;
            font-weight: 700 !important;
            font-size: 1.1rem !important;
            border-radius: 12px !important;
            padding: 0.8rem 1.2rem !important;
        }
        .reset-btn > button:hover {
            background-color: #b63a00 !important;
        }
        .advice-box {
            background-color: #fff3e6;
            border-left: 6px solid #d2691e;
            padding: 1rem 1.2rem;
            margin-top: 1rem;
            border-radius: 10px;
            box-shadow: 0 2px 6px rgb(210 105 30 / 0.3);
            white-space: pre-line;
        }
        .idea-box {
            background-color: #fff6f0;
            border-left: 6px solid #b05214;
            padding: 0.8rem 1rem;
            margin-top: 1rem;
            border-radius: 8px;
            font-style: italic;
            color: #7a4a22;
            white-space: pre-line;
        }
        .interaction-text {
            color: #7a4a22;
            font-size: 0.95rem;
            margin-top: 0.8rem;
            margin-bottom: 0.2rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 제목 및 설명
st.markdown('<h1 class="title">🧠 Gemini 3단계 조언 챗봇</h1>', unsafe_allow_html=True)
st.markdown("""
<p>당신의 고민이나 기분을 입력하면, Gemini AI가 <strong>상황 해석 → 감정 파악 → 추천 액션</strong>의 3단계로 따뜻하게 조언해 드립니다.</p>
<ul>
<li>‘분석 시작’ 버튼을 눌러 AI의 조언을 받아보세요.</li>
<li>조언이 끝난 후, 더 다양한 시각이 필요하면 ‘더 다른 시각이 듣고 싶나요?’ 버튼을 눌러 새로운 아이디어를 추가할 수 있습니다.</li>
<li>‘주제 초기화 및 새로 시작’ 버튼은 언제든지 모든 내용을 초기화합니다.</li>
</ul>
""", unsafe_allow_html=True)

# 세션 상태 초기화 함수
def reset_state():
    st.session_state["user_input"] = ""
    st.session_state["advice"] = ""
    st.session_state["ideas"] = []
    st.session_state["extra_ideas"] = []
    st.session_state["show_advice"] = False
    st.session_state["error"] = ""

# 최초 초기화
if "user_input" not in st.session_state:
    reset_state()

# 사용자 입력창
user_input = st.text_area(
    "지금의 기분이나 고민을 자유롭게 입력해 주세요",
    value=st.session_state["user_input"],
    key="user_input_input",
    height=130,
)

# 버튼 배치
col1, col2 = st.columns([1,1])
with col1:
    analyze_btn = st.button("분석 시작", use_container_width=True)
with col2:
    reset_btn = st.button("주제 초기화 및 새로 시작", key="reset_btn", use_container_width=True, help="입력과 결과를 모두 초기화합니다.")

# 리셋 버튼 클릭시 상태 초기화 및 리로드
if reset_btn:
    reset_state()
    st.experimental_rerun()

# 분석 시작 버튼 클릭시
if analyze_btn and user_input.strip():
    with st.spinner("Gemini가 3단계로 분석 중..."):
        prompt = build_advice_prompt(user_input)
        try:
            advice = gemini_generate(prompt)
            st.session_state["advice"] = advice
            st.session_state["ideas"] = [advice]
            st.session_state["extra_ideas"] = []
            st.session_state["show_advice"] = True
        except Exception as e:
            st.session_state["error"] = str(e)
            st.session_state["show_advice"] = False

# 분석 결과 보여주기
if st.session_state["show_advice"] and st.session_state["advice"]:
    st.markdown("---")
    st.markdown('<div class="advice-box">', unsafe_allow_html=True)
    st.subheader("🔎 3단계 분석 결과")
    st.markdown(st.session_state["advice"].replace("\n", "<br>"), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 추가 아이디어 출력
    for idx, idea in enumerate(st.session_state["extra_ideas"], 1):
        formatted_idea = idea.replace("\n", "<br>")
        st.markdown(f'<div class="idea-box"><strong>💡 추가 아이디어 #{idx}</strong><br>{formatted_idea}</div>', unsafe_allow_html=True)


    # 추가 아이디어 요청 버튼 및 안내
    st.markdown('<p class="interaction-text">더 다양한 시각이 궁금하다면, 아래 버튼을 눌러보세요!</p>', unsafe_allow_html=True)
    more_idea_btn = st.button("더 다른 시각이 듣고 싶나요?", use_container_width=True)

    if more_idea_btn:
        with st.spinner("새로운 시각을 생성 중..."):
            try:
                extra_idea = gemini_generate(user_input, previous_ideas=st.session_state["ideas"] + st.session_state["extra_ideas"])
                st.session_state["extra_ideas"].append(extra_idea)
            except Exception as e:
                st.error(f"추가 아이디어 생성 중 오류가 발생했습니다: {e}")
