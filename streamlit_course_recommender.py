import streamlit as st
import pandas as pd

# 데이터 불러오기
df = pd.read_excel("통합_교육과정_데이터셋.xlsx")

# 추천 텍스트 필드 준비
df['추천_본문'] = df[['학습목표', '학습내용', '학습대상']].fillna('').agg(' '.join, axis=1)
df['추천_본문'] = df['추천_본문'].str.replace(r'\n|\t', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip()

# Streamlit UI
st.title("🎯 KGM 4월 사이버 교육 추천받기")
st.markdown("""
관심 있는 키워드를 입력하고, 원하는 교육방식을 선택하세요.
""")

# 플레이스홀더가 있는 텍스트 입력 필드
keyword = st.text_input("🔑 관심 키워드 입력", placeholder="예: AI, 엑셀, 디자인, 영어, 리더십 등")

# "교육방식 선택" 제목 추가 (아이콘 포함)
st.markdown("<div style='font-weight: 600; font-size: 16px; margin-top:20px;'>✅ 교육방식 선택</div>", unsafe_allow_html=True)

# 대분류 체크박스 UI
categories = df['대분류'].dropna().unique().tolist()
selected_categories = []

# st.columns를 사용하여 각 항목을 동일한 너비로 배치
cols = st.columns(len(categories))
for i, category in enumerate(categories):
    if cols[i].checkbox(category, key=f"checkbox_{category}"):
        selected_categories.append(category)

# 필터링 로직
results = df.copy()  # 기본값으로 모든 결과 설정

if keyword:
    results = results[results['추천_본문'].str.contains(keyword, case=False, na=False)]

if selected_categories:
    results = results[results['대분류'].isin(selected_categories)]

# 결과 표시
if keyword or selected_categories:
    st.markdown(f"### 🔎 '{keyword if keyword else '모든'}' 관련 추천 교육과정: {len(results)}건")
    
    if results.empty:
        st.warning("입력하신 키워드에 적합한 과정이 없습니다. 다른 키워드를 시도해보세요.")
    else:
        # 대분류별 결과 건수 계산
        category_counts = results['대분류'].value_counts().to_dict()
        
        # 대분류별 결과 건수 표시
        category_count_display = ", ".join([f"{cat}: {count}건" for cat, count in category_counts.items()])
        st.markdown(f"**대분류별 결과**: {category_count_display}")
        
        # 대분류별로 정렬
        results = results.sort_values(by='대분류')
        
        # 대분류별로 그룹화하여 표시
        current_category = None
        
        for _, row in results.iterrows():
            # 대분류가 바뀌면 헤더 추가
            if current_category != row['대분류']:
                if current_category is not None:  # 첫 번째가 아닌 경우 구분선 추가
                    st.markdown("---")
                
                current_category = row['대분류']
                st.markdown(f"## 📚 {current_category}")
                st.markdown("---")
            
            # 교육과정 정보 표시
            with st.expander(row['과정명']):
                st.markdown(f"**출처**: {row['출처']}")
                st.markdown(f"**카테고리**: {row['대분류']} / {row['카테고리1']} / {row['KG카테고리2']}")
                st.markdown(f"**학습 인정 시간**: {row['학습인정시간']}시간")
                st.markdown(f"**수료 기준**: {row['수료기준']}")
                st.markdown("---")
                st.markdown(f"**학습 목표**\n\n{row['학습목표']}")
                st.markdown(f"**학습 내용**\n\n{row['학습내용']}")
                st.markdown(f"**학습 대상**\n\n{row['학습대상']}")
