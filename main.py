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
# CSS 스타일
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
    .question-box {
        background-color: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        border-radius: 0 10px 10px 0;
        margin: 1rem 0;
        font-size: 1.05rem;
        line-height: 1.7;
    }
    .progress-text {
        text-align: center;
        font-size: 1.2rem;
        font-weight: bold;
        color: #667eea;
    }
    .review-item {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #667eea;
    }
    .review-item-unanswered {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 3px solid #ffc107;
    }
    .selected-answer {
        color: #667eea;
        font-weight: bold;
    }
    .token-info {
        background-color: #e8f4f8;
        padding: 0.8rem;
        border-radius: 8px;
        font-size: 0.85rem;
        text-align: center;
        margin-top: 1rem;
    }
    .submit-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 2rem 0;
    }
    .nav-buttons {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API 키 불러오기
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
SBTI_QUESTIONS = [
    {
        "id": 1,
        "text": "믿는 사람이랑은 진짜 가까워지고 싶어, 잃어버린 가족 만난 것처럼.",
        "choices": {"A": "동의", "B": "중립", "C": "비동의"},
        "model": "사회", "dimension": "친밀욕구"
    },
    {
        "id": 2,
        "text": "난 찐따일 뿐만 아니라, 조커이고, 건어물녀남이야. 평생 연애 한 번 못 해봤어. 소심하고 자존감 바닥이고, 내 청춘은 망상의 연속이야. 매일 나도 같이 길 걸어주고, 쇼핑하고, 놀아줄 사람이 있으면 좋겠다고 상상해. 현실은 부모님 돈 다 써버리고, 구린 학교 나와서, 대충 살다가 취직한 꿈도 목표도 능력도 없는 3무 인간. 온라인에서 찐따 드립치는 거 볼 때마다 울고 싶어.",
        "choices": {"A": "나 울었어..", "B": "이게 뭐야..", "C": "이건 내가 아니야!"},
        "model": "자아", "dimension": "자기수용"
    },
    {
        "id": 3,
        "text": "난 보통 계획을 세우는데, ____",
        "choices": {"A": "근데 계획은 변화를 못 따라가.", "B": "될 때도 있고, 안 될 때도 있고.", "C": "계획 깨지는 거 진짜 싫어."},
        "model": "행동", "dimension": "계획성"
    },
    {
        "id": 4,
        "text": "나랑 사귀는 건 전기 울타리 수준이야. 너무 가까이 오면 자동으로 경보 울림.",
        "choices": {"A": "동의", "B": "중립", "C": "비동의"},
        "model": "사회", "dimension": "사회적거리"
    },
    {
        "id": 5,
        "text": "남들이 뭐라 하든 1도 신경 안 써.",
        "choices": {"A": "비동의", "B": "중립", "C": "동의"},
        "model": "자아", "dimension": "자아일관성"
    },
    {
        "id": 6,
        "text": "하늘에 맹세코, 모든 연애에 진심이었다고!",
        "choices": {"A": "아닌데", "B": "글쎄?", "C": "맞아! (당당한 표정)"},
        "model": "감정", "dimension": "감정표현"
    },
    {
        "id": 7,
        "text": "친구가 자기 친구를 데려왔어. 네 반응은?",
        "choices": {"A": "\"친구의 친구\"한테 본능적으로 좀 거리감", "B": "상대 보고, 맞으면 놀지 뭐.", "C": "친구의 친구는 내 친구지! 열정적으로 떠들어야지"},
        "model": "사회", "dimension": "사회적거리"
    },
    {
        "id": 8,
        "text": "연애 시작했는데, 상대가 엄청 집착해. 어떻게 느껴?",
        "choices": {"A": "완전 좋지", "B": "뭐 상관없어", "C": "나만의 공간이 더 좋아"},
        "model": "사회", "dimension": "독립성"
    },
    {
        "id": 9,
        "text": "연애할 때 상대에게 버림받을까 자주 걱정돼.",
        "choices": {"A": "응", "B": "가끔", "C": "아니"},
        "model": "감정", "dimension": "정서안정"
    },
    {
        "id": 10,
        "text": "가끔 어떤 일에 부정적인 생각이 있는데 결국 말 안 할 때가 있잖아. 대부분의 이유는:",
        "choices": {"A": "그런 경우 별로 없어.", "B": "체면이나 관계 때문에 그런 듯.", "C": "내가 어두운 사람인 거 들키기 싫어서."},
        "model": "자아", "dimension": "자기수용"
    },
    {
        "id": 11,
        "text": "남들이 \"실행력 쩐다\"고 하면, 속마음은?",
        "choices": {"A": "마감에 몰리면 진짜 실행력 미쳐...", "B": "아, 가끔은 그런가.", "C": "맞아, 일이란 건 원래 밀고 나가야지."},
        "model": "행동", "dimension": "실행력"
    },
    {
        "id": 12,
        "text": "난 부족해, 주변 사람들이 다 나보다 잘나.",
        "choices": {"A": "맞아", "B": "가끔", "C": "아닌데"},
        "model": "자아", "dimension": "자기인식"
    },
    {
        "id": 13,
        "text": "뭔가를 할 때 성과와 성장이 목적이지, 귀찮은 일이나 위험을 피하려는 게 아니야.",
        "choices": {"A": "비동의", "B": "중립", "C": "동의"},
        "model": "행동", "dimension": "목표지향"
    },
    {
        "id": 14,
        "text": "이 문제에는 지문이 없어. 눈 감고 골라.",
        "choices": {"A": "깊이 고민해보니 A인 것 같은데?", "B": "음, B로 할까?", "C": "모르면 C지?"},
        "model": "태도", "dimension": "개방성"
    },
    {
        "id": 15,
        "text": "반드시 계속 올라가고, 더 강해져야 해.",
        "choices": {"A": "비동의", "B": "중립", "C": "동의"},
        "model": "행동", "dimension": "목표지향"
    },
    {
        "id": 16,
        "text": "뭘 하든 보통 목표가 있어.",
        "choices": {"A": "비동의", "B": "중립", "C": "동의"},
        "model": "행동", "dimension": "실행력"
    },
    {
        "id": 17,
        "text": "어느 날 갑자기 깨달았어. 인생에 무슨 개같은 의미가 있냐고. 인간은 동물처럼 욕망에 지배당하는, 순전히 호르몬에 조종되는 존재잖아. 배고프면 먹고, 졸리면 자고, 발정나면 짝짓기하고. 우리 진짜 짐승이랑 다를 게 뭐야.",
        "choices": {"A": "맞는 말이야.", "B": "맞을 수도, 아닐 수도.", "C": "완전 헛소리야."},
        "model": "태도", "dimension": "낙관성"
    },
    {
        "id": 18,
        "text": "변비로 변기에 앉은 지 30분째. 안 나와서 고통스러워. 이때 넌?",
        "choices": {"A": "30분 더 앉아보자. 혹시 나올지도.", "B": "엉덩이 때리면서 \"야 이 엉덩아, 빨리 싸!\"", "C": "관장약 써서 빨리 끝내자."},
        "model": "감정", "dimension": "감정표현"
    },
    {
        "id": 19,
        "text": "게임하다가 사귄 온라인 친구들이 오프 모임에 초대했어. 어떻게 생각해?",
        "choices": {"A": "온라인으로 떠드는 건 괜찮은데, 직접 만나긴 좀 떨려.", "B": "만나는 것도 괜찮지, 누가 오든 대화는 하지.", "C": "꾸미고 가서 열정적으로 떠들 거야. 혹시 모르잖아, 혹시?"},
        "model": "사회", "dimension": "친밀욕구"
    },
    {
        "id": 20,
        "text": "대부분의 사람은 착해.",
        "choices": {"A": "사실 사악한 인간이 세상 치질보다 많아.", "B": "글쎄.", "C": "응, 착한 사람이 더 많다고 믿고 싶어."},
        "model": "태도", "dimension": "신뢰성"
    },
    {
        "id": 21,
        "text": "네 연애 상대가 어른 공경하고, 아이 사랑하고, 다정하고, 청렴하고, 의리 있고, 말 잘하고, 관찰력 좋고, 박학다식하고, 상냥하고, 마음 착하고, 의욕 넘치고, 외모까지 완벽한 사람이야. 이때 넌?",
        "choices": {"A": "아무리 완벽해도 깊이 빠지진 않을 거야.", "B": "A와 C 사이 어딘가.", "C": "엄청 소중히 할 거고, 연애 바보가 될 수도."},
        "model": "감정", "dimension": "공감력"
    },
    {
        "id": 22,
        "text": "관습을 깨는 게 좋아. 구속당하는 건 싫어.",
        "choices": {"A": "동의", "B": "중립", "C": "비동의"},
        "model": "태도", "dimension": "개방성"
    },
    {
        "id": 23,
        "text": "내 마음속에 진심으로 추구하는 게 있어.",
        "choices": {"A": "비동의", "B": "중립", "C": "동의"},
        "model": "자아", "dimension": "자기인식"
    },
    {
        "id": 24,
        "text": "어떤 관계에서든 개인 공간을 중시해.",
        "choices": {"A": "서로 의지하는 게 더 좋아", "B": "상황에 따라", "C": "맞아! (단호하게)"},
        "model": "사회", "dimension": "독립성"
    },
    {
        "id": 25,
        "text": "결정은 빠르게 내려. 우유부단한 건 싫어.",
        "choices": {"A": "비동의", "B": "중립", "C": "동의"},
        "model": "행동", "dimension": "계획성"
    },
    {
        "id": 26,
        "text": "상대가 5시간 넘게 답장 없다가 배탈 났다고 하면, 어떻게 생각해?",
        "choices": {"A": "배탈이 5시간이나? 뭔가 숨기는 거 아냐.", "B": "믿음과 의심 사이에서 흔들려.", "C": "오늘 진짜 몸이 안 좋았나 보지."},
        "model": "태도", "dimension": "신뢰성"
    },
    {
        "id": 27,
        "text": "사람마다 다른 모습을 보여줘.",
        "choices": {"A": "비동의", "B": "중립", "C": "동의"},
        "model": "자아", "dimension": "자아일관성"
    },
    {
        "id": 28,
        "text": "시험 코앞인데, 학교에서 야간 자율학습 필수에 빠지면 벌점이야. 근데 오늘 밤 이상형이랑 배그 하기로 했어. 어떡해?",
        "choices": {"A": "빼! 한 번쯤이야!", "B": "그냥 조퇴하자.", "C": "시험인데 뭘 빼, 공부해야지."},
        "model": "감정", "dimension": "정서안정"
    },
    {
        "id": 29,
        "text": "진짜 내가 어떤 사람인지 잘 알고 있어.",
        "choices": {"A": "비동의", "B": "중립", "C": "동의"},
        "model": "자아", "dimension": "자기인식"
    },
    {
        "id": 30,
        "text": "난 가끔 세상이 다 부질없다고 느껴.",
        "choices": {"A": "동의", "B": "중립", "C": "비동의"},
        "model": "태도", "dimension": "낙관성"
    },
]

SBTI_BONUS = [
    {
        "id": "B1",
        "text": "평소 취미가 뭐야?",
        "choices": {"A": "먹고 자고 기본 생활", "B": "예술/창작 취미", "C": "음주", "D": "운동"},
    },
]

SBTI_TYPES = {
    "주도/행동형": [
        {"code": "CTRL", "name": "장악자"},
        {"code": "BOSS", "name": "리더"},
        {"code": "GOGO", "name": "직진러"},
        {"code": "SEXY", "name": "매력괴물"},
        {"code": "JOKE-R", "name": "광대"},
    ],
    "관계/감정형": [
        {"code": "LOVE-R", "name": "연애뇌"},
        {"code": "MUM", "name": "엄마"},
        {"code": "THAN-K", "name": "감사쟁이"},
        {"code": "MALO", "name": "원숭이"},
        {"code": "OH-NO", "name": "헉쟁이"},
        {"code": "WOC!", "name": "헐쟁이"},
    ],
    "냉소/일상형": [
        {"code": "Dior-s", "name": "찐따"},
        {"code": "SHIT", "name": "욕쟁이"},
        {"code": "OJBK", "name": "아무거나인간"},
        {"code": "ZZZZ", "name": "죽은척러"},
        {"code": "POOR", "name": "가난뱅이"},
        {"code": "MONK", "name": "중"},
        {"code": "IMSB", "name": "바보"},
        {"code": "ATM", "name": "현금인출기"},
        {"code": "FAKE", "name": "가면인간"},
        {"code": "THIN-K", "name": "생각쟁이"},
        {"code": "SOLO", "name": "고아"},
        {"code": "FUCK", "name": "씹러"},
        {"code": "DEAD", "name": "사망자"},
        {"code": "IMFW", "name": "폐인"},
    ],
    "히든": [
        {"code": "DRUNK", "name": "취객"},
        {"code": "HHHH", "name": "???"},
    ],
}

# ─────────────────────────────────────────────
# L/M/H 매핑
# ─────────────────────────────────────────────
LMH_MAP = {
    1: {"A": "H", "B": "M", "C": "L"},
    2: {"A": "H", "B": "M", "C": "L"},
    3: {"A": "L", "B": "M", "C": "H"},
    4: {"A": "H", "B": "M", "C": "L"},
    5: {"A": "L", "B": "M", "C": "H"},
    6: {"A": "L", "B": "M", "C": "H"},
    7: {"A": "L", "B": "M", "C": "H"},
    8: {"A": "L", "B": "M", "C": "H"},
    9: {"A": "H", "B": "M", "C": "L"},
    10: {"A": "L", "B": "M", "C": "H"},
    11: {"A": "L", "B": "M", "C": "H"},
    12: {"A": "L", "B": "M", "C": "H"},
    13: {"A": "L", "B": "M", "C": "H"},
    14: {"A": "L", "B": "M", "C": "H"},
    15: {"A": "L", "B": "M", "C": "H"},
    16: {"A": "L", "B": "M", "C": "H"},
    17: {"A": "L", "B": "M", "C": "H"},
    18: {"A": "L", "B": "M", "C": "H"},
    19: {"A": "L", "B": "M", "C": "H"},
    20: {"A": "L", "B": "M", "C": "H"},
    21: {"A": "L", "B": "M", "C": "H"},
    22: {"A": "H", "B": "M", "C": "L"},
    23: {"A": "L", "B": "M", "C": "H"},
    24: {"A": "L", "B": "M", "C": "H"},
    25: {"A": "L", "B": "M", "C": "H"},
    26: {"A": "L", "B": "M", "C": "H"},
    27: {"A": "L", "B": "M", "C": "H"},
    28: {"A": "L", "B": "M", "C": "H"},
    29: {"A": "L", "B": "M", "C": "H"},
    30: {"A": "L", "B": "M", "C": "H"},
}


def calculate_sbti_pattern(answers):
    """응답 기반 15차원 L/M/H 패턴 생성"""
    dimensions = {
        "자아_자기인식": [], "자아_자기수용": [], "자아_자아일관성": [],
        "감정_정서안정": [], "감정_감정표현": [], "감정_공감력": [],
        "태도_낙관성": [], "태도_신뢰성": [], "태도_개방성": [],
        "행동_실행력": [], "행동_목표지향": [], "행동_계획성": [],
        "사회_친밀욕구": [], "사회_사회적거리": [], "사회_독립성": [],
    }

    for q in SBTI_QUESTIONS:
        qid = q["id"]
        if qid in answers:
            answer = answers[qid]
            lmh = LMH_MAP.get(qid, {}).get(answer, "M")
            key = f"{q['model']}_{q['dimension']}"
            if key in dimensions:
                score = {"L": 1, "M": 2, "H": 3}.get(lmh, 2)
                dimensions[key].append(score)

    pattern = {}
    for key, scores in dimensions.items():
        if scores:
            avg = sum(scores) / len(scores)
            if avg <= 1.5:
                pattern[key] = "L"
            elif avg <= 2.5:
                pattern[key] = "M"
            else:
                pattern[key] = "H"
        else:
            pattern[key] = "M"

    return pattern


def pattern_to_string(pattern):
    """패턴을 읽기 쉬운 문자열로 변환"""
    models = ["자아", "감정", "태도", "행동", "사회"]
    dims = {
        "자아": ["자기인식", "자기수용", "자아일관성"],
        "감정": ["정서안정", "감정표현", "공감력"],
        "태도": ["낙관성", "신뢰성", "개방성"],
        "행동": ["실행력", "목표지향", "계획성"],
        "사회": ["친밀욕구", "사회적거리", "독립성"],
    }
    result_parts = []
    for model in models:
        part = ""
        for dim in dims[model]:
            key = f"{model}_{dim}"
            part += pattern.get(key, "M")
        result_parts.append(part)
    return "-".join(result_parts)


def check_hidden_type(answers, bonus_answers):
    """히든 유형 조건 체크"""
    if bonus_answers.get("B1") == "C":
        return "DRUNK"
    if answers:
        all_values = list(answers.values())
        a_count = all_values.count("A")
        c_count = all_values.count("C")
        total = len(all_values)
        if total > 0 and (a_count / total >= 0.85 or c_count / total >= 0.85):
            return "HHHH"
    return None


# ─────────────────────────────────────────────
# 세션 상태 초기화
# ─────────────────────────────────────────────
defaults = {
    "page": "home",
    "test_type": None,
    "sbti_answers": {},
    "sbti_bonus_answers": {},
    "sbti_current_q": 0,
    "mbti_messages": [],
    "mbti_result": None,
    "sbti_result": None,
    "total_input_tokens": 0,
    "total_output_tokens": 0,
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val


def reset_all():
    """전체 초기화"""
    for key, val in defaults.items():
        if key not in ("total_input_tokens", "total_output_tokens"):
            st.session_state[key] = val if not isinstance(val, (dict, list)) else type(val)()


# ─────────────────────────────────────────────
# 홈 페이지
# ─────────────────────────────────────────────
def show_home():
    st.markdown("<p class='main-title'>🧠 성격 유형 검사</p>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>AI와 함께하는 MBTI & SBTI 검사</p>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### 🔮 MBTI 검사")
        st.markdown("""
        **16가지 성격 유형**

        AI와 자연스럽게 대화하면서
        당신의 MBTI를 알아보세요!

        - 🗣️ 대화형 검사
        - 🤖 AI가 질문하고 분석
        - 📊 상세한 유형 설명
        """)
        if st.button("🔮 MBTI 검사 시작", use_container_width=True, key="mbti_btn"):
            st.session_state["page"] = "mbti_test"
            st.session_state["test_type"] = "mbti"
            st.session_state["mbti_messages"] = []
            st.rerun()

    with col2:
        st.markdown("### 🎭 SBTI 검사")
        st.markdown("""
        **27가지 풍자적 유형**

        5대 심리 모델 × 15차원 기반
        뼈 때리는 팩폭 결과!

        - 📝 30문항 선택형
        - ⬅️ 이전 버튼으로 수정 가능
        - 💀 풍자적 팩폭 분석
        """)
        if st.button("🎭 SBTI 검사 시작", use_container_width=True, key="sbti_btn"):
            st.session_state["page"] = "sbti_test"
            st.session_state["test_type"] = "sbti"
            st.session_state["sbti_answers"] = {}
            st.session_state["sbti_bonus_answers"] = {}
            st.session_state["sbti_current_q"] = 0
            st.rerun()

    st.markdown("---")
    st.caption("🏫 당곡고등학교 AI 학습 프로젝트 | Powered by Anthropic Claude API & Streamlit")


# ─────────────────────────────────────────────
# MBTI 검사 (AI 대화형)
# ─────────────────────────────────────────────
def show_mbti_test():
    st.markdown("<p class='main-title'>🔮 MBTI 검사</p>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>AI와 대화하면서 당신의 MBTI를 알아보세요</p>", unsafe_allow_html=True)

    if st.button("🏠 홈으로", key="mbti_home"):
        reset_all()
        st.rerun()

    st.markdown("---")

    MBTI_SYSTEM = """당신은 MBTI 성격 유형 전문 분석가입니다.

역할:
1. 사용자에게 자연스러운 대화형 질문을 하나씩 해서 MBTI 4가지 지표(E/I, S/N, T/F, J/P)를 파악합니다.
2. 질문은 한 번에 하나만. 일상적이고 재미있는 상황 질문을 하세요.
3. 총 8~12개 질문 후 충분히 파악되면 결과를 알려주세요.
4. 결과를 알려줄 때 반드시 아래 형식 포함:

===MBTI결과===
유형: (4글자)
별명: (재미있는 별명)
설명: (3-4줄)
장점: (2-3개)
단점: (2-3개)
잘 맞는 유형: (2-3개 + 이유)
안 맞는 유형: (1-2개 + 이유)
===결과끝===

5. 한국어, 친근한 반말로 대화하세요.
6. 첫 메시지에서 인사 + 첫 질문."""

    if not st.session_state["mbti_messages"]:
        with st.spinner("AI가 준비 중..."):
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=500,
                    system=MBTI_SYSTEM,
                    messages=[{"role": "user", "content": "안녕! MBTI 검사 해줘!"}],
                )
                ai_msg = response.content[0].text
                st.session_state["total_input_tokens"] += response.usage.input_tokens
                st.session_state["total_output_tokens"] += response.usage.output_tokens
                st.session_state["mbti_messages"].append({"role": "user", "content": "안녕! MBTI 검사 해줘!"})
                st.session_state["mbti_messages"].append({"role": "assistant", "content": ai_msg})
                st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")
                return

    for msg in st.session_state["mbti_messages"]:
        if msg["role"] == "user" and msg["content"] == "안녕! MBTI 검사 해줘!":
            continue
        avatar = "🧑‍🎓" if msg["role"] == "user" else "🔮"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    last_ai = ""
    for msg in reversed(st.session_state["mbti_messages"]):
        if msg["role"] == "assistant":
            last_ai = msg["content"]
            break

    if "===MBTI결과===" in last_ai or "===결과끝===" in last_ai:
        st.markdown("---")
        st.success("🎉 MBTI 검사가 완료되었습니다!")
        st.markdown(f"""
        <div class='token-info'>
            📊 총 사용 토큰 — 입력: {st.session_state["total_input_tokens"]:,} | 출력: {st.session_state["total_output_tokens"]:,}
        </div>
        """, unsafe_allow_html=True)
        if st.button("🏠 다른 검사 하러가기", key="mbti_done"):
            reset_all()
            st.rerun()
        return

    user_input = st.chat_input("답변을 입력하세요...")

    if user_input:
        st.session_state["mbti_messages"].append({"role": "user", "content": user_input})
        with st.spinner("AI가 분석 중..."):
            try:
                response = client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=800,
                    system=MBTI_SYSTEM,
                    messages=st.session_state["mbti_messages"],
                )
                ai_msg = response.content[0].text
                st.session_state["total_input_tokens"] += response.usage.input_tokens
                st.session_state["total_output_tokens"] += response.usage.output_tokens
                st.session_state["mbti_messages"].append({"role": "assistant", "content": ai_msg})
                st.rerun()
            except Exception as e:
                st.error(f"오류: {e}")
                st.session_state["mbti_messages"].pop()


