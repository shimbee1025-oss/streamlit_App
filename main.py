import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import time

st.set_page_config(
    page_title="서울 공영주차장 지도",
    layout="wide"
)

st.title("🚗 서울 공영주차장 정보 서비스")

uploaded = st.file_uploader(
    "CSV 파일 업로드",
    type=["csv"]
)

@st.cache_data
def geocode(addr):
    geolocator = Nominatim(user_agent="parking_app")

    try:
        loc = geolocator.geocode(addr)

        if loc:
            return loc.latitude, loc.longitude

    except:
        pass

    return None, None


if uploaded:

    df = pd.read_csv(
        uploaded,
        encoding="euc-kr"
    )

else:

    df = pd.read_csv(
        "서울시 공영주차장 안내 정보 (1).csv",
        encoding="euc-kr"
    )


#########################################
# 자치구 추출
#########################################

df["자치구"] = df["주소"].str.extract(r"(\\S+구)")

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

filtered = df[df["자치구"] == district]

if free_only:
    filtered = filtered[
        filtered["유무료구분명"] == "무료"
    ]

if weekend_only:
    filtered = filtered[
        filtered["주말 운영 종료시각(HHMM)"].notna()
    ]

#########################################
# 가장 저렴한 주차장
#########################################

tmp = filtered.copy()

tmp["기본 주차 요금"] = (
    pd.to_numeric(
        tmp["기본 주차 요금"],
        errors="coerce"
    )
)

cheap = tmp.loc[
    tmp["기본 주차 요금"].idxmin()
]

st.subheader("💰 가장 저렴한 주차장")

col1, col2, col3 = st.columns(3)

col1.metric(
    "주차장",
    cheap["주차장명"]
)

col2.metric(
    "기본요금",
    f'{cheap["기본 주차 요금"]:.0f}원'
)

col3.metric(
    "주소",
    cheap["주소"]
)

#########################################
# 좌표 처리
#########################################

for idx, row in filtered.iterrows():

    if pd.isna(row["위도"]) or pd.isna(row["경도"]):

        lat, lon = geocode(row["주소"])

        filtered.loc[idx, "위도"] = lat
        filtered.loc[idx, "경도"] = lon

        time.sleep(1)

filtered = filtered.dropna(
    subset=["위도", "경도"]
)

#########################################
# 지도
#########################################

center_lat = filtered["위도"].mean()
center_lon = filtered["경도"].mean()

m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=13
)

for _, row in filtered.iterrows():

    popup = f"""
    <b>{row['주차장명']}</b><br>
    주소 : {row['주소']}<br>
    기본요금 : {row['기본 주차 요금']}원<br>
    무료여부 : {row['유무료구분명']}<br>
    주말운영 :
    {'운영' if pd.notna(row['주말 운영 종료시각(HHMM)']) else '미운영'}
    """

    folium.Marker(
        location=[
            row["위도"],
            row["경도"]
        ],
        tooltip=popup,
        popup=popup
    ).add_to(m)

st_folium(
    m,
    width=1200,
    height=700
)

#########################################
# 표
#########################################

st.subheader("주차장 목록")

st.dataframe(
    filtered[
        [
            "주차장명",
            "주소",
            "유무료구분명",
            "기본 주차 요금",
            "총 주차면"
        ]
    ],
    use_container_width=True
)
