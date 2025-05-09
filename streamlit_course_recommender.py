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
    </style>
    """,
    unsafe_allow_html=True,
)

# 형태소 분석기 초기화
kiwi = Kiwi()

# 데이터 불러오기
df = pd.read_excel("통합_교육과정_데이터셋_6월.xlsx")
# 검색 대상 필드 확장
# 여러 메소드를 메서드 체이닝할 때는 괄호로 묶어 올바른 들여쓰기를 유지합니다.
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

# 기존 CSS: 카드 및 버튼 등 스타일링 (카드 색상은 초록색 계열로 수정)
st.markdown("""
    <style>
    /* 버튼 가운데 정렬 */
    div.stButton > button {
        display: block !important;
        margin: 0 auto !important;
        width: 200px !important;
    }

    /* 카드 스타일: 초록색 계열 + 최소 높이 지정 */
    .card {
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #66bb6a; /* 초록색 외곽선 */
        border-radius: 10px;
        background-color: #e8f5e9; /* 연한 초록 배경색 */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        /* 카드 높이를 최소화하여 내부 콘텐츠에 맞게 조정 */
        min-height: auto;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
    }

    /* 카드 제목 스타일 */
    .card-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #2e7d32; /* 진한 초록색 텍스트 */
    }

    /* 카드 콘텐츠 스타일 */
    .card-content {
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 0.5rem;
    }

    /* 별점 스타일 */
    .rating {
        color: #66bb6a;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }

    /* 대분류 헤더 스타일 */
    .category-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1.5rem 0 0.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4CAF50;
        color: #2e7d32;
    }
    </style>
    """, unsafe_allow_html=True)

# 별점 표시 함수: 10점 만점 기준 5개 별로 환산
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
    selected_categories = []
    cols = st.columns(len(categories))
    for i, category in enumerate(categories):
        if cols[i].checkbox(category, key=f"checkbox_{category}"):
            selected_categories.append(category)
    submitted = st.form_submit_button("🔍 추천 받기")

# 필터링 및 정렬 로직
results = df.copy()
if submitted:
    # 교육방식 필터링 (선택한 경우)
    if selected_categories:
        results = results[results['대분류'].isin(selected_categories)]

    # 키워드 필터링: 키워드가 입력된 경우에만 실행
    if keyword:
        morphs = [token.form for token in kiwi.tokenize(keyword) if len(token.form) > 1]
        keywords = set([keyword] + morphs)
        def compute_score(text):
            return sum(text.lower().count(k.lower()) for k in keywords)
        results['정확도점수'] = results['검색_본문'].apply(compute_score)
        results = results[results['정확도점수'] >= 3]

    # 정렬: 키워드가 있으면 정확도 점수 기준, 없으면 대분류 기준으로 정렬
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
        # 그룹별(대분류) 과정 개수 표시
        category_counts = results['대분류'].value_counts().reindex(category_order).dropna().astype(int).to_dict()
        category_count_display = ", ".join([f"{cat}: {count}건" for cat, count in category_counts.items()])
        st.markdown(category_count_display)

        # 대분류별 그룹화 후 카드 형태로 수평 배치
        grouped_results = results.groupby('대분류')
        for category_name, group in grouped_results:
            st.markdown(f"<div class='category-header'>📚 {category_name}</div>", unsafe_allow_html=True)
            n_cols = 3 # 한 행에 표시할 카드 개수
            cols = st.columns(n_cols)
            for i, (_, row) in enumerate(group.iterrows()):
                # 미리보기 링크 처리
                preview = row.get('미리보기 링크', '')
                if preview and not pd.isna(preview):
                    preview_html = f" (<a href='{preview}' target='_blank' rel='noopener noreferrer'>미리보기</a>)"
                else:
                    preview_html = ''
                card_title = f"📘 {row['과정명']}{preview_html}"

                with cols[i % n_cols]:
                    with st.container():
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
                                    <strong>🎓 학습 목표</strong><br>{row['학습목표']}<br><br>
                                    <strong>📘 학습 내용</strong><br>{re.sub(r'\r\n|\r|\n', '<br>', row['학습내용'])}<br><br>
                                    <strong>🧍 학습 대상</strong><br>{re.sub(r'\r\n|\r|\n', '<br>', row['학습대상'])}
                                </details>
                            </div>
                        </div>
                        """
                        st.markdown(card_html, unsafe_allow_html=True)
