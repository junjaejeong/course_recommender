import streamlit as st
import pandas as pd
import math

# 데이터 불러오기
df = pd.read_excel("통합_교육과정_데이터셋.xlsx")
# 검색 대상 필드 확장
df['검색_본문'] = df[['과정명', '학습목표', '학습내용', '학습대상', '카테고리1', 'KG카테고리2']].fillna('').agg(' '.join, axis=1)
df['검색_본문'] = df['검색_본문'].str.replace(r'\n|\t', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip()

# Streamlit UI
st.title("🎯 KGM 4월 사이버 교육 추천받기")
st.markdown("관심 있는 키워드를 입력하면 관련된 교육과정을 추천해드립니다.")

# CSS 추가: 카드 UI 및 가로 스크롤 스타일링
st.markdown("""
    <style>
    /* 버튼 가운데 정렬 */
    div.stButton > button {
        display: block !important;
        margin: 0 auto !important;
        width: 200px !important;
    }
    
    /* 카드 컨테이너 스타일 */
    .card-container {
        display: flex;
        overflow-x: auto;
        padding: 1rem 0;
        gap: 1rem;
        scrollbar-width: thin;
    }
    
    /* 카드 스타일 */
    .card {
        min-width: 280px;
        max-width: 280px;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1), 0 1px 3px rgba(0, 0, 0, 0.08);
        background-color: white;
        transition: transform 0.3s ease;
        height: 100%;
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
    
    /* 카드 내부 버튼 스타일 */
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
    
    /* 가로 스크롤 안내 텍스트 */
    .scroll-hint {
        font-size: 0.8rem;
        color: #666;
        font-style: italic;
        margin-bottom: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)

# 별점 표시 함수
def display_rating(score, max_score=10):
    if score is None or score == 'N/A':
        return "⭐ 관련도: N/A"
    
    # 10점 만점에 5개 별로 변환
    star_count = min(5, max(1, round(score * 5 / max_score)))
    return "⭐" * star_count + f" 관련도: {score}점"

# 입력 폼 구성
with st.form(key="search_form"):
    keyword = st.text_input("🔑 관심 키워드 입력", placeholder="예: AI, 엑셀, 디자인, 영어스피킹 등")
    # 교육방식 선택 제목
    st.markdown("<div style='font-weight: 600; font-size: 16px; margin-top:10px;'>✅ 교육방식 선택</div>", unsafe_allow_html=True)
    categories = df['대분류'].dropna().unique().tolist()
    selected_categories = []
    cols = st.columns(len(categories))
    for i, category in enumerate(categories):
        if cols[i].checkbox(category, key=f"checkbox_{category}"):
            selected_categories.append(category)
    
    # 버튼을 중앙에 위치
    submitted = st.form_submit_button("🔍 추천 받기")

# 필터링 로직
results = df.copy()
if submitted:
    # (선택 사항) 먼저 교육방식에 따른 필터링 적용
    if selected_categories:
        results = results[results['대분류'].isin(selected_categories)]
    
    # 키워드가 입력된 경우에만 키워드 필터링 수행
    if keyword:
        # 형태소 분석 대신 간단한 단어 분리 사용
        simple_words = [k.strip() for k in keyword.split() if len(k.strip()) > 1]
        keywords = set([keyword] + simple_words)
        def compute_score(text):
            return sum(text.lower().count(k.lower()) for k in keywords)
        results['정확도점수'] = results['검색_본문'].apply(compute_score)
        results = results[results['정확도점수'] > 0]
    
    # 정렬: 키워드가 있으면 정확도 점수 기준, 없으면 대분류 기준으로 정렬
    category_order = ['직무(무료)', '직무(유료)', '북러닝', '전화외국어', '외국어']
    results['대분류'] = pd.Categorical(results['대분류'], categories=category_order, ordered=True)
    if '정확도점수' in results.columns:
        results = results.sort_values(by=['대분류', '정확도점수'], ascending=[True, False])
    else:
        results = results.sort_values(by='대분류')
    
    # 결과 표시
    st.markdown(f"### 🔎 '{keyword if keyword else '모든'}' 관련 추천 교육과정: {len(results)}건")
    if results.empty:
        st.warning("입력하신 키워드에 적합한 과정이 없습니다. 다른 키워드를 시도해보세요.")
    else:
        category_counts = results['대분류'].value_counts().reindex(category_order).dropna().astype(int).to_dict()
        category_count_display = ", ".join([f"{cat}: {count}건" for cat, count in category_counts.items()])
        st.markdown(category_count_display)
        
        # 대분류별로 그룹화
        grouped_results = results.groupby('대분류')
        
        for category_name, group in grouped_results:
            # 대분류 제목 표시
            st.markdown(f"<div class='category-header'>📚 {category_name}</div>", unsafe_allow_html=True)
            st.markdown("<div class='scroll-hint'>→ 오른쪽으로 스크롤하여 더 많은 추천 과정을 확인하세요</div>", unsafe_allow_html=True)
            
            # 카드 컨테이너 시작
            st.markdown("<div class='card-container'>", unsafe_allow_html=True)
            
            # 각 과정을 카드로 표시
            for _, row in group.iterrows():
                card_html = f"""
                <div class='card'>
                    <div class='card-title'>📘 {row['과정명']}</div>
                    <div class='rating'>{display_rating(row.get('정확도점수', 'N/A'))}</div>
                    <div class='card-content'>
                        <div>🏷️ <b>카테고리</b>: {row['카테고리1']} / {row['KG카테고리2']}</div>
                        <div>⏱️ <b>학습 시간</b>: {row['학습인정시간']}시간</div>
                        <div>🎯 <b>수료 기준</b>: {row['수료기준']}</div>
                    </div>
                """
                
                # 상세보기 버튼을 클릭하면 모달 표시되도록 고유 ID 생성
                detail_id = f"detail_{hash(row['과정명'])}"
                card_html += f"""
                    <button class='card-button' 
                            onclick="document.getElementById('{detail_id}').style.display='block'">
                        📖 상세 보기
                    </button>
                </div>
                """
                
                st.markdown(card_html, unsafe_allow_html=True)
            
            # 카드 컨테이너 닫기
            st.markdown("</div>", unsafe_allow_html=True)
            
            # 각 과정의 상세 정보 모달 생성
            for _, row in group.iterrows():
                detail_id = f"detail_{hash(row['과정명'])}"
                # Streamlit은 JavaScript modal을 직접 지원하지 않으므로 expander로 대체
                with st.expander(f"📖 {row['과정명']} 상세 정보"):
                    st.markdown("🎓 **학습 목표**")
                    st.markdown(row['학습목표'])
                    st.markdown("📘 **학습 내용**")
                    st.markdown(row['학습내용'])
                    st.markdown("🧍 **학습 대상**")
                    st.markdown(row['학습대상'])
                    
        # 아무것도 선택하지 않았을 때 안내
        if not selected_categories and not keyword:
            st.info("키워드를 입력하거나 교육방식을 선택하여 추천받으세요.")
