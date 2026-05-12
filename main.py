import streamlit as st
from anthropic import Anthropic

# ─────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="🧠 MBTI & SBTI 성격 검사",
    page_icon="🧠",
    layout="centered",
)

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0;
    }
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .token-info {
        background-color: #e8f4f8;
        padding: 0.8rem;
        border-radius: 8px;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API 키
# ─────────────────────────────────────────────
try:
    api_key = st.secrets["ANTHROPIC_API_KEY"]
except Exception:
    st.error("⚠️ API 키가 설정되지 않았습니다! Streamlit Cloud의 Secrets에 `ANTHROPIC_API_KEY`를 추가해주세요.")
    st.stop()

client = Anthropic(api_key=api_key)

# ─────────────────────────────────────────────
# SBTI 문항 데이터
# ─────────────────────────────────────────────
SBTI_QUESTIONS_TEXT = """
제1문 [사회-친밀욕구]
믿는 사람이랑은 진짜 가까워지고 싶어, 잃어버린 가족 만난 것처럼.
A) 동의  B) 중립  C) 비동의

제2문 [자아-자기수용]
난 찐따일 뿐만 아니라, 조커이고, 건어물녀남이야. 평생 연애 한 번 못 해봤어. 소심하고 자존감 바닥이고, 내 청춘은 망상의 연속이야. 매일 나도 같이 길 걸어주고, 쇼핑하고, 놀아줄 사람이 있으면 좋겠다고 상상해. 현실은 부모님 돈 다 써버리고, 구린 학교 나와서, 대충 살다가 취직한 꿈도 목표도 능력도 없는 3무 인간. 온라인에서 찐따 드립치는 거 볼 때마다 울고 싶어.
A) 나 울었어..  B) 이게 뭐야..  C) 이건 내가 아니야!

제3문 [행동-계획성]
난 보통 계획을 세우는데, ____
A) 근데 계획은 변화를 못 따라가.  B) 될 때도 있고, 안 될 때도 있고.  C) 계획 깨지는 거 진짜 싫어.

제4문 [사회-사회적거리]
나랑 사귀는 건 전기 울타리 수준이야. 너무 가까이 오면 자동으로 경보 울림.
A) 동의  B) 중립  C) 비동의

제5문 [자아-자아일관성]
남들이 뭐라 하든 1도 신경 안 써.
A) 비동의  B) 중립  C) 동의

제6문 [감정-감정표현]
하늘에 맹세코, 모든 연애에 진심이었다고!
A) 아닌데  B) 글쎄?  C) 맞아! (당당한 표정)

제7문 [사회-사회적거리]
친구가 자기 친구를 데려왔어. 네 반응은?
A) "친구의 친구"한테 본능적으로 좀 거리감  B) 상대 보고, 맞으면 놀지 뭐.  C) 친구의 친구는 내 친구지! 열정적으로 떠들어야지

제8문 [사회-독립성]
연애 시작했는데, 상대가 엄청 집착해. 어떻게 느껴?
A) 완전 좋지  B) 뭐 상관없어  C) 나만의 공간이 더 좋아

제9문 [감정-정서안정]
연애할 때 상대에게 버림받을까 자주 걱정돼.
A) 응  B) 가끔  C) 아니

제10문 [자아-자기수용]
가끔 어떤 일에 부정적인 생각이 있는데 결국 말 안 할 때가 있잖아. 대부분의 이유는:
A) 그런 경우 별로 없어.  B) 체면이나 관계 때문에 그런 듯.  C) 내가 어두운 사람인 거 들키기 싫어서.

제11문 [행동-실행력]
남들이 "실행력 쩐다"고 하면, 속마음은?
A) 마감에 몰리면 진짜 실행력 미쳐...  B) 아, 가끔은 그런가.  C) 맞아, 일이란 건 원래 밀고 나가야지.

제12문 [자아-자기인식]
난 부족해, 주변 사람들이 다 나보다 잘나.
A) 맞아  B) 가끔  C) 아닌데

제13문 [행동-목표지향]
뭔가를 할 때 성과와 성장이 목적이지, 귀찮은 일이나 위험을 피하려는 게 아니야.
A) 비동의  B) 중립  C) 동의

제14문 [태도-개방성]
이 문제에는 지문이 없어. 눈 감고 골라.
A) 깊이 고민해보니 A인 것 같은데?  B) 음, B로 할까?  C) 모르면 C지?

제15문 [행동-목표지향]
반드시 계속 올라가고, 더 강해져야 해.
A) 비동의  B) 중립  C) 동의

제16문 [행동-실행력]
뭘 하든 보통 목표가 있어.
A) 비동의  B) 중립  C) 동의

제17문 [태도-낙관성]
어느 날 갑자기 깨달았어. 인생에 무슨 개같은 의미가 있냐고. 인간은 동물처럼 욕망에 지배당하는, 순전히 호르몬에 조종되는 존재잖아. 배고프면 먹고, 졸리면 자고, 발정나면 짝짓기하고. 우리 진짜 짐승이랑 다를 게 뭐야.
A) 맞는 말이야.  B) 맞을 수도, 아닐 수도.  C) 완전 헛소리야.

제18문 [감정-감정표현]
변비로 변기에 앉은 지 30분째. 안 나와서 고통스러워. 이때 넌?
A) 30분 더 앉아보자. 혹시 나올지도.  B) 엉덩이 때리면서 "야 이 엉덩아, 빨리 싸!"  C) 관장약 써서 빨리 끝내자.

제19문 [사회-친밀욕구]
게임하다가 사귄 온라인 친구들이 오프 모임에 초대했어. 어떻게 생각해?
A) 온라인으로 떠드는 건 괜찮은데, 직접 만나긴 좀 떨려.  B) 만나는 것도 괜찮지, 누가 오든 대화는 하지.  C) 꾸미고 가서 열정적으로 떠들 거야. 혹시 모르잖아, 혹시?

제20문 [태도-신뢰성]
대부분의 사람은 착해.
A) 사실 사악한 인간이 세상 치질보다 많아.  B) 글쎄.  C) 응, 착한 사람이 더 많다고 믿고 싶어.

제21문 [감정-공감력]
네 연애 상대가 어른 공경하고, 아이 사랑하고, 다정하고, 청렴하고, 의리 있고, 말 잘하고, 관찰력 좋고, 박학다식하고, 상냥하고, 마음 착하고, 의욕 넘치고, 외모까지 완벽한 사람이야. 이때 넌?
A) 아무리 완벽해도 깊이 빠지진 않을 거야.  B) A와 C 사이 어딘가.  C) 엄청 소중히 할 거고, 연애 바보가 될 수도.

제22문 [태도-개방성]
관습을 깨는 게 좋아. 구속당하는 건 싫어.
A) 동의  B) 중립  C) 비동의

제23문 [자아-자기인식]
내 마음속에 진심으로 추구하는 게 있어.
A) 비동의  B) 중립  C) 동의

제24문 [사회-독립성]
어떤 관계에서든 개인 공간을 중시해.
A) 서로 의지하는 게 더 좋아  B) 상황에 따라  C) 맞아! (단호하게)

제25문 [행동-계획성]
결정은 빠르게 내려. 우유부단한 건 싫어.
A) 비동의  B) 중립  C) 동의

제26문 [태도-신뢰성]
상대가 5시간 넘게 답장 없다가 배탈 났다고 하면, 어떻게 생각해?
A) 배탈이 5시간이나? 뭔가 숨기는 거 아냐.  B) 믿음과 의심 사이에서 흔들려.  C) 오늘 진짜 몸이 안 좋았나 보지.

제27문 [자아-자아일관성]
사람마다 다른 모습을 보여줘.
A) 비동의  B) 중립  C) 동의

제28문 [감정-정서안정]
시험 코앞인데, 학교에서 야간 자율학습 필수에 빠지면 벌점이야. 근데 오늘 밤 이상형이랑 배그 하기로 했어. 어떡해?
A) 빼! 한 번쯤이야!  B) 그냥 조퇴하자.  C) 시험인데 뭘 빼, 공부해야지.

제29문 [자아-자기인식]
진짜 내가 어떤 사람인지 잘 알고 있어.
A) 비동의  B) 중립  C) 동의

제30문 [태도-낙관성]
난 가끔 세상이 다 부질없다고 느껴.
A) 동의  B) 중립  C) 비동의

보너스 [히든유형 판별]
평소 취미가 뭐야?
A) 먹고 자고 기본 생활  B) 예술/창작 취미  C) 음주  D) 운동
"""

SBTI_TYPES_TEXT = """
[주도/행동형]
CTRL(장악자), BOSS(리더), GOGO(직진러), SEXY(매력괴물), JOKE-R(광대)

[관계/감정형]
LOVE-R(연애뇌), MUM(엄마), THAN-K(감사쟁이), MALO(원숭이), OH-NO(헉쟁이), WOC!(헐쟁이)

[냉소/일상형]
Dior-s(찐따), SHIT(욕쟁이), OJBK(아무거나인간), ZZZZ(죽은척러), POOR(가난뱅이), MONK(중), IMSB(바보), ATM(현금인출기), FAKE(가면인간), THIN-K(생각쟁이), SOLO(고아), FUCK(씹러), DEAD(사망자), IMFW(폐인)

[히든 유형]
DRUNK(취객) — 보너스에서 음주 선택 시
HHHH(???) — 극단적 응답 패턴 시
"""

# ─────────────────────────────────────────────
# 시스템 프롬프트
# ─────────────────────────────────────────────
SBTI_SYSTEM_PROMPT = f"""너는 SBTI(Satirical Behavioral Type Indicator, 풍자적 행동 유형 지표) 검사를 진행하는 AI 검사관이야.

## 검사 진행 단계

### [1단계: 문항 진행]
1. 사용자에게 SBTI 문항을 채팅 대화로 하나씩 제시해.
2. 문항 제시할 때 질문 내용과 선택지(A/B/C)를 보여줘.
3. 사용자가 답하면 짧고 재미있는 리액션 + 다음 문항.
4. "이전" → 직전 문항 다시 제시, 다시 답변 가능.
5. "제출" → 현재까지 응답 기반으로 바로 2단계로.
6. 30문항 + 보너스 1문항 = 31문항 끝나면 자동으로 2단계.
7. MZ세대 말투로 짧은 리액션, 드립, 공감. 너무 길지 않게.
8. 진행 상황(예: "5/31") 표시.

### [2단계: 결과 발표]
모든 문항이 끝나거나 "제출" 시:
- 유형코드와 별명만 짧게 알려줘.
- 형식:

🎭 **검사 완료!**
# 너의 SBTI 유형은... [유형코드] ([별명])!

궁금한 거 있으면 뭐든 물어봐! 예를 들면:
- "팩폭 해줘" → 뼈 때리는 풍자 분석
- "궁합 알려줘" → 잘 맞는/안 맞는 유형
- "5대 모델 분석" → 상세 심리 모델 결과
- "장점/단점" → 이 유형의 특징
- "한 줄 요약" → 킬러 한 마디
- 그 외 아무거나!

⚠️ 절대로 유형코드+별명 외의 상세 분석, 궁합, 모델 분석 등을 자동으로 보여주지 마. 사용자가 물어볼 때만 답해.

### [3단계: 자유 대화]
- 사용자가 궁금한 걸 물어보면 그때그때 답해줘.
- "팩폭" → 풍자적이고 뼈 때리는 분석 3-5문단. 독설+애정+유머. MZ세대 말투.
- "궁합" → 찰떡궁합, 좋은 궁합, 최악의 궁합 각각 유형코드+별명+이유.
- "5대 모델" 또는 "모델 분석" → 5대 모델별 L/M/H 결과와 해석을 표로.
- "장점" → 이 유형의 장점 2-3개.
- "단점" → 이 유형의 단점 2-3개.
- "한 줄 요약" → 킬러 문장 하나.
- 다른 질문에도 유형 기반으로 재미있게 답해줘.
- 항상 풍자적이고 재미있는 SBTI 말투 유지.

## SBTI 문항 데이터
{SBTI_QUESTIONS_TEXT}

## SBTI 유형 목록
{SBTI_TYPES_TEXT}

## L/M/H 매핑 규칙
대부분: A=L, B=M, C=H
역코딩: 제1문(A=H), 제2문(A=H), 제4문(A=H), 제9문(A=H), 제22문(A=H), 제30문(A=L,C=H → 동의=낙관성 낮음)

## 5대 모델 × 3차원
자아: 자기인식, 자기수용, 자아일관성
감정: 정서안정, 감정표현, 공감력
태도: 낙관성, 신뢰성, 개방성
행동: 실행력, 목표지향, 계획성
사회: 친밀욕구, 사회적거리, 독립성

## 히든 유형
- DRUNK(취객): 보너스에서 C(음주) 선택
- HHHH(???): 85% 이상 같은 선택지

## 첫 메시지
1. 짧고 재미있게 인사
2. SBTI 한두 줄 설명
3. 사용법: A/B/C로 답, "이전"=이전문항, "제출"=바로결과
4. 바로 제1문 제시
"""

MBTI_SYSTEM_PROMPT = """당신은 MBTI 성격 유형 전문 분석가입니다.

## 검사 진행 단계

### [1단계: 대화형 질문]
1. 사용자에게 자연스러운 대화형 질문을 하나씩 해서 E/I, S/N, T/F, J/P를 파악.
2. 질문은 한 번에 하나만. 일상적이고 재미있는 상황 질문.
3. 총 8~12개 질문 후 파악되면 2단계로.
4. "이전" → 직전 질문 다시.
5. "제출" → 현재까지 파악한 것 기반으로 바로 2단계로.
6. MZ세대 말투로 친근하게.

### [2단계: 결과 발표]
유형코드와 별명만 짧게 알려줘:

🔮 **검사 완료!**
# 너의 MBTI는... [4글자코드] ([별명])!

궁금한 거 있으면 뭐든 물어봐! 예를 들면:
- "상세 분석" → 유형 상세 설명
- "궁합 알려줘" → 잘 맞는/안 맞는 유형
- "4가지 지표 분석" → E/I, S/N, T/F, J/P 상세
- "장점/단점"
- "한 줄 요약"
- 그 외 아무거나!

⚠️ 절대로 유형코드+별명 외의 내용을 자동으로 보여주지 마. 사용자가 물어볼 때만 답해.

### [3단계: 자유 대화]
사용자가 물어보는 것에 맞춰 답해줘:
- "상세 분석" → 3-4문단 재미있는 분석
- "궁합" → 찰떡/좋은/최악 궁합 유형+이유
- "지표 분석" → 4가지 지표별 결과 표
- "장점" → 2-3개
- "단점" → 2-3개
- "한 줄 요약" → 킬러 문장
- 다른 질문에도 유형 기반으로 재미있게.
- 항상 친근한 MZ 말투 유지.

## 첫 메시지
인사 + MBTI 대화형 검사 설명 + "이전"/"제출" 안내 + 첫 질문
한국어, 반말로."""

# ─────────────────────────────────────────────
# 세션 상태
# ─────────────────────────────────────────────
defaults = {
    "page": "home",
    "test_type": None,
    "messages": [],
    "started": False,
    "total_input_tokens": 0,
    "total_output_tokens": 0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def reset_test():
    st.session_state["page"] = "home"
    st.session_state["test_type"] = None
    st.session_state["messages"] = []
    st.session_state["started"] = False


# ─────────────────────────────────────────────
# 홈 페이지
# ─────────────────────────────────────────────
def show_home():
    st.markdown("<p class='main-title'>🧠 성격 유형 검사</p>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>AI와 대화하며 알아보는 나의 성격 유형</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### 🔮 MBTI 검사")
        st.markdown("""
        **16가지 성격 유형**

        AI와 자연스럽게 대화하면서
        당신의 MBTI를 알아보세요!

        - 🗣️ AI가 질문하고 분석
        - 💬 자유로운 대화형 검사
        - ❓ 결과 후 궁금한 건 직접 질문!
        """)
        if st.button("🔮 MBTI 검사 시작", use_container_width=True, key="btn_mbti"):
            st.session_state["page"] = "test"
            st.session_state["test_type"] = "mbti"
            st.session_state["messages"] = []
            st.session_state["started"] = False
            st.rerun()

    with col2:
        st.markdown("### 🎭 SBTI 검사")
        st.markdown("""
        **27가지 풍자적 유형**

        AI와 대화하며 30문항에 답하고
        결과 후 원하는 것만 골라 질문!

        - 💬 AI가 문항을 대화로 제시
        - ⬅️ "이전" 입력하면 수정 가능
        - ❓ 팩폭, 궁합 등 직접 질문!
        """)
        if st.button("🎭 SBTI 검사 시작", use_container_width=True, key="btn_sbti"):
            st.session_state["page"] = "test"
            st.session_state["test_type"] = "sbti"
            st.session_state["messages"] = []
            st.session_state["started"] = False
            st.rerun()

    st.markdown("---")
    st.caption("🏫 당곡고등학교 AI 학습 프로젝트 | Powered by Anthropic Claude API & Streamlit")


# ─────────────────────────────────────────────
# 대화형 검사 페이지
# ─────────────────────────────────────────────
def show_test():
    test_type = st.session_state["test_type"]

    if test_type == "mbti":
        icon = "🔮"
        title = "MBTI 검사"
        system_prompt = MBTI_SYSTEM_PROMPT
        first_msg = "안녕! MBTI 검사 시작해줘!"
    else:
        icon = "🎭"
        title = "SBTI 검사"
        system_prompt = SBTI_SYSTEM_PROMPT
        first_msg = "안녕! SBTI 검사 시작해줘!"

    st.markdown(f"<p class='main-title'>{icon} {title}</p>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>AI와 대화하며 검사를 진행합니다</p>", unsafe_allow_html=True)

    # 사이드바
    with st.sidebar:
        st.markdown(f"## {icon} {title}")
        st.markdown("---")

        st.markdown("### 💡 사용법")
        if test_type == "sbti":
            st.markdown("""
            **검사 중:**
            - `A` / `B` / `C` → 답변 선택
            - `이전` → 이전 문항으로
            - `제출` → 바로 결과 보기

            **결과 나온 후:**
            - `팩폭 해줘` → 뼈 때리는 분석
            - `궁합 알려줘` → 유형 궁합
            - `5대 모델 분석` → 상세 결과
            - `장점` / `단점`
            - `한 줄 요약`
            - 아무거나 자유롭게!
            """)
        else:
            st.markdown("""
            **검사 중:**
            - 자유롭게 답변
            - `이전` → 이전 질문으로
            - `제출` → 바로 결과 보기

            **결과 나온 후:**
            - `상세 분석` → 유형 설명
            - `궁합 알려줘` → 유형 궁합
            - `지표 분석` → E/I, S/N 등
            - `장점` / `단점`
            - `한 줄 요약`
            - 아무거나 자유롭게!
            """)

        st.markdown("---")
        st.markdown("### 📊 토큰 사용량")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("입력", f"{st.session_state['total_input_tokens']:,}")
        with col2:
            st.metric("출력", f"{st.session_state['total_output_tokens']:,}")

        st.markdown("---")
        if st.button("🏠 홈으로", use_container_width=True, key="side_home"):
            reset_test()
            st.rerun()
        if st.button("🔄 처음부터 다시", use_container_width=True, key="side_reset"):
            st.session_state["messages"] = []
            st.session_state["started"] = False
            st.rerun()

    # 첫 AI 메시지
    if not st.session_state["started"]:
        with st.spinner(f"{icon} AI 준비 중..."):
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=1000,
                    system=system_prompt,
                    messages=[{"role": "user", "content": first_msg}],
                )
                ai_msg = response.content[0].text
                st.session_state["total_input_tokens"] += response.usage.input_tokens
                st.session_state["total_output_tokens"] += response.usage.output_tokens
                st.session_state["messages"].append({"role": "assistant", "content": ai_msg})
                st.session_state["started"] = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ 오류: {e}")
                return

    # 대화 표시
    for msg in st.session_state["messages"]:
        if msg["role"] == "assistant":
            with st.chat_message("assistant", avatar=icon):
                st.markdown(msg["content"])
        else:
            with st.chat_message("user", avatar="🧑‍🎓"):
                st.markdown(msg["content"])

    # 사용자 입력
    user_input = st.chat_input("답변을 입력하세요! (A/B/C, 이전, 제출, 또는 자유롭게)")

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})

        api_messages = [{"role": "user", "content": first_msg}] + st.session_state["messages"]

        with st.spinner(f"{icon} AI 응답 중..."):
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=2000,
                    system=system_prompt,
                    messages=api_messages,
                )
                ai_msg = response.content[0].text
                st.session_state["total_input_tokens"] += response.usage.input_tokens
                st.session_state["total_output_tokens"] += response.usage.output_tokens
                st.session_state["messages"].append({"role": "assistant", "content": ai_msg})
                st.rerun()
            except Exception as e:
                st.error(f"❌ 오류: {e}")
                st.session_state["messages"].pop()


# ─────────────────────────────────────────────
# 라우팅
# ─────────────────────────────────────────────
page = st.session_state["page"]

if page == "home":
    show_home()
elif page == "test":
    show_test()
else:
    show_home()