# ─────────────────────────────────────────────
# SBTI 검사 (문항 선택형 + 이전/다음 버튼)
# ─────────────────────────────────────────────
def show_sbti_test():
    st.markdown("<p class='main-title'>🎭 SBTI 검사</p>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>풍자적 행동 유형 지표 — 30문항으로 알아보는 진짜 나</p>", unsafe_allow_html=True)

    if st.button("🏠 홈으로", key="sbti_home"):
        reset_all()
        st.rerun()

    all_questions = SBTI_QUESTIONS + SBTI_BONUS
    total_q = len(all_questions)
    current = st.session_state["sbti_current_q"]

    # 진행률
    answered_count = len(st.session_state["sbti_answers"]) + len(st.session_state["sbti_bonus_answers"])
    progress = answered_count / total_q
    st.progress(progress)
    st.markdown(f"<p class='progress-text'>📝 {answered_count} / {total_q} 문항 응답 완료 | 현재: {current + 1}번</p>", unsafe_allow_html=True)
    st.markdown("---")

    # 제출 확인 페이지
    if current >= total_q:
        st.session_state["page"] = "sbti_review"
        st.rerun()
        return

    # 현재 문항 표시
    q = all_questions[current]
    is_bonus = current >= len(SBTI_QUESTIONS)

    if is_bonus:
        st.markdown("### 🎁 보너스 문항")
    else:
        st.markdown(f"### 제{current + 1}문")

    st.markdown(f"<div class='question-box'>{q['text']}</div>", unsafe_allow_html=True)

    # 이미 답한 경우 표시
    if is_bonus:
        prev_answer = st.session_state["sbti_bonus_answers"].get(q["id"])
    else:
        prev_answer = st.session_state["sbti_answers"].get(q["id"])

    if prev_answer:
        st.info(f"✅ 이전 응답: **{prev_answer}) {q['choices'][prev_answer]}** — 다시 선택하면 변경됩니다.")

    # 선택지 버튼
    for key, value in q["choices"].items():
        # 이전에 선택한 답이면 강조
        btn_label = f"{'👉 ' if prev_answer == key else ''}{key}) {value}"
        if st.button(btn_label, key=f"q_{current}_{key}", use_container_width=True):
            if is_bonus:
                st.session_state["sbti_bonus_answers"][q["id"]] = key
            else:
                st.session_state["sbti_answers"][q["id"]] = key
            # 자동으로 다음 문항으로
            if current < total_q - 1:
                st.session_state["sbti_current_q"] = current + 1
            else:
                st.session_state["sbti_current_q"] = total_q
            st.rerun()

    # ─── 이전 / 다음 네비게이션 버튼 ───
    st.markdown("---")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 1])

    with nav_col1:
        if current > 0:
            if st.button("⬅️ 이전 문항", key="prev_btn", use_container_width=True):
                st.session_state["sbti_current_q"] = current - 1
                st.rerun()

    with nav_col2:
        # 문항 점프 기능
        jump_to = st.number_input(
            "문항 이동",
            min_value=1,
            max_value=total_q,
            value=current + 1,
            step=1,
            key="jump_input",
            label_visibility="collapsed"
        )
        if st.button("🔢 이동", key="jump_btn", use_container_width=True):
            st.session_state["sbti_current_q"] = jump_to - 1
            st.rerun()

    with nav_col3:
        if current < total_q - 1:
            if st.button("다음 문항 ➡️", key="next_btn", use_container_width=True):
                st.session_state["sbti_current_q"] = current + 1
                st.rerun()
        else:
            if st.button("📋 제출 확인 ➡️", key="to_review_btn", use_container_width=True):
                st.session_state["sbti_current_q"] = total_q
                st.rerun()


