import streamlit as st
import ephem
from datetime import date
import random

# ----------------------------
# 페이지 설정
# ----------------------------
st.set_page_config(
    page_title="🌙 Moon Meal",
    page_icon="🌙",
    layout="centered"
)

# ----------------------------
# CSS
# ----------------------------
st.markdown("""
<style>
.stApp{
    background: linear-gradient(to bottom,#FFF8F3,#FFF2CC);
}

.title{
    text-align:center;
    font-size:45px;
    font-weight:bold;
    color:#444;
}

.subtitle{
    text-align:center;
    font-size:20px;
    color:#777;
}

.card{
    background:white;
    padding:25px;
    border-radius:20px;
    box-shadow:0px 5px 15px rgba(0,0,0,0.15);
    text-align:center;
    margin-top:20px;
}

.food{
    font-size:35px;
    font-weight:bold;
}

.kcal{
    font-size:25px;
    color:#ff6b6b;
}

.reason{
    font-size:18px;
    color:#666;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------
# 달 위상 계산
# ----------------------------
moon = ephem.Moon()
moon.compute(date.today())

illum = moon.phase

if illum < 5:
    phase = "🌑 신월"
elif illum < 25:
    phase = "🌒 초승달"
elif illum < 45:
    phase = "🌓 상현달"
elif illum < 65:
    phase = "🌔 차오르는 달"
elif illum < 90:
    phase = "🌖 기우는 달"
else:
    phase = "🌕 보름달"

# ----------------------------
# 메뉴 데이터
# ----------------------------
foods = {
    "🌑 신월":[
        ("🥗 샐러드",250),
        ("🍙 주먹밥",320),
        ("🥣 죽",300)
    ],

    "🌒 초승달":[
        ("🥪 샌드위치",420),
        ("🍜 우동",480),
        ("🌮 타코",430)
    ],

    "🌓 상현달":[
        ("🍛 카레",620),
        ("🍚 비빔밥",580),
        ("🍜 라멘",650)
    ],

    "🌔 차오르는 달":[
        ("🍝 파스타",700),
        ("🍔 햄버거",760),
        ("🍗 치킨",820)
    ],

    "🌕 보름달":[
        ("🥩 삼겹살",900),
        ("🍖 스테이크",850),
        ("🍣 초밥",550)
    ],

    "🌖 기우는 달":[
        ("🍱 도시락",550),
        ("🍲 순두부찌개",480),
        ("🍜 칼국수",530)
    ]
}

food, kcal = random.choice(foods[phase])

messages = {
    "🌑 신월":"새로운 시작! 가볍게 먹어보세요 🌱",
    "🌒 초승달":"조금씩 에너지를 채워볼까요? ✨",
    "🌓 상현달":"든든한 한 끼가 필요한 날입니다 😋",
    "🌔 차오르는 달":"활력이 필요한 하루예요 💪",
    "🌕 보름달":"보름달처럼 꽉 찬 행복을 즐겨보세요 🌕",
    "🌖 기우는 달":"편안하고 따뜻한 음식을 추천해요 ☕"
}

# ----------------------------
# 제목
# ----------------------------
st.markdown('<p class="title">🌙 Moon Meal</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">오늘 달이 골라준 메뉴</p>', unsafe_allow_html=True)

st.write("")

st.markdown(
f"""
<div class="card">

<h1>{phase}</h1>

<div class="food">{food}</div>

<br>

<div class="kcal">🔥 {kcal} kcal</div>

<br>

<div class="reason">{messages[phase]}</div>

</div>
""",
unsafe_allow_html=True
)

st.write("")

st.metric(
    label="🌕 오늘 달 밝기",
    value=f"{illum:.1f}%"
)

st.write("")

if st.button("🔄 다시 추천받기"):
    st.rerun()

st.write("---")

st.caption("Made with ❤️ using Streamlit")
