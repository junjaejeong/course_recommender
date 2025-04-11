import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
# 형태소 분석기 초기화
kiwi = Kiwi()
# 데이터 불러오기
df = pd.read_excel("통합_교육과정_데이터셋.xlsx")
# 검색 대상 필드 확장
df['검색_본문'] = df[['과정명', '학습목표', '학습내용', '학습대상', '카테고리1', 'KG카테고리2']].fillna('').agg(' '.join, axis=1)
df['검색_본문'] = df['검색_본문'].str.replace(r'\n|\t', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip()
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
    if keyword:
        morphs = [token.form for token in kiwi.tokenize(keyword) if len(token.form) > 1]
        keywords = set([keyword] + morphs)
        def compute_score(text):
            return sum(text.lower().count(k.lower()) for k in keywords)
        results['정확도점수'] = results['검색_본문'].apply(compute_score)
        results = results[results['정확도점수'] > 0]
    if selected_categories:
        results = results[results['대분류'].isin(selected_categories)]
    # 정렬
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
        st.markdown( category_count_display)
        current_category = None
        for _, row in results.iterrows():
            if current_category != row['대분류']:
                if current_category is not None:
                    st.markdown("---")
                current_category = row['대분류']
                st.markdown(f"## 📚 {current_category}")
                st.markdown("---")
            with st.container():
                st.markdown(f"##### 📘 {row['과정명']} (정확도: {row['정확도점수']}점)")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"🏷️ **카테고리**: {row['카테고리1']} / {row['KG카테고리2']}")
                with col2:
                    st.markdown(f"⏱️ **학습 시간**: {row['학습인정시간']}시간")
                st.markdown(f"🎯 **수료 기준**: {row['수료기준']}")
                with st.expander("📖 상세 보기"):
                    st.markdown("🎓 **학습 목표**")
                    st.markdown(row['학습목표'])
                    st.markdown("📘 **학습 내용**")
                    st.markdown(row['학습내용'])
                    st.markdown("🧍 **학습 대상**")
                    st.markdown(row['학습대상'])
                st.markdown("---")
