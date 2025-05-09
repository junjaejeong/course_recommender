import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
import math

# -----------------------
# CSS 스타일 정의
# -----------------------
st.markdown("""
<style>
/* 컨테이너 전체 여백 */
.block-container {
    max-width: 100% !important;
    padding-left: 10% !important;
    padding-right: 10% !important;
}

/* 필터 영역 고정 (sticky) */
.filter-container {
    position: sticky;
    top: 0;
    background-color: white;
    z-index: 100;
    padding: 1rem 0;
    border-bottom: 1px solid #ddd;
}

/* 토글 칩 스타일 (st.multiselect 대체 옵션) */
.chip {
    display: inline-block;
    padding: 0.5rem 1rem;
    margin: 0.25rem;
    border: 1px solid #4CAF50;
    border-radius: 20px;
    cursor: pointer;
    user-select: none;
}
.chip-selected {
    background-color: #4CAF50;
    color: white;
}

/* 카드 그리드 컨테이너 */
.card-container {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    grid-gap: 1rem;
    margin-top: 1rem;
}

/* 카드 스타일 */
.card {
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
    padding: 1rem;
    border: 1px solid #66bb6a;
    border-radius: 10px;
    background-color: #e8f5e9;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 8px 12px rgba(0,0,0,0.15);
}

.card-title {
    font-size: 1.2rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #2e7d32;
}

.rating {
    font-size: 1.2rem;
    margin-bottom: 0.5rem;
    color: #66bb6a;
}

.card-content {
    font-size: 0.9rem;
    color: #555;
    margin-bottom: 0.5rem;
}

.category-header {
    font-size: 1.5rem;
    font-weight: bold;
    margin-top: 2rem;
    margin-bottom: 0.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #4CAF50;
    color: #2e7d32;
}

/* 모바일 대응 */
@media (max-width: 768px) {
    .card-container {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# 형태소 분석기 초기화
# -----------------------
kiwi = Kiwi()

# -----------------------
# 데이터 로드 및 전처리
# -----------------------
df = pd.read_excel("통합_교육과정_데이터셋_6월.xlsx")
# 검색용 본문 컬럼 생성
search_cols = ['과정명', '학습목표', '학습내용', '학습대상', '카테고리1', 'KG카테고리2']
df['검색_본문'] = (
    df[search_cols]
    .fillna('')
    .agg(' '.join, axis=1)
    .str.replace(r'\n|\t', ' ', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# -----------------------
# display_rating 함수
# -----------------------
def display_rating(score, max_score=10):
    if score is None or score == 'N/A':
        return "⭐ 관련도: N/A"
    star_count = min(5, max(1, round(score * 5 / max_score)))
    return "⭐" * star_count + f" 관련도: {score}점"

# -----------------------
# Streamlit UI
# -----------------------
st.title("🎯 KGM 6월 사이버 교육 추천받기")
st.markdown("관심 있는 키워드를 입력하면 관련된 교육과정을 추천해드립니다.")

# 필터 섹션 (sticky)
st.markdown("<div class='filter-container'>", unsafe_allow_html=True)
# 키워드 입력
keyword = st.text_input("🔑 관심 키워드 입력", placeholder="예: AI, 엑셀, 디자인, 영어스피킹 등")
# 교육방식 선택: multiselect로 토글 칩 효과
categories = df['대분류'].dropna().unique().tolist()
selected_categories = st.multiselect("✅ 교육방식 선택", options=categories)
# 검색 버튼
if st.button("🔍 추천 받기"):
    submitted = True
else:
    submitted = False
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------
# 필터링 및 결과 렌더링
# -----------------------
results = df.copy()
if submitted:
    # 교육방식 필터링
    if selected_categories:
        results = results[results['대분류'].isin(selected_categories)]
    # 키워드 기반 필터링 및 점수 산출
    if keyword:
        morphs = [t.form for t in kiwi.tokenize(keyword) if len(t.form) > 1]
        keys = set([keyword] + morphs)
        def comp(text): return sum(text.lower().count(k.lower()) for k in keys)
        results['정확도점수'] = results['검색_본문'].apply(comp)
        results = results[results['정확도점수'] >= 3]
    # 정렬
    order = ['직무(무료)', '직무(유료)', '북러닝', '전화외국어', '외국어']
    results['대분류'] = pd.Categorical(results['대분류'], categories=order, ordered=True)
    if '정확도점수' in results:
        results = results.sort_values(by=['대분류','정확도점수'], ascending=[True,False])
    else:
        results = results.sort_values(by='대분류')

    # 결과 헤더
    st.markdown(f"### 🔎 '{keyword or '모든'}' 관련 추천 교육과정: {len(results)}건")
    if results.empty:
        st.warning("적합한 과정이 없습니다. 다른 키워드를 시도해보세요.")
    else:
        # 각 대분류별 렌더링
        html = []
        current_cat = None
        for _, row in results.iterrows():
            if row['대분류'] != current_cat:
                current_cat = row['대분류']
                html.append(f"<div class='category-header'>📚 {current_cat}</div>")
                html.append("<div class='card-container'>")
            # 미리보기 링크 처리
            preview = row.get('미리보기 링크', '')
            if preview and not pd.isna(preview):
                preview_html = f" (<a href='{preview}' target='_blank'>미리보기</a>)"
            else:
                preview_html = ''
            # 카드 HTML
            card = f"""
            <div class='card'>
              <div class='card-title'>📘 {row['과정명']}{preview_html}</div>
              <div class='rating'>{display_rating(row.get('정확도점수','N/A'))}</div>
              <div class='card-content'><strong>⏱️ {row['학습인정시간']}시간</strong></div>
              <details>
                <summary>📖 상세 정보</summary>
                <p><strong>🏷️ 카테고리:</strong> {row['카테고리1']} / {row['KG카테고리2']}</p>
                <p><strong>🎯 학습 목표:</strong> {row['학습목표']}</p>
                <p><strong>📘 학습 내용:</strong> {row['학습내용']}</p>
                <p><strong>🧍 학습 대상:</strong> {row['학습대상']}</p>
                <p><strong>🎯 수료 기준:</strong> {row['수료기준']}</p>
              </details>
            </div>
            """
            html.append(card)
            # 다음 카테고리 오면 닫기
            next_idx = results.index.get_loc(_)
            if next_idx + 1 == len(results) or results.iloc[next_idx+1]['대분류'] != current_cat:
                html.append("</div>")
        st.markdown('\n'.join(html), unsafe_allow_html=True)