# ─────────────────────────────────────────────
# SBTI 제출 확인 페이지
# ─────────────────────────────────────────────
def show_sbti_review():
    st.markdown("<p class='main-title'>📋 응답 확인</p>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>제출 전에 답변을 확인하고 수정할 수 있어요!</p>", unsafe_allow_html=True)

    if st.button("🏠 홈으로", key="review_home"):
        reset_all()
        st.rerun()

    st.markdown("---")

    all_questions = SBTI_QUESTIONS + SBTI_BONUS
    total_q = len(all_questions)

    answered_main = len(st.session_state["sbti_answers"])
    answered_bonus = len(st.session_state["sbti_bonus_answers"])
    answered_total = answered_main + answered_bonus
    unanswered = total_q - answered_total

    # 응답 요약
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("✅ 응답 완료", f"{answered_total}문항")
    with col2:
        st.metric("❌ 미응답", f"{unanswered}문항")
    with col3:
        st.metric("📊 응답률", f"{answered_total/total_q*100:.0f}%")

    if unanswered > 0:
        st.warning(f"⚠️ 아직 {unanswered}개 문항에 답하지 않았어요! 정확한 결과를 위해 모두 응답해주세요.")

    st.markdown("---")
    st.markdown("### 📝 전체 응답 목록")

    # 전체 응답 목록
    for i, q in enumerate(all_questions):
        is_bonus = i >= len(SBTI_QUESTIONS)

        if is_bonus:
            answer = st.session_state["sbti_bonus_answers"].get(q["id"])
            q_label = "🎁 보너스"
        else:
            answer = st.session_state["sbti_answers"].get(q["id"])
            q_label = f"제{i+1}문"

        # 질문 텍스트 줄이기 (너무 길면)
        short_text = q["text"][:60] + "..." if len(q["text"]) > 60 else q["text"]

        if answer:
            answer_text = q["choices"].get(answer, "?")
            st.markdown(f"""
            <div class='review-item'>
                <strong>{q_label}</strong>: {short_text}<br>
                <span class='selected-answer'>✅ 응답: {answer}) {answer_text}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='review-item-unanswered'>
                <strong>{q_label}</strong>: {short_text}<br>
                ❌ <strong>미응답</strong>
            </div>
            """, unsafe_allow_html=True)

        # 수정 버튼
        col_edit, col_space = st.columns([1, 3])
        with col_edit:
            if st.button(f"✏️ 수정", key=f"edit_{i}", use_container_width=True):
                st.session_state["sbti_current_q"] = i
                st.session_state["page"] = "sbti_test"
                st.rerun()

    # ─── 제출 버튼 ───
    st.markdown("---")
    st.markdown("""
    <div class='submit-box'>
        <h2>🎭 제출할 준비가 되셨나요?</h2>
        <p>제출하면 AI가 당신의 영혼을 분석합니다...</p>
    </div>
    """, unsafe_allow_html=True)

    submit_col1, submit_col2 = st.columns(2)

    with submit_col1:
        if st.button("⬅️ 문항으로 돌아가기", use_container_width=True, key="back_to_test"):
            st.session_state["sbti_current_q"] = 0
            st.session_state["page"] = "sbti_test"
            st.rerun()

    with submit_col2:
        if answered_total == 0:
            st.button("🚫 응답이 없습니다", use_container_width=True, disabled=True)
        else:
            if st.button("🚀 제출하고 결과 보기!", use_container_width=True, key="submit_btn", type="primary"):
                st.session_state["page"] = "sbti_result"
                st.rerun()


