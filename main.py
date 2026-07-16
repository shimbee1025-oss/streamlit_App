import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(
    page_title="서울 공영주차장 지도",
    layout="wide"
)

st.title("🚗 서울시 공영주차장 정보 서비스")

########################################
# CSV 업로드
########################################

uploaded = st.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)

if uploaded:

    try:
        df = pd.read_csv(uploaded, encoding="cp949")

    except:
        df = pd.read_csv(uploaded, encoding="utf-8")

else:

    df = pd.read_csv(
        "서울시 공영주차장 안내 정보.csv",
        encoding="cp949"
    )

########################################
# 컬럼 전처리
########################################

df["자치구"] = (
    df["주소"]
    .astype(str)
    .str.extract(r"(\S+구)")
)

########################################
# 사이드바
########################################

st.sidebar.header("검색 옵션")

district = st.sidebar.selectbox(
    "자치구 선택",
    sorted(df["자치구"].dropna().unique())
)

free_only = st.sidebar.checkbox(
    "무료 주차장만 보기"
)

weekend_only = st.sidebar.checkbox(
    "주말 운영만 보기"
)

########################################
# 필터
########################################

filtered = df[
    df["자치구"] == district
].copy()

if free_only:

    filtered = filtered[
        filtered["유무료구분명"] == "무료"
    ]

if weekend_only:

    filtered = filtered[
        filtered["주말 운영 종료시각(HHMM)"].notna()
    ]

########################################
# 가장 저렴한 주차장
########################################

tmp = filtered.copy()

tmp["기본 주차 요금"] = pd.to_numeric(
    tmp["기본 주차 요금"],
    errors="coerce"
)

tmp = tmp.dropna(
    subset=["기본 주차 요금"]
)

st.subheader("💰 가장 저렴한 주차장")

if not tmp.empty:

    cheap = tmp.loc[
        tmp["기본 주차 요금"].idxmin()
    ]

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "주차장",
        cheap["주차장명"]
    )

    c2.metric(
        "기본요금",
        f"{int(cheap['기본 주차 요금'])}원"
    )

    c3.metric(
        "무료 여부",
        cheap["유무료구분명"]
    )

    st.write(
        f"📍 {cheap['주소']}"
    )

else:

    st.warning(
        "요금 정보가 없습니다."
    )

########################################
# 주소 → 좌표 변환
########################################

@st.cache_data
def geocode(addr):

    geolocator = Nominatim(
        user_agent="parking_app"
    )

    try:

        loc = geolocator.geocode(
            "서울 " + str(addr)
        )

        if loc:

            return (
                loc.latitude,
                loc.longitude
            )

    except:
        pass

    return None, None


for idx, row in filtered.iterrows():

    lat = row.get("위도")
    lon = row.get("경도")

    if pd.isna(lat) or pd.isna(lon):

        lat, lon = geocode(
            row["주소"]
        )

        filtered.loc[idx, "위도"] = lat
        filtered.loc[idx, "경도"] = lon

########################################
# 지도 생성
########################################

map_df = filtered.dropna(
    subset=["위도", "경도"]
)

st.subheader("🗺️ 주차장 위치")

if not map_df.empty:

    center = [
        map_df["위도"].mean(),
        map_df["경도"].mean()
    ]

    m = folium.Map(
        location=center,
        zoom_start=13
    )

    for _, row in map_df.iterrows():

        fee = row["기본 주차 요금"]

        if pd.isna(fee):
            fee = "정보없음"
        else:
            fee = f"{int(fee)}원"

        weekend = (
            "운영"
            if pd.notna(
                row["주말 운영 종료시각(HHMM)"]
            )
            else "미운영"
        )

        tooltip = f"""
        <b>{row['주차장명']}</b><br>
        주소 : {row['주소']}<br>
        기본요금 : {fee}<br>
        무료여부 : {row['유무료구분명']}<br>
        주말운영 : {weekend}
        """

        color = (
            "green"
            if row["유무료구분명"] == "무료"
            else "red"
        )

        folium.Marker(
            location=[
                row["위도"],
                row["경도"]
            ],
            tooltip=tooltip,
            popup=tooltip,
            icon=folium.Icon(
                color=color,
                icon="info-sign"
            )
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=700
    )

else:

    st.warning(
        "표시 가능한 위치 정보가 없습니다."
    )

########################################
# 데이터 표
########################################

st.subheader("📋 주차장 목록")

show_cols = [
    "주차장명",
    "주소",
    "유무료구분명",
    "기본 주차 요금",
    "총 주차면"
]

show_cols = [
    c for c in show_cols
    if c in filtered.columns
]

st.dataframe(
    filtered[show_cols],
    use_container_width=True
)
