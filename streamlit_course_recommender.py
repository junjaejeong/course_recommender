import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
import math
import re  # 정규 표현식 라이브러리 추가

# 추가 CSS: 좌우 여백 지정 (전체 너비 사용하며 좌우에 여백 확보)
st.markdown(
    """
    <style>
    .block-container {
        max-width: 100% !important;
        padding-left: 10% !important;
        padding-right: 10% !important;
    }

    /* 카드 그룹을 감싸는 div 스타일 */
    .card-row {
        display: flex;
        flex-direction: row;
        align-items: stretch;
        gap: 1rem;
        margin-bottom: 1rem; /* 카드 그룹 사이 간격 */
    }

    /* 변경된 카드 스타일 */
    .card {
        padding: 1.2rem;
        border: 1px solid #90caf9;
        border-radius: 8px;
        background-color: #e3f2fd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        min-height: auto; /* 더 이상 고정 높이 불필요 */
        display: flex;
        flex-direction: column;
        flex: 1; /* 각 카드가 남은 공간을 균등하게 차지하도록 */
    }

    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 5px 8px rgba(0,0,0,0.15);
        border-color: #64b5f6;
    }

    .card-title {
        font-size: 1.15rem;
        font-weight: 600;
        margin-bottom: 0.6rem;
        color: #1e88e5;
    }

    .card-content {
        font-size: 0.95rem;
        color: #424242;
        margin-bottom: 0.6rem;
        display: flex;
        align-items: center;
    }

    .card-content > span {
        margin-left: 0.4rem;
    }

    .rating {
        color: #fdd835;
        font-size: 1.3rem;
        margin-bottom: 0.7rem;
    }

    .category-header {
        font-size: 1.6rem;
        font-weight: bold;
        margin: 1.8rem 0 0.6rem 0;
        padding-bottom: 0.6rem;
        border-bottom: 2px solid #1976d2;
        color: #1e88e5;
    }

    details {
        margin-top: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 형태소 분석기 초기화
kiwi = Kiwi()

# 데이터 불러오기
df = pd.read_excel("통합_교육과정_데이터셋_6월.xlsx")
df['검색_본문'] = (
    df[['과정명', '학습목표', '학습내용', '학습대상', '카테고리1', 'KG카테고리2']]
    .fillna('')
    .agg(' '.join, axis=1)
    .str.replace(r'\n|\t', ' ', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

def display_rating(score, max_score=10):
    if score is None or score == 'N/A':
        return "⭐ 관련도: N/A"
    star_count = min(5, max(1, round(score * 5 / max_score)))
    return "⭐" * star_count + f" 관련도: {score}점"

with st.form(key="search_form"):
    keyword = st.text_input("🔑 관심 키워드 입력", placeholder="예: AI, 엑셀, 디자인, 영어스피킹 등")
    st.markdown("<div style='font-weight:600; font-size:16px; margin-top:10px;'>✅ 교육방식 선택</div>", unsafe_allow_html=True)
    categories = df['대분류'].dropna().unique().tolist()
    selected_categories = []
    cols = st.columns(len(categories))
    for i, category in enumerate(categories):
        if cols[i].checkbox(category, key=f"checkbox_{category}"):
            selected_categories.append(category)
    submitted = st.form_submit_button("🔍 추천 받기")

results = df.copy()
if submitted:
    if selected_categories:
        results = results[results['대분류'].isin(selected_categories)]
    if keyword:
        morphs = [token.form for token in kiwi.tokenize(keyword) if len(token.form) > 1]
        keywords = set([keyword] + morphs)
        def compute_score(text):
            return sum(text.lower().count(k.lower()) for k in keywords)
        results['정확도점수'] = results['검색_본문'].apply(compute_score)
        results = results[results['정확도점수'] >= 3]

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
        category_counts = results['대분류'].value_counts().reindex(category_order).dropna().astype(int).to_dict()
        category_count_display = ", ".join([f"{cat}: {count}건" for cat, count in category_counts.items()])
        st.markdown(category_count_display)

        grouped_results = results.groupby('대분류')
        for category_name, group in grouped_results:
            st.markdown(f"<div class='category-header'>📚 {category_name}</div>", unsafe_allow_html=True)
            n_cols = 3
            for i in range(0, len(group), n_cols):
                row_of_cards = group.iloc[i:i + n_cols]
                st.markdown("<div class='card-row'>", unsafe_allow_html=True)
                for _, row in row_of_cards.iterrows():
                    preview = row.get('미리보기 링크', '')
                    preview_html = f" (<a href='{preview}' target='_blank' rel='noopener noreferrer'>미리보기</a>)" if preview and not pd.isna(preview) else ''
                    card_title = f"📘 {row['과정명']}{preview_html}"

                    card_html = f"""
                    <div class='card'>
                        <div class='card-title'>{card_title}</div>
                        <div class='rating'>{display_rating(row.get('정확도점수', 'N/A'))}</div>
                        <div class='card-content'><strong>🏷️ 카테고리:</strong> {row['카테고리1']} / {row['KG카테고리2']}</div>
                        <div class='card-content'><strong>⏱️ 학습 시간:</strong> {row['학습인정시간']} 시간</div>
                        <div class='card-content'><strong>🎯 수료 기준:</strong> {row['수료기준']}</div>
                        <div class='card-content'>
                            <details>
                                <summary>📖 상세 정보</summary>
                                <strong>🎓 학습 목표</strong><br>{re.sub(r'\r\n|\r|\n', '<br>', row['학습목표'])}<br><br>
                                <strong>📘 학습 내용</strong><br>{re.sub(r'\r\n|\r|\n', '<br>', row['학습내용'])}<br><br>
                                <strong>🧍 학습 대상</strong><br>{re.sub(r'\r\n|\r|\n', '<br>', row['학습대상'])}
                            </details>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
