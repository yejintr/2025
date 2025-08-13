# streamlit_app.py
# 실행 방법:
#   pip install streamlit folium streamlit-folium
#   streamlit run streamlit_app.py

import streamlit as st
import folium
from streamlit_folium import st_folium
import random

st.set_page_config(page_title="🇰🇷 한국지리 여행 코스 추천", page_icon="🗺️", layout="wide")

# =============================
# 💅 Custom CSS (요즘 감성)
# =============================
st.markdown(
    """
    <style>
    @keyframes floaty { 0%{transform:translateY(0)}50%{transform:translateY(-6px)}100%{transform:translateY(0)} }
    .title-hero { font-size: 42px; font-weight: 900; background: linear-gradient(90deg,#ff7ad9,#7ad7ff,#8cff98); -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: -0.5px; }
    .subtitle { font-size: 18px; opacity: 0.9; }
    .pill { display:inline-block; padding:6px 12px; border-radius:999px; background:#111; color:#fff; margin-right:6px; font-size:13px; }
    .spark { animation: floaty 3s ease-in-out infinite; display:inline-block; }
    .card { border-radius: 18px; padding:18px; background: rgba(255,255,255,0.65); backdrop-filter: blur(6px); box-shadow: 0 10px 24px rgba(0,0,0,0.08); border: 1px solid rgba(0,0,0,0.05); }
    .metric { font-size: 28px; font-weight: 800; }
    .emoji { font-size: 28px; }
    footer{visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# =============================
# 🧠 데이터: 17개 시·도 좌표/특징/여행지/코스
# =============================
REGIONS = {
    "서울특별시": {
        "coords": [37.5665, 126.9780],
        "feature": "🛍️ 경제·문화 중심지 · 📚 교육·행정 허브 · 🏙️ 한강 주변 분지 지형",
        "spots": ["경복궁 🏯", "남산타워 🌃", "홍대 🎶", "청계천 🌊", "한강 🚴"],
    },
    "부산광역시": {
        "coords": [35.1796, 129.0756],
        "feature": "🌊 해양도시 · 🐟 수산업 · 🚢 국제무역항 · 산지와 해안의 복합 지형",
        "spots": ["해운대 🏖️", "광안리 🌉", "자갈치시장 🦑", "태종대 🌿"],
    },
    "대구광역시": {
        "coords": [35.8714, 128.6014],
        "feature": "🌞 분지 기후(대륙성) · 섬유·패션 산업 · 근교 팔공산",
        "spots": ["동성로 🛍️", "팔공산 ⛰️", "김광석길 🎵", "수성못 🌙"],
    },
    "인천광역시": {
        "coords": [37.4563, 126.7052],
        "feature": "🛫 공항·항만 결절점 · 📦 물류 허브 · 갯벌·도서",
        "spots": ["송도센트럴파크 🌆", "차이나타운 🧧", "월미도 🎡", "영종도 🏝️"],
    },
    "광주광역시": {
        "coords": [35.1595, 126.8526],
        "feature": "🎨 문화예술 도시 · 🥬 호남평야 관문 · 무등산",
        "spots": ["국립아시아문화전당 🏛️", "무등산 ⛰️", "송정시장 🍜", "양림동 📷"],
    },
    "대전광역시": {
        "coords": [36.3504, 127.3845],
        "feature": "🔬 R&D·과학특구 · 교통 요충(철도 분기) · 금강",
        "spots": ["한빛탑 🚀", "엑스포과학공원 🔭", "유성온천 ♨️", "갑천 🌿"],
    },
    "울산광역시": {
        "coords": [35.5384, 129.3114],
        "feature": "🏭 공업도시(자동차·조선·화학) · 태화강",
        "spots": ["대왕암 🌊", "태화강국가정원 🌿", "간절곶 🌅", "울산대공원 🌳"],
    },
    "세종특별자치시": {
        "coords": [36.4800, 127.2890],
        "feature": "🏛️ 행정중심복합도시 · 계획도시 · 금강 수변",
        "spots": ["세종호수공원 🦢", "국립세종수목원 🌿", "정부세종청사 🏢"],
    },
    "경기도": {
        "coords": [37.4138, 127.5183],
        "feature": "🏘️ 수도권 배후 · 첨단 제조업 · 교통망 촘촘",
        "spots": ["수원화성 🏯", "가평 남이섬 🍁", "용인 에버랜드 🎢", "파주 임진각 🕊️"],
    },
    "강원특별자치도": {
        "coords": [37.8228, 128.1555],
        "feature": "⛰️ 태백산맥 · 산악·하천 경관 · 동해안 해변",
        "spots": ["강릉 경포대 🌊", "속초 설악산 🏔️", "양양 서핑 🏄", "평창 대관령 🐑"],
    },
    "충청북도": {
        "coords": [36.6357, 127.4917],
        "feature": "⛰️ 내륙 분지·산지 · 충주호 · 공업·농업 혼재",
        "spots": ["청남대 🏡", "속리산 법주사 🛕", "충주호 🚤", "단양 만천하 🌉"],
    },
    "충청남도": {
        "coords": [36.5184, 126.8],
        "feature": "🏖️ 서해안 갯벌 · 산업단지 · 내포신도시",
        "spots": ["태안 안면도 🏝️", "보령 머드비치 🏖️", "공주 공산성 🏯", "서산 해미읍성 🛡️"],
    },
    "전라북도": {
        "coords": [35.7175, 127.1530],
        "feature": "🌾 호남평야 · 농업 중심 · 한옥·음식 문화",
        "spots": ["전주 한옥마을 🏘️", "남원 광한루원 🌸", "부안 채석강 🪨", "무주 덕유산 ⛰️"],
    },
    "전라남도": {
        "coords": [34.8679, 126.9910],
        "feature": "🏝️ 다도해 · 수산업 · 따뜻한 기후",
        "spots": ["여수 밤바다 🌃", "순천만 습지 🐦", "보성 녹차밭 🍵", "담양 메타세쿼이아길 🌲"],
    },
    "경상북도": {
        "coords": [36.4919, 128.8889],
        "feature": "🏛️ 신라 유산 · 산지·분지 · 내륙 공업",
        "spots": ["경주 불국사 🛕", "안동 하회마을 🏘️", "포항 영일대해수욕장 🏖️", "문경새재 🌿"],
    },
    "경상남도": {
        "coords": [35.4606, 128.2132],
        "feature": "⚓ 항만·제조업 · 낙동강 하구 · 남해안 리아스식",
        "spots": ["창원 진해 군항제 🌸", "통영 동피랑 🎨", "거제 바람의언덕 🌬️", "남해 독일마을 🏡"],
    },
    "제주특별자치도": {
        "coords": [33.4996, 126.5312],
        "feature": "🌋 화산지형(한라산·오름·용암동굴) · 아열대 기후 · 관광 1번지",
        "spots": ["성산일출봉 🌅", "한라산 ⛰️", "협재해수욕장 🌊", "우도 🚤", "천지연폭포 💦"],
    },
}

THEMES = {
    "자연": "🌿",
    "역사·문화": "🏛️",
    "먹거리": "🍜",
    "힐링": "🧘",
    "액티비티": "🤸",
}

# 간단 퀴즈 데이터 (지역별 1문항)
QUIZ = {
    "서울특별시": ("서울의 중심을 흐르는 강은?", ["한강", "금강", "영산강", "낙동강"], 0),
    "부산광역시": ("부산의 대표 해변은?", ["경포대", "광안리", "만리포", "정동진"], 1),
    "강원특별자치도": ("강원도를 관통하는 큰 산맥은?", ["차령산맥", "소백산맥", "태백산맥", "노령산맥"], 2),
    "경상북도": ("경북의 신라 수도였던 도시는?", ["경주", "안동", "대구", "포항"], 0),
    "전라남도": ("전남 연안의 바다를 뭐라 부를까?", ["다도해", "황해", "울산만", "제주해협"], 0),
}

# =============================
# 🌟 헤더
# =============================
col1, col2 = st.columns([3, 2])
with col1:
    st.markdown(
        """
        <div class="title-hero">🗺️🇰🇷 한국지리 × 여행코스 추천</div>
        <div class="subtitle">지도를 클릭하면 지역의 <b>지리 특징</b>과 <b>핫플 코스</b>가 촤르르 ✨ <span class="spark">🌈</span></div>
        <div style="margin-top:10px;">
            <span class="pill">#한국지리</span>
            <span class="pill">#여행추천</span>
            <span class="pill">#교육용</span>
            <span class="pill">#프로젝트기반학습</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
with col2:
    st.metric(label="오늘의 랜덤 설렘 지수 ✨", value=f"{random.randint(82, 100)}%")

st.divider()

# =============================
# 🎛️ 사이드바: 테마/코스 길이/지역 선택
# =============================
with st.sidebar:
    st.markdown("## 🎒 여행 취향")
    theme = st.selectbox("테마를 골라주세요", list(THEMES.keys()), index=0)
    days = st.slider("코스 길이(일)", 1, 3, 2)
    st.markdown("---")
    st.markdown("## 🧭 지역 찾기")
    region_select = st.selectbox("지역(시·도)", list(REGIONS.keys()))
    st.markdown("""
    #### 🔍 팁
    - 지도 마커를 클릭해도 지역이 선택돼요.
    - 아래 <b>코스 생성</b> 버튼으로 요즘 감성 코스를 뚝딱! ✨
    """, unsafe_allow_html=True)

# =============================
# 🗺️ 지도
# =============================
center = [36.5, 127.9]
zoom = 6.6
m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")

# 마커 추가
for r, info in REGIONS.items():
    folium.Marker(
        location=info["coords"],
        tooltip=f"{r} 클릭! 🎯",
        popup=folium.Popup(f"<b>{r}</b>", max_width=200),
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

st_map = st_folium(m, width=None, height=540)

# 지도 클릭 처리 → region_select 업데이트 비스무리 (Streamlit 상태 반영)
if st_map and st_map.get("last_object_clicked_tooltip"):
    tip = st_map["last_object_clicked_tooltip"]
    clicked = tip.replace(" 클릭! 🎯", "") if tip else None
    if clicked in REGIONS:
        region_select = clicked

# =============================
# 🧭 선택 지역 카드
# =============================
info = REGIONS[region_select]

c1, c2, c3 = st.columns([1,1,1])
with c1:
    st.markdown(f"""
    <div class="card">
      <div class="emoji">📍</div>
      <div class="metric">{region_select}</div>
      <div>중심 좌표: {info['coords'][0]:.3f}, {info['coords'][1]:.3f} </div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="card">
      <div class="emoji">🧭</div>
      <div class="metric">지리 특징</div>
      <div>{info['feature']}</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="card">
      <div class="emoji">🎨</div>
      <div class="metric">여행 테마</div>
      <div>{THEMES[theme]} <b>{theme}</b> · {days}일 코스</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("")

# =============================
# 🧩 탭: 여행지 / 코스 / 퀴즈
# =============================
T1, T2, T3 = st.tabs(["🌟 추천 여행지", "🛤️ 코스 생성기", "🧠 지역 퀴즈"])

with T1:
    st.markdown("### 🌈 이 지역의 핫플 리스트")
    cols = st.columns(4)
    for i, spot in enumerate(info["spots"]):
        with cols[i % 4]:
            st.markdown(f"- {spot}")

with T2:
    st.markdown("### 🛠️ 코스 생성기 ✨")

    def build_course(region_name: str, days: int, theme: str):
        spots = REGIONS[region_name]["spots"]
        random.seed(region_name + theme + str(days))
        picks = random.sample(spots, k=min(len(spots), max(2, days+1)))
        lines = []
        for d in range(1, days+1):
            seq = " → ".join(picks[(d-1): (d-1)+min(3, len(picks))])
            lines.append(f"Day {d} {THEMES[theme]} : {seq}")
        return "\n".join(lines)

    st.info("테마와 일수를 고른 뒤, 아래 버튼을 눌러 코스를 받아보세요! ✨")
    if st.button("🎁 요즘 감성 코스 생성하기"):
        course_text = build_course(region_select, days, theme)
        st.success(f"{region_select} · {days}일 · {theme} 코스가 완성됐어요! 💖")
        st.code(course_text, language="markdown")

with T3:
    st.markdown("### 🧩 지역 퀴즈로 개념 체크!")
    if region_select in QUIZ:
        q, choices, answer = QUIZ[region_select]
        sel = st.radio(q, choices, index=None)
        if sel is not None:
            if choices.index(sel) == answer:
                st.balloons()
                st.success("정답! 🎉 지리센스 만점")
            else:
                st.error("앗! 다시 도전 🔁")
    else:
        st.warning("이 지역은 준비 중이에요! 퀴즈 요청 주시면 바로 추가할게요. 📝")

# =============================
# 📚 학습 포인트 (요약 카드)
# =============================
st.markdown("---")
st.markdown("#### 🧭 학습 포인트 요약")
colA, colB, colC = st.columns(3)
with colA:
    st.markdown(
        """
        <div class="card">
        <b>입지·공간 패턴</b><br>
        - 중심지 이론 감각 익히기 🧲<br>
        - 교통 결절·물류 허브 파악 🚉🛳️<br>
        </div>
        """, unsafe_allow_html=True,
    )
with colB:
    st.markdown(
        """
        <div class="card">
        <b>자연·인문 상호작용</b><br>
        - 산맥·하천·해안과 도시 발달 ⛰️🌊<br>
        - 산업 구조와 지형의 연결 고리 🏭<br>
        </div>
        """, unsafe_allow_html=True,
    )
with colC:
    st.markdown(
        """
        <div class="card">
        <b>여행 설계 역량</b><br>
        - 테마·일정 최적화 🧩<br>
        - 동선·밀집도 고려한 코스 🗺️<br>
        </div>
        """, unsafe_allow_html=True,
    )

st.markdown("\n")

# =============================
# ℹ️ 푸터 노트
# =============================
st.caption("© 한국지리 × 여행코스 추천 · 교육용 데모 · 이모지 과다 주의 🤩")
