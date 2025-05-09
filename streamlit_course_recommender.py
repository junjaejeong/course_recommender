import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
import math

# 페이지 기본 설정
st.set_page_config(
    page_title="KGM 6월 사이버 교육 추천",
    page_icon="🎯",
    layout="wide"
)

# 시각적 계층구조 개선: 전체 페이지 여백 및 레이아웃 설정
st.markdown(
    """
    <style>
    .block-container {
        max-width: 1200px !important;
        padding-left: 5% !important;
        padding-right: 5% !important;
        margin: 0 auto !important;
    }
    
    /* 헤더 영역 강화 */
    .header-container {
        background-color: #f0f7ff;
        padding: 2rem 2rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 5px solid #4285F4;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .main-title {
        color: #1a3d82;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .subtitle {
        color: #555;
        font-size: 1.1rem;
        font-weight: 400;
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

# 헤더 영역 개선
with st.container():
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    st.markdown('<h1 class="main-title">🎯 KGM 6월 사이버 교육 추천받기</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">관심 있는 키워드를 입력하면 관련된 교육과정을 추천해드립니다.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# UI 요소 및 상호작용 개선을 위한 CSS
st.markdown("""
    <style>
    /* 검색 폼 스타일링 */
    .search-container {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    /* 버튼 개선 */
    div.stButton > button {
        background-color: #4285F4 !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.5rem 1.5rem !important;
        border-radius: 8px !important;
        transition: all 0.3s !important;
        display: block !important;
        margin: 0 auto !important;
        width: 200px !important;
        box-shadow: 0 4px 6px rgba(66, 133, 244, 0.3) !important;
    }
    
    div.stButton > button:hover {
        background-color: #3367D6 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 8px rgba(66, 133, 244, 0.4) !important;
    }
    
    div.stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* 필터 선택 UI 개선 */
    .filter-option {
        background-color: #e9ecef;
        border-radius: 20px;
        padding: 8px 15px;
        font-size: 0.9rem;
        display: inline-block;
        margin-right: 10px;
        margin-bottom: 10px;
        cursor: pointer;
        transition: all 0.2s;
        border: 1px solid #dee2e6;
    }
    
    .filter-option.active {
        background-color: #4285F4;
        color: white;
        border-color: #3367D6;
    }
    
    /* 카드 디자인 균일화 및 개선 */
    .card {
        padding: 1.2rem;
        margin-bottom: 1.5rem;
        border-radius: 12px;
        background-color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        border-top: 4px solid #4285F4;
        min-height: 280px;
        display: flex;
        flex-direction: column;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    /* 카드 제목 스타일 */
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #1a3d82;
        line-height: 1.4;
    }
    
    /* 카드 콘텐츠 스타일 */
    .card-content {
        font-size: 0.9rem;
        color: #444;
        margin-bottom: 0.7rem;
        display: flex;
        align-items: center;
    }
    
    .card-content i {
        margin-right: 8px;
        color: #4285F4;
    }
    
    /* 관련도 표시 방법 개선 */
    .relevance {
        margin: 0.8rem 0;
    }
    
    .relevance-meter {
        height: 6px;
        background-color: #e9ecef;
        border-radius: 3px;
        margin-top: 5px;
        overflow: hidden;
    }
    
    .relevance-value {
        height: 100%;
        background: linear-gradient(90deg, #4285F4, #34A853);
        border-radius: 3px;
    }
    
    /* 대분류 헤더 스타일 개선 */
    .category-header {
        font-size: 1.4rem;
        font-weight: 700;
        margin: 2rem 0 1.2rem 0;
        padding: 0.7rem 1rem;
        border-radius: 8px;
        background-color: #f0f7ff;
        color: #1a3d82;
        display: flex;
        align-items: center;
    }
    
    .category-header i {
        margin-right: 10px;
        color: #4285F4;
    }
    
    /* 확장 영역 스타일 */
    .expander-content {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.5rem;
    }
    
    .expander-title {
        font-size: 1rem;
        font-weight: 600;
        color: #1a3d82;
        margin-bottom: 0.5rem;
    }
    
    /* 결과 요약 정보 */
    .results-summary {
        background-color: #f0f7ff;
        padding: 0.8rem 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #4285F4;
    }
    
    /* 검색창 스타일 */
    .search-input-container {
        margin-bottom: 1rem;
    }
    
    /* 검색어 하이라이트 */
    .highlight {
        background-color: #ffff00;
        padding: 0 2px;
        border-radius: 2px;
    }
    
    /* 미리보기 링크 */
    .preview-link {
        color: #4285F4;
        text-decoration: none;
        font-weight: 600;
        font-size: 0.85rem;
        position: absolute;
        top: 1.2rem;
        right: 1.2rem;
    }
    
    .preview-link:hover {
        text-decoration: underline;
    }
    </style>
    """, unsafe_allow_html=True)

# 개선된 검색 폼 (레이아웃 최적화)
st.markdown('<div class="search-container">', unsafe_allow_html=True)
col1, col2 = st.columns([3, 1])

with col1:
    keyword = st.text_input("🔍 관심 키워드 입력", placeholder="예: AI, 엑셀, 디자인, 영어스피킹 등", key="search_input")

with col2:
    st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
    search_button = st.button("🔍 추천 받기")

st.markdown("<div style='font-weight:600; font-size:16px; margin-top:10px; margin-bottom:10px;'>✅ 교육방식 선택</div>", unsafe_allow_html=True)

# 교육방식 필터 개선 (버튼형 UI)
categories = df['대분류'].dropna().unique().tolist()
category_options = []

col_filter = st.columns(len(categories))
selected_categories = []

for i, category in enumerate(categories):
    if col_filter[i].checkbox(category, key=f"checkbox_{category}"):
        selected_categories.append(category)
st.markdown('</div>', unsafe_allow_html=True)

# 필터링 및 정렬 로직
results = df.copy()
if search_button or keyword:  # 검색 버튼을 누르거나 키워드가 입력된 경우
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
        results = results[results['정확도점수'] > 0]  # 0점보다 높은 것만 표시 (기준을 3에서 조정)

    # 정렬: 키워드가 있으면 정확도 점수 기준, 없으면 대분류 기준으로 정렬
    category_order = ['직무(무료)', '직무(유료)', '북러닝', '전화외국어', '외국어']
    results['대분류'] = pd.Categorical(results['대분류'], categories=category_order, ordered=True)
    if '정확도점수' in results.columns:
        results = results.sort_values(by=['정확도점수', '대분류'], ascending=[False, True])
    else:
        results = results.sort_values(by='대분류')

    # 결과 표시 개선
    if not results.empty:
        # 그룹별(대분류) 과정 개수 표시 (개선된 디자인)
        category_counts = results['대분류'].value_counts().reindex(category_order).dropna().astype(int).to_dict()
        
        # 결과 요약 정보 표시
        st.markdown(f"<div class='results-summary'>", unsafe_allow_html=True)
        st.markdown(f"### 🔎 '{keyword if keyword else '모든'}' 관련 추천 교육과정: {len(results)}건")
        category_count_display = " | ".join([f"<b>{cat}</b>: {count}건" for cat, count in category_counts.items()])
        st.markdown(f"<p>{category_count_display}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # 대분류별 그룹화 후 카드 형태로 수평 배치 (개선된 카드 디자인)
        grouped_results = results.groupby('대분류')
        for category_name, group in grouped_results:
            st.markdown(f"<div class='category-header'><i>📚</i> {category_name}</div>", unsafe_allow_html=True)
            
            # 반응형 그리드 적용 (화면 크기에 따라 조정)
            n_cols = 3  # 기본값
            cols = st.columns(n_cols)
            
            for i, (_, row) in enumerate(group.iterrows()):
                # 미리보기 링크 처리
                preview = row.get('미리보기 링크', '')
                preview_html = ''
                if preview and not pd.isna(preview):
                    preview_html = f"<a href='{preview}' target='_blank' rel='noopener noreferrer' class='preview-link'>📑 미리보기</a>"
                
                # 관련도 계산 (10점 만점 기준)
                relevance_score = row.get('정확도점수', 0)
                max_score = results['정확도점수'].max() if '정확도점수' in results.columns and len(results) > 0 else 10
                relevance_percent = min(100, max(10, int(relevance_score / max_score * 100))) if max_score > 0 else 10
                
                with cols[i % n_cols]:
                    card_html = f"""
                    <div class='card'>
                        {preview_html}
                        <div class='card-title'>📘 {row['과정명']}</div>
                        
                        <div class='relevance'>
                            <div style='display: flex; justify-content: space-between;'>
                                <span style='font-size: 0.85rem; color: #666;'>관련도:</span>
                                <span style='font-size: 0.85rem; font-weight: 600; color: #4285F4;'>{relevance_score if relevance_score > 0 else 'N/A'}</span>
                            </div>
                            <div class='relevance-meter'>
                                <div class='relevance-value' style='width: {relevance_percent}%;'></div>
                            </div>
                        </div>
                        
                        <div class='card-content'><i>🏷️</i> <b>카테고리:</b> {row['카테고리1']} / {row['KG카테고리2']}</div>
                        <div class='card-content'><i>⏱️</i> <b>학습 시간:</b> {row['학습인정시간']} 시간</div>
                        <div class='card-content'><i>🎯</i> <b>수료 기준:</b> {row['수료기준']}</div>
                        
                        <div style='margin-top: auto;'>
                            <details class='expander'>
                                <summary style='color: #4285F4; font-weight: 600; cursor: pointer; margin-top: 10px;'>
                                    상세 정보 보기
                                </summary>
                                <div class='expander-content'>
                                    <p class='expander-title'>🎓 학습 목표</p>
                                    <p>{row['학습목표']}</p>
                                    
                                    <p class='expander-title'>📘 학습 내용</p>
                                    <p>{row['학습내용']}</p>
                                    
                                    <p class='expander-title'>🧍 학습 대상</p>
                                    <p>{row['학습대상']}</p>
                                </div>
                            </details>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.warning("⚠️ 입력하신 키워드에 적합한 과정이 없습니다. 다른 키워드를 시도해보세요.")
