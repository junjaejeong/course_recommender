import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
import math

# 형태소 분석기 초기화
kiwi = Kiwi()

# 데이터 불러오기
df = pd.read_excel("통합_교육과정_데이터셋.xlsx")
# 검색 대상 필드 확장: 여러 필드를 결합하여 하나의 문자열 생성
df['검색_본문'] = df[['과정명', '학습목표', '학습내용', '학습대상', '카테고리1', 'KG카테고리2']]\
    .fillna('').agg(' '.join, axis=1)
df['검색_본문'] = df['검색_본문'].str.replace(r'\n|\t', ' ', regex=True)\
    .str.replace(r'\s+', ' ', regex=True).str.strip()

# Streamlit UI
st.title("🎯 KGM 4월 사이버 교육 추천받기")
st.markdown("관심 있는 키워드를 입력하면 관련된 교육과정을 추천해드립니다.")

# CSS – 카드 UI 및 가로 스크롤 스타일링
st.markdown("""
    <style>
    /* 버튼 가운데 정렬 */
    div.stButton > button {
        display: block !important;
        margin: 0 auto !important;
        width: 200px !important;
    }
    
    /* 카드 컨테이너 스타일: 부모 너비 100% 사용, 좌우 여백 및 간격 적용 */
    .card-container {
        display: flex;
        overflow-x: auto;
        padding: 1rem 0;
        gap: 1rem;
        scrollbar-width: thin;
    }
    
    /* 카드 스타일: 고정 크기, 그림자 효과, hover시 살짝 떠오르는 효과 */
    .card {
        min-width: 280px;
        max-width: 280px;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
        background-color: white;
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
    }
    
    /* 카드 제목 스타일 */
    .card-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #333;
    }
    
    /* 카드 콘텐츠 스타일 */
    .card-content {
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 1rem;
    }
    
    /* 별점 스타일 */
    .rating {
        color: #FFD700;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }
    
    /* 카드 내부 버튼(상세 보기) 스타일 – 여기서는 단순 버튼 모양만 */
    .card-button {
        padding: 5px 10px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.8rem;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        margin-top: 0.5rem;
        transition: background-color 0.3s ease;
    }
    
    .card-button:hover {
        background-color: #45a049;
    }
    
    /* 대분류 헤더 스타일 */
    .category-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1.5rem 0 0.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4CAF50;
        color: #333;
    }
    
    /* 스크롤바 스타일링 */
    .card-container::-webkit-scrollbar {
        height: 6px;
    }
    
    .card-container::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    .card-container::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    
    .card-container::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    
    /* 가로 스크롤 컨테이너가 부모 너비의 100% 사용 */
    .slider-container {
         width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 별점 표시 함수: 10점 만점 점수를 5개 별로 변환하여 표시
def display_rating(score, max_score=10):
    if score is None or score == 'N/A':
        return "⭐ 관련도: N/A"
    star_count = min(5, max(1, round(score * 5 / max_score)))
    return "⭐" * star_count + f" 관련도: {score}점"

# 입력 폼 구성
with st.form(key="search_form"):
    keyword = st.text_input("🔑 관심 키워드 입력", placeholder="예: AI, 엑셀, 디자인, 영어스피킹 등")
    st.markdown("<div style='font-weight: 600; font-size: 16px; margin-top:10px;'>✅ 교육방식 선택</div>", unsafe_allow_html=True)
    categories = df['대분류'].dropna().unique().tolist()
    selected_categories = []
    cols = st.columns(len(categories))
    for i, category in enumerate(categories):
        if cols[i].checkbox(category, key=f"checkbox_{category}"):
            selected_categories.append(category)
    submitted = st.form_submit_button("🔍 추천 받기")

# 필터링 로직
results = df.copy()
if submitted:
    # 교육방식 필터링 (키워드가 없더라도 적용)
    if selected_categories:
        results = results[results['대분류'].isin(selected_categories)]
    
    # 키워드가 입력된 경우에만 키워드 필터링 수행
    if keyword:
        morphs = [token.form for token in kiwi.tokenize(keyword) if len(token.form) > 1]
        keywords = set([keyword] + morphs)
        def compute_score(text):
            return sum(text.lower().count(k.lower()) for k in keywords)
        results['정확도점수'] = results['검색_본문'].apply(compute_score)
        results = results[results['정확도점수'] > 0]
    
    # 정렬: 키워드 있을 경우 정확도 기준, 없으면 대분류 기준
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
        
        # 그룹별(대분류별) 카드 슬라이더 표시
        grouped_results = results.groupby('대분류')
        for category_name, group in grouped_results:
            st.markdown(f"<div class='category-header'>📚 {category_name}</div>", unsafe_allow_html=True)
            st.markdown("<div class='scroll-hint'>→ 오른쪽으로 스크롤하여 더 많은 추천 과정을 확인하세요</div>", unsafe_allow_html=True)
            
            # 카드 슬라이더 컨테이너 (부모 너비 100% 사용)
            slider_html = "<div class='slider-container'>"
            for _, row in group.iterrows():
                card_html = f"""
                <div class='card'>
                    <div class='card-title'>📘 {row['과정명']}</div>
                    <div class='rating'>{display_rating(row.get('정확도점수', 'N/A'))}</div>
                    <div class='card-content'>
                        <div>🏷️ <b>카테고리</b>: {row['카테고리1']} / {
