import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
import streamlit.components.v1 as components

# 형태소 분석기 초기화
kiwi = Kiwi()

# 데이터 불러오기
df = pd.read_excel("통합_교육과정_데이터셋.xlsx")
# 검색 대상 필드 확장: 과정명, 학습목표, 학습내용, 학습대상, 카테고리1, KG카테고리2
df['검색_본문'] = df[['과정명', '학습목표', '학습내용', '학습대상', '카테고리1', 'KG카테고리2']]\
    .fillna('').agg(' '.join, axis=1)
df['검색_본문'] = df['검색_본문'].str.replace(r'\n|\t', ' ', regex=True)\
    .str.replace(r'\s+', ' ', regex=True).str.strip()

# Streamlit UI
st.title("🎯 KGM 4월 사이버 교육 추천받기")
st.markdown("관심 있는 키워드를 입력하면 관련된 교육과정을 추천해드립니다.")

# CSS 추가하여 버튼 가운데 정렬 
st.markdown("""
    <style>
    div.stButton > button {
        display: block !important;
        margin: 0 auto !important;
        width: 200px !important;
    }
    </style>
    """, unsafe_allow_html=True)

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
    # 교육방식 필터링: 선택된 교육방식에 따라 필터 적용 (키워드 미입력 시에도 해당 조건 적용)
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
        # 대분류별 추천과정을 카드 슬라이더 형식의 HTML로 생성 (가로스크롤이 가능하도록 overflow-x: auto)
        slider_html = """
        <html>
        <head>
          <meta charset="utf-8">
          <style>
             body {
                 font-family: sans-serif;
                 margin: 0;
                 padding: 0;
             }
             h2 {
                 margin-top: 40px;
             }
             .slider-wrapper {
                 position: relative;
                 margin-bottom: 40px;
             }
             .slider-container {
                 display: flex;
                 overflow-x: auto;  /* 수동 가로 스크롤 가능 */
                 scroll-behavior: smooth;
             }
             .card {
                 min-width: 300px;
                 height: 200px;
                 background-color: #ffffff;
                 margin-right: 20px;
                 border-radius: 8px;
                 box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                 padding: 10px;
                 flex-shrink: 0;
             }
             .card h4 {
                 margin: 0;
                 font-size: 18px;
                 overflow: hidden;
                 text-overflow: ellipsis;
                 white-space: nowrap;
             }
             .card p {
                 margin: 5px 0;
                 font-size: 14px;
             }
             .slider-arrow {
                 position: absolute;
                 top: 50%;
                 right: -40px;
                 transform: translateY(-50%);
                 background-color: #007bff;
                 border: none;
                 color: white;
                 width: 30px;
                 height: 30px;
                 border-radius: 50%;
                 cursor: pointer;
             }
          </style>
          <script>
             function slideRight(containerId) {
                 var container = document.getElementById(containerId);
                 var cardWidth = 320; // 카드의 width(300px) + 오른쪽 margin (20px)
                 container.scrollLeft += cardWidth;
             }
          </script>
        </head>
        <body>
        """
        # 각 대분류별로 그룹화하여 슬라이더 구성
        for cat in category_order:
            group = results[results['대분류'] == cat]
            if not group.empty:
                slider_id = f"slider_{''.join(ch for ch in cat if ch.isalnum())}"
                slider_html += f"<h2>{cat}</h2>\n"
                slider_html += f"<div class='slider-wrapper'>\n"
                slider_html += f"<div class='slider-container' id='{slider_id}'>\n"
                for _, row in group.iterrows():
                    card_html = f"""
                    <div class='card'>
                        <h4>{row['과정명']}</h4>
                        <p>정확도: {row.get('정확도점수', 'N/A')}</p>
                        <p>카테고리: {row['카테고리1']} / {row['KG카테고리2']}</p>
                        <p>학습 시간: {row['학습인정시간']}시간</p>
                        <p>수료 기준: {row['수료기준']}</p>
                    </div>
                    """
                    slider_html += card_html
                slider_html += "</div>\n"  # slider-container 종료
                slider_html += f"<button class='slider-arrow' onclick=\"slideRight('{slider_id}')\">&#9654;</button>\n"
                slider_html += "</div>\n"  # slider-wrapper 종료
        slider_html += """
        </body>
        </html>
        """
        components.html(slider_html, height=600)
