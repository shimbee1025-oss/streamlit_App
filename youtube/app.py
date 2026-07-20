import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
from wordcloud import WordCloud
from konlpy.tag import Okt
from collections import Counter
import re
import matplotlib.font_manager as fm

st.set_page_config(
    page_title="유튜브 댓글 분석기",
    layout="wide"
)

# ==========================
# API
# ==========================
API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

FONT_PATH = "fonts/NanumGothic.ttf"

# 한글 깨짐 방지
if fm.findSystemFonts(fontpaths=["fonts"]):
    plt.rc("font", family="NanumGothic")
plt.rcParams["axes.unicode_minus"] = False


# ==========================
# 영상 ID 추출
# ==========================
def extract_video_id(url):

    patterns = [
        r"v=([^&]+)",
        r"youtu\.be/([^?&]+)",
        r"shorts/([^?&]+)"
    ]

    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)

    return None


# ==========================
# 영상 정보
# ==========================
def get_video_info(video_id):

    response = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    ).execute()

    if not response["items"]:
        return None

    item = response["items"][0]

    return {
        "title":
            item["snippet"]["title"],
        "channel":
            item["snippet"]["channelTitle"],
        "views":
            int(item["statistics"].get("viewCount", 0))
    }


# ==========================
# 댓글 수집
# ==========================
@st.cache_data(show_spinner=False)
def get_comments(video_id, max_comments):

    comments = []

    request = youtube.commentThreads().list(
        part="snippet",
        videoId=video_id,
        maxResults=100,
        textFormat="plainText"
    )

    while request and len(comments) < max_comments:

        response = request.execute()

        for item in response["items"]:

            snippet = (
                item["snippet"]
                ["topLevelComment"]
                ["snippet"]
            )

            comments.append({
                "댓글":
                    snippet["textDisplay"],
                "좋아요":
                    snippet["likeCount"],
                "작성시간":
                    snippet["publishedAt"]
            })

            if len(comments) >= max_comments:
                break

        request = youtube.commentThreads().list_next(
            request,
            response
        )

    return pd.DataFrame(comments)


# ==========================
# 워드클라우드
# ==========================
def create_wordcloud(texts):

    okt = Okt()
    nouns = []

    for text in texts:

        text = re.sub(
            r"[^가-힣 ]",
            " ",
            str(text)
        )

        nouns.extend(
            [
                n
                for n in okt.nouns(text)
                if len(n) >= 2
            ]
        )

    counter = Counter(nouns)

    if len(counter) == 0:
        return None

    return WordCloud(
        font_path=FONT_PATH,
        background_color="white",
        width=1200,
        height=600
    ).generate_from_frequencies(counter)


# ==========================
# UI
# ==========================
st.title("🎬 유튜브 댓글 분석기")

url = st.text_input(
    "유튜브 링크 입력"
)

comment_count = st.slider(
    "댓글 개수",
    100,
    3000,
    500,
    100
)

if st.button("분석 시작"):

    video_id = extract_video_id(url)

    if not video_id:
        st.error("올바른 링크를 입력하세요.")
        st.stop()

    info = get_video_info(video_id)

    if info is None:
        st.error("영상을 찾을 수 없습니다.")
        st.stop()

    st.subheader(info["title"])
    st.caption(
        f'{info["channel"]} · 조회수 {info["views"]:,}'
    )

    st.video(
        f"https://www.youtube.com/watch?v={video_id}"
    )

    with st.spinner("댓글 수집 중..."):
        df = get_comments(
            video_id,
            comment_count
        )

    if len(df) == 0:
        st.warning("댓글이 없습니다.")
        st.stop()

    st.success(
        f"{len(df)}개 댓글 분석 완료!"
    )

    # -----------------------
    # 기본 통계
    # -----------------------
    c1, c2, c3 = st.columns(3)

    c1.metric(
        "댓글 수",
        len(df)
    )

    c2.metric(
        "평균 좋아요",
        round(
            df["좋아요"].mean(),
            2
        )
    )

    c3.metric(
        "최대 좋아요",
        int(
            df["좋아요"].max()
        )
    )

    # -----------------------
    # 시간대 분석
    # -----------------------
    st.subheader(
        "📈 시간대별 댓글 작성 추이"
    )

    df["작성시간"] = pd.to_datetime(
        df["작성시간"]
    )

    df["시간"] = (
        df["작성시간"].dt.hour
    )

    hour_df = (
        df.groupby("시간")
        .size()
        .reindex(
            range(24),
            fill_value=0
        )
    )

    fig, ax = plt.subplots(
        figsize=(10, 4)
    )

    ax.plot(
        hour_df.index,
        hour_df.values,
        marker="o"
    )

    ax.set_xticks(range(24))

    st.pyplot(fig)

    # -----------------------
    # 좋아요 분포
    # -----------------------
    st.subheader(
        "🔥 댓글 반응도"
    )

    fig2, ax2 = plt.subplots()

    ax2.hist(
        df["좋아요"],
        bins=20
    )

    st.pyplot(fig2)

    # -----------------------
    # 인기 댓글
    # -----------------------
    st.subheader(
        "👍 인기 댓글 TOP10"
    )

    st.dataframe(
        df.sort_values(
            "좋아요",
            ascending=False
        ).head(10),
        use_container_width=True
    )

    # -----------------------
    # 워드클라우드
    # -----------------------
    st.subheader(
        "☁️ 워드클라우드"
    )

    wc = create_wordcloud(
        df["댓글"]
    )

    if wc:

        fig3, ax3 = plt.subplots(
            figsize=(12, 6)
        )

        ax3.imshow(
            wc,
            interpolation="bilinear"
        )

        ax3.axis("off")

        st.pyplot(fig3)