# ─────────────────────────────────────────────
# SBTI 결과 페이지
# ─────────────────────────────────────────────
def show_sbti_result():
    st.markdown("<p class='main-title'>🎭 SBTI 검사 결과</p>", unsafe_allow_html=True)

    # 이미 결과가 있으면 바로 표시
    if st.session_state["sbti_result"]:
        st.markdown(st.session_state["sbti_result"])

        answers = st.session_state["sbti_answers"]
        pattern = calculate_sbti_pattern(answers)
        pattern_str = pattern_to_string(pattern)

        with st.expander("🔍 내 검사 패턴 상세보기"):
            st.code(f"15차원 패턴: {pattern_str}")
            for key, val in pattern.items():
                model, dim = key.split("_")
                st.write(f"- **{model}** → {dim}: **{val}**")

        st.markdown(f"""
        <div class='token-info'>
            📊 AI 사용량 — 입력: {st.session_state["total_input_tokens"]:,} 토큰 | 출력: {st.session_state["total_output_tokens"]:,} 토큰
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 다시 검사하기", use_container_width=True, key="retry"):
                reset_all()
                st.session_state["page"] = "sbti_test"
                st.session_state["test_type"] = "sbti"
                st.rerun()
        with col2:
            if st.button("🏠 홈으로", use_container_width=True, key="result_home"):
                reset_all()
                st.rerun()
        return

    # 결과 생성
    answers = st.session_state["sbti_answers"]
    bonus_answers = st.session_state["sbti_bonus_answers"]

    pattern = calculate_sbti_pattern(answers)
    pattern_str = pattern_to_string(pattern)
    hidden = check_hidden_type(answers, bonus_answers)

    all_types_text = ""
    for category, types in SBTI_TYPES.items():
        all_types_text += f"\n[{category}]\n"
        for t in types:
            all_types_text += f"  - {t['code']} ({t['name']})\n"

    analysis_prompt = f"""너는 SBTI(Satirical Behavioral Type Indicator, 풍자적 행동 유형 지표) 전문 분석가야.

사용자의 검사 결과를 분석해서 가장 적합한 SBTI 유형을 판별해줘.

## 사용자 검사 패턴
15차원 L/M/H 패턴: {pattern_str}

상세 패턴:
- 자아 모델: 자기인식={pattern.get("자아_자기인식","M")}, 자기수용={pattern.get("자아_자기수용","M")}, 자아일관성={pattern.get("자아_자아일관성","M")}
- 감정 모델: 정서안정={pattern.get("감정_정서안정","M")}, 감정표현={pattern.get("감정_감정표현","M")}, 공감력={pattern.get("감정_공감력","M")}
- 태도 모델: 낙관성={pattern.get("태도_낙관성","M")}, 신뢰성={pattern.get("태도_신뢰성","M")}, 개방성={pattern.get("태도_개방성","M")}
- 행동 모델: 실행력={pattern.get("행동_실행력","M")}, 목표지향={pattern.get("행동_목표지향","M")}, 계획성={pattern.get("행동_계획성","M")}
- 사회 모델: 친밀욕구={pattern.get("사회_친밀욕구","M")}, 사회적거리={pattern.get("사회_사회적거리","M")}, 독립성={pattern.get("사회_독립성","M")}

{"히든 유형 조건 감지됨: " + hidden + " → 이 유형으로 판별해줘!" if hidden else "히든 유형 조건 없음"}

## SBTI 유형 목록
{all_types_text}

## 응답 형식 (반드시 이 형식으로!)

🎭 **당신의 SBTI 유형**

# [유형코드] ([별명])

---

## 💀 팩폭 분석
(이 유형에 대한 풍자적이고 뼈 때리는 분석 3-5문단. 웃기면서 정확한 통찰. 독설+애정. MZ세대 말투.)

---

## 📊 5대 모델 분석
| 모델 | 결과 | 해석 |
|------|------|------|
| 자아 | {pattern.get("자아_자기인식","M")}{pattern.get("자아_자기수용","M")}{pattern.get("자아_자아일관성","M")} | 한 줄 해석 |
| 감정 | {pattern.get("감정_정서안정","M")}{pattern.get("감정_감정표현","M")}{pattern.get("감정_공감력","M")} | 한 줄 해석 |
| 태도 | {pattern.get("태도_낙관성","M")}{pattern.get("태도_신뢰성","M")}{pattern.get("태도_개방성","M")} | 한 줄 해석 |
| 행동 | {pattern.get("행동_실행력","M")}{pattern.get("행동_목표지향","M")}{pattern.get("행동_계획성","M")} | 한 줄 해석 |
| 사회 | {pattern.get("사회_친밀욕구","M")}{pattern.get("사회_사회적거리","M")}{pattern.get("사회_독립성","M")} | 한 줄 해석 |

---

## 💕 궁합
- **찰떡궁합**: [유형코드] ([별명]) — 이유
- **좋은 궁합**: [유형코드] ([별명]) — 이유
- **최악의 궁합**: [유형코드] ([별명]) — 이유

---

## 🔥 한 줄 요약
(이 유형을 한 문장으로 정리하는 킬러 문장)
"""

    with st.spinner("🎭 AI가 당신의 영혼을 분석하는 중..."):
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system="너는 SBTI 풍자적 성격 검사 전문 분석가야. 독설과 유머와 정확한 통찰을 섞어서 결과를 알려줘. 한국어로, MZ세대 말투로 써줘. 재미있고 뼈 때리게!",
                messages=[{"role": "user", "content": analysis_prompt}],
            )

            result_text = response.content[0].text
            st.session_state["total_input_tokens"] += response.usage.input_tokens
            st.session_state["total_output_tokens"] += response.usage.output_tokens
            st.session_state["sbti_result"] = result_text

            st.rerun()

        except Exception as e:
            st.error(f"❌ 분석 중 오류가 발생했습니다: {e}")
            if st.button("🔄 다시 시도", key="retry_error"):
                st.rerun()


# ─────────────────────────────────────────────
# 페이지 라우팅
# ─────────────────────────────────────────────
page = st.session_state["page"]

if page == "home":
    show_home()
elif page == "mbti_test":
    show_mbti_test()
elif page == "sbti_test":
    show_sbti_test()
elif page == "sbti_review":
    show_sbti_review()
elif page == "sbti_result":
    show_sbti_result()
else:
    show_home()
