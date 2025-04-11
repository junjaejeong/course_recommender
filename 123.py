import streamlit as st
import pandas as pd

# 데이터 불러오기
df = pd.read_excel("통합_교육과정_데이터셋.xlsx")

# 추천 텍스트 필드 준비: 학습목표, 학습내용, 학습대상 결합 및 공백/개행문자 정리
df['추천_본문'] = df[['학습목표', '학습내용', '학습대상']].fillna('').agg(' '.join, axis=1)
df['추천_본문'] = (
    df['추천_본문']
    .str.replace(r'\n|\t', ' ', regex=True)
    .str.replace(r'\s+', ' ', regex=True)
    .str.strip()
)

# Streamlit UI 구성
st.title("🎯 KGM 4월 사이버 교육 추천받기")

# 키워드 입력창에 플레이스홀더 적용 (사용자가 입력시 사라지고, 빈 상태면 표시됨)
keyword = st.text_input("🔑 관심 키워드 입력", placeholder="예: AI, 엑셀, 디자인, 영어, 리더십 등")

# "교육방식 선택" 제목 추가 (아이콘 포함)
st.markdown("<div style='font-weight: 600; font-size: 16px; margin-top:20px;'>✅ 교육방식 선택</div>", unsafe_allow_html=True)

# 대분류 체크박스 UI (원본 데이터프레임 순서 유지)
categories = df['대분류'].dropna().unique().tolist()
selected_categories = []
cols = st.columns(len(categories))
for i, category in enumerate(categories):
    if cols[i].checkbox(category, key=f"checkbox_{category}"):
        selected_categories.append(category)

# 키워드가 입력된 경우에만 필터링 수행
if keyword:
    # 키워드를 포함한 행 필터링 (대소문자 구분 없이 검색)
    results = df[df['추천_본문'].str.contains(keyword, case=False, na=False)]
    
    # 만약 사용자가 대분류를 선택한 경우 추가 필터링
    if selected_categories:
        results = results[results['대분류'].isin(selected_categories)]
    
    # 전체 결과 건수 출력
    total_count = len(results)
    st.markdown(f"### 🔎 '{keyword}' 관련 추천 교육과정: {total_count}건")
    
    # 대분류별 결과 건수 산출 (출력 순서는 원본 데이터프레임에 나타난 순서를 따름)
    category_counts = {}
    for cat in categories:
        cnt = results[results['대분류'] == cat].shape[0]
        if cnt > 0:
            category_counts[cat] = cnt

    # 인라인 형식으로 "대분류 : 건수" 텍스트 출력 (예: 직무(무료) : oo건, 직무(유료) : oo건)
    if category_counts:
        cat_text = ", ".join([f"{cat} : {cnt}건" for cat, cnt in category_counts.items()])
        st.markdown(cat_text)
    
    # 결과가 없으면 경고 메시지 표시
    if results.empty:
        st.warning("입력하신 키워드에 적합한 과정이 없습니다. 다른 키워드를 시도해보세요.")
    else:
        # 대분류별로 그룹화하여 출력 (원본 순서대로)
        for cat in categories:
            group = results[results['대분류'] == cat]
            if not group.empty:
                # 초록색 섹션 제목 및 구분선 적용 (기본 초록색)
                st.markdown(f"<h2 style='color: green; border-bottom: 2px solid green;'>{cat}</h2>", unsafe_allow_html=True)
                # 각 추천 과정 상세 정보 출력
                for _, row in group.iterrows():
                    with st.expander(row['과정명']):
                        st.markdown(f"**출처**: {row['출처']}")
                        st.markdown(f"**카테고리**: {row['대분류']} / {row['카테고리1']} / {row['KG카테고리2']}")
                        st.markdown(f"**학습 인정 시간**: {row['학습인정시간']}시간")
                        st.markdown(f"**수료 기준**: {row['수료기준']}")
                        st.markdown("---")
                        st.markdown(f"**학습 목표**\n\n{row['학습목표']}")
                        st.markdown(f"**학습 내용**\n\n{row['학습내용']}")
                        st.markdown(f"**학습 대상**\n\n{row['학습대상']}")
