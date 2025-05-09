import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
import math

# --- CSS 스타일 정의 ---
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');

    body {
        font-family: 'Noto Sans KR', sans-serif;
    }

    .block-container {
        max-width: 95% !important;
        padding-left: 2.5% !important;
        padding-right: 2.5% !important;
    }

    .category-filter {
        margin-bottom: 1rem;
        padding: 0.5rem;
        border: 1px solid #ccc;
        border-radius: 5px;
    }

    .category-filter label {
        font-weight: bold;
        margin-right: 0.5rem;
    }

    .card-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }

    .card {
        flex: 0 0 calc(33% - 1rem); /* 3개씩 배치, 간격 고려 */
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #81D4FA; /* 하늘색 테두리 */
        border-radius: 10px;
        background-color: #E1F5FE; /* 연한 하늘색 배경 */
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        min-height: 200px; /* 카드 최소 높이 조정 */
        display: flex;
        flex-direction: column;
        justify-content: space-between; /* 내용 균등 분배 */
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0, 0, 0, 0.15);
    }

    .card-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1976D2; /* 진한 하늘색 텍스트 */
    }

    .card-content {
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 0.3rem;
    }

    .rating {
        color: #4FC3F7; /* 밝은 하늘색 */
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    .preview-link {
        font-size: 0.8rem;
        color: #1976D2;
        text-decoration: none;
    }

    .preview-link:hover {
        text-decoration: underline;
    }

    .category-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1.5rem 0 0.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4FC3F7; /* 밝은 하늘색 */
        color: #1976D2;
    }

    .expander-title {
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 형태소 분석기 초기화
kiwi = Kiwi()

# 데이터 불러오기
df = pd.read_excel("통합_교육과정_데이터셋_6월.xlsx")
# 검색 대상 필드 확장
df['검색_본문'] = (
    df[['과정명', '학습목표', '학습내용', '학습대상', '카테고리1', 'KG카테고리2']]
    .fillna('')
    .agg(' '.join, axis=1)
)
df['검색_본문'] = (
    df['검색_본문']
    .str.replace(r'\n|\t', ' ', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# Streamlit UI: 타이틀 및 설명
st.title("🎯 KGM 6월 사이버 교육 추천받기")
st.markdown("관심 있는 키워드를 입력하면 관련된 교육과정을 추천해드립니다.")

# 별점 표시 함수
def display_rating(score, max_score=10):
    if score is None or score == 'N/A':
        return "⭐ 관련도: N/A"
    star_count = min(5, max(1, round(score * 5 / max_score)))
    return "⭐" * star_count + f" 관련도: {score}점"

# 검색 폼 구성
with st.form(key="search_form"):
    keyword = st.text_input("🔑 관심 키워드 입력", placeholder="예: AI, 엑셀, 디자인, 영어스피킹 등")
    st.markdown("<div style='font-weight:600; font-size:16px; margin-top:10px;'>✅ 교육방식 선택</div>", unsafe_allow_html=True)
    categories = df['대분류'].dropna().unique().tolist()
    selected_categories = st.multiselect("교육 방식 선택", categories)
    submitted = st.form_submit_button("🔍 추천 받기")

# 필터링 및 정렬 로직
results = df.copy()
if submitted:
    # 교육방식 필터링 (선택한 경우)
    if selected_categories:
        results = results[results['대분류'].isin(selected_categories)]

    # 키워드 필터링
    if keyword:
        morphs = [token.form for token in kiwi.tokenize(keyword) if len(token.form) > 1]
        keywords = set([keyword] + morphs)
        def compute_score(text):
            return sum(text.lower().count(k.lower()) for k in keywords)
        results['정확도점수'] = results['검색_본문'].apply(compute_score)
        results = results[results['정확도점수'] >= 3]

    # 정렬
    category_order = ['직무(무료)', '직무(유료)', '북러닝', '전화외국어', '외국어']
    results['대분류'] = pd.Categorical(results['대분류'], categories=category_order, ordered=True)
    if '정확도점수' in results.columns:
        results = results.sort_values(by=['대분류', '정확도점수'], ascending=[True, False])
    else:
        results = results.sort_values(by='대분류')

    st.markdown(f"### 🔎 '{keyword if keyword else '모든'}' 관련 추천 교육과정: {len(results)}건")
    if results.empty:
        st.warning("입력하신 키워드에 적합한 과정이 없습니다. 다른 키워드를 시도해보세요.")
    else:
        # 그룹별 과정 개수 표시
        category_counts = results['대분류'].value_counts().reindex(category_order).dropna().astype(int).to_dict()
        category_count_display = ", ".join([f"{cat}: {count}건" for cat, count in category_counts.items()])
        st.markdown(category_count_display)

        # 대분류별 그룹화 후 카드 형태로 표시
        grouped_results = results.groupby('대분류')
        for category_name, group in grouped_results:
            st.markdown(f"<div class='category-header'>📚 {category_name}</div>", unsafe_allow_html=True)
            st.markdown("<div class='card-container'>", unsafe_allow_html=True)
            for _, row in group.iterrows():
                preview = row.get('미리보기 링크', '')
                preview_html = f" (<a href='{preview}' target='_blank' rel='noopener noreferrer' class='preview-link'>미리보기</a>)" if preview and not pd.isna(preview) else ''
                card_title = f"📘 {row['과정명']}{preview_html}"

                card_html = f"""
                    <div class='card'>
                        <div>
                            <div class='card-title'>{card_title}</div>
                            <div class='rating'>{display_rating(row.get('정확도점수', 'N/A'))}</div>
                            <div class='card-content'>🏷️ 카테고리: {row['카테고리1']} / {row['KG카테고리2']}</div>
                            <div class='card-content'>⏱️ 학습 시간: {row['학습인정시간']} 시간</div>
                            <div class='card-content'>🎯 수료 기준: {row['수료기준']}</div>
                        </div>
                        <div>
                            <details>
                                <summary class='expander-title'>📖 상세 정보</summary>
                                <div>
                                    <br>
                                    <strong>🎓 학습 목표</strong><br>
                                    {row['학습목표']}<br><br>
                                    <strong>📘 학습 내용</strong><br>
                                    {row['학습내용']}<br><br>
                                    <strong>🧍 학습 대상</strong><br>
                                    {row['학습대상']}
                                </div>
                            </details>
                        </div>
                    </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
