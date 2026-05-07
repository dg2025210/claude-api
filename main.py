import streamlit as st
from anthropic import Anthropic

# ─────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🤖 Claude AI 질문하기",
    page_icon="🤖",
    layout="centered",
)

# ─────────────────────────────────────────────
# 커스텀 CSS (깔끔한 UI)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
    }
    .token-box {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .stChatMessage {
        border-radius: 10px;
    }
    /* 사이드바 스타일 */
    section[data-testid="stSidebar"] {
        background-color: #fafafa;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API 키 불러오기 (Streamlit Secrets)
# ─────────────────────────────────────────────
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    st.error("⚠️ API 키가 설정되지 않았습니다! Streamlit Cloud의 Secrets에 `ANTHROPIC_API_KEY`를 추가해주세요.")
    st.stop()

# Anthropic 클라이언트 생성
client = Anthropic(api_key=api_key)

# ─────────────────────────────────────────────
# 사용 가능한 모델 목록
# ─────────────────────────────────────────────
MODELS = {
    "Claude Sonnet 4 (빠르고 효율적)": "claude-sonnet-4-20250514",
    "Claude Opus 4 (가장 강력)": "claude-opus-4-20250514",
}

# ─────────────────────────────────────────────
# 사이드바 설정
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ 설정")

    # 모델 선택
    selected_model_name = st.selectbox(
        "🧠 AI 모델 선택",
        options=list(MODELS.keys()),
        index=0,
        help="Sonnet은 빠르고 저렴, Opus는 가장 똑똑합니다."
    )
    selected_model_id = MODELS[selected_model_name]

    st.caption(f"📌 모델 ID: `{selected_model_id}`")

    st.divider()

    # 시스템 프롬프트 설정
    system_prompt = st.text_area(
        "📝 시스템 프롬프트 (AI 역할 설정)",
        value="당신은 친절하고 유능한 AI 도우미입니다. 한국어로 답변해주세요. 학생들이 이해하기 쉽게 설명해주세요.",
        height=120,
    )

    # 최대 토큰 설정
    max_tokens = st.slider(
        "📏 최대 응답 길이 (토큰)",
        min_value=256,
        max_value=4096,
        value=1024,
        step=256,
        help="토큰이 클수록 긴 답변을 받을 수 있지만 비용이 증가합니다."
    )

    st.divider()

    # 누적 사용량 표시
    st.subheader("📊 누적 사용량")

    total_input = st.session_state.get("total_input_tokens", 0)
    total_output = st.session_state.get("total_output_tokens", 0)

    col1, col2 = st.columns(2)
    with col1:
        st.metric("입력 토큰", f"{total_input:,}")
    with col2:
        st.metric("출력 토큰", f"{total_output:,}")

    st.caption(f"💰 총 토큰: **{total_input + total_output:,}**")

    st.divider()

    # 대화 초기화 버튼
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["total_input_tokens"] = 0
        st.session_state["total_output_tokens"] = 0
        st.session_state["usage_history"] = []
        st.rerun()

# ─────────────────────────────────────────────
# 메인 화면
# ─────────────────────────────────────────────
st.markdown("<div class='main-header'>", unsafe_allow_html=True)
st.title("🤖 Claude AI에게 질문하기")
st.caption("Anthropic Claude API를 활용한 AI 질문 웹앱 | 당곡고등학교")
st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "total_input_tokens" not in st.session_state:
    st.session_state["total_input_tokens"] = 0

if "total_output_tokens" not in st.session_state:
    st.session_state["total_output_tokens"] = 0

if "usage_history" not in st.session_state:
    st.session_state["usage_history"] = []

# ─────────────────────────────────────────────
# 이전 대화 메시지 표시
# ─────────────────────────────────────────────
for msg in st.session_state["messages"]:
    role = msg["role"]
    content = msg["content"]
    avatar = "🧑‍🎓" if role == "user" else "🤖"
    with st.chat_message(role, avatar=avatar):
        st.markdown(content)

# ─────────────────────────────────────────────
# 사용자 입력 처리
# ─────────────────────────────────────────────
user_input = st.chat_input("궁금한 것을 질문해보세요! 예: '광합성이 뭐야?'")

if user_input:
    # 사용자 메시지 추가 & 표시
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(user_input)

    # AI 응답 생성
    with st.chat_message("assistant", avatar="🤖"):
        message_placeholder = st.empty()
        message_placeholder.markdown("⏳ 생각하는 중...")

        try:
            # Claude API 호출
            response = client.messages.create(
                model=selected_model_id,
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state["messages"]
                ],
            )

            # 응답 텍스트 추출
            assistant_text = response.content[0].text

            # 토큰 사용량 추출
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            # 누적 사용량 업데이트
            st.session_state["total_input_tokens"] += input_tokens
            st.session_state["total_output_tokens"] += output_tokens

            # 사용 기록 저장
            st.session_state["usage_history"].append({
                "model": selected_model_id,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            })

            # 응답 표시
            message_placeholder.markdown(assistant_text)

            # 이번 응답의 토큰 사용량 표시
            st.markdown("---")
            cols = st.columns(3)
            with cols[0]:
                st.info(f"📥 입력: **{input_tokens:,}** 토큰")
            with cols[1]:
                st.success(f"📤 출력: **{output_tokens:,}** 토큰")
            with cols[2]:
                st.warning(f"📊 합계: **{input_tokens + output_tokens:,}** 토큰")

            # 대화 기록에 저장
            st.session_state["messages"].append({
                "role": "assistant",
                "content": assistant_text,
            })

            # 사이드바 갱신을 위해 리런
            st.rerun()

        except Exception as e:
            error_msg = str(e)
            message_placeholder.empty()

            if "invalid_api_key" in error_msg or "authentication" in error_msg.lower():
                st.error("🔑 API 키가 올바르지 않습니다. Secrets 설정을 확인해주세요.")
            elif "rate_limit" in error_msg.lower():
                st.error("⏱️ API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요.")
            elif "overloaded" in error_msg.lower():
                st.error("🔥 현재 서버가 혼잡합니다. 잠시 후 다시 시도해주세요.")
            else:
                st.error(f"❌ 오류가 발생했습니다:\n\n```\n{error_msg}\n```")

            # 실패한 사용자 메시지 제거
            if st.session_state["messages"] and st.session_state["messages"][-1]["role"] == "user":
                st.session_state["messages"].pop()

# ─────────────────────────────────────────────
# 대화가 없을 때 안내 메시지
# ─────────────────────────────────────────────
if not st.session_state["messages"]:
    st.markdown("---")
    st.markdown(
        """
        ### 👋 안녕하세요! 사용법을 알려드릴게요.

        1. **왼쪽 사이드바**에서 AI 모델을 선택하세요.
           - **Sonnet 4**: 빠르고 효율적 (일반 질문에 추천)
           - **Opus 4**: 가장 강력 (복잡한 문제에 추천)

        2. 아래 **입력창**에 질문을 입력하세요.

        3. AI가 답변하면 **토큰 사용량**도 함께 확인할 수 있어요.

        ---

        💡 **질문 예시**:
        - "광합성 과정을 쉽게 설명해줘"
        - "이차방정식의 근의 공식을 유도해줘"
        - "영어 에세이 쓰는 법을 알려줘"
        - "파이썬으로 구구단 프로그램 만들어줘"
        """
    )

# ─────────────────────────────────────────────
# 하단 정보
# ─────────────────────────────────────────────
st.markdown("---")
st.caption("🏫 당곡고등학교 AI 학습 도우미 | Powered by Anthropic Claude API & Streamlit")
