import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="맞춤 교육과정 추천기", layout="wide")

# 사용자 정의 CSS
st.markdown("""
<style>
    div.stButton > button {
        width: 100%;
        border-radius: 5px;
        background-color: #f0f2f6;
        border: 1px solid #e0e0e0;
        padding: 0.5rem;
        text-align: center;
        margin: 0.2rem 0;
        transition: background-color 0.3s, transform 0.2s;
    }
    div.stButton > button:hover {
        background-color: #e0e2e6;
        transform: translateY(-2px);
    }
    div.stButton > button:active {
        background-color: #4e8cff;
        color: white;
    }
    div.stButton > button.selected {
        background-color: #4e8cff;
        color: white;
    }
    .course-title {
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 데이터 불러오기
try:
    df = pd.read_excel("통합_교육과정_데이터셋.xlsx")
    
    # 추천 텍스트 필드 준비
    df['추천_본문'] = df[['학습목표', '학습내용', '학습대상']].fillna('').agg(' '.join, axis=1)
    df['추천_본문'] = df['추천_본문'].str.replace(r'\n|\t', ' ', regex=True).str.replace(r'\s+', ' ', regex=True).str.strip()
except Exception as e:
    st.error(f"데이터 로딩 중 오류가 발생했습니다: {e}")
    st.stop()

# 세션 상태 초기화
if 'selected_categories' not in st.session_state:
    st.session_state.selected_categories = []

# Streamlit UI
st.title("🎯 맞춤 교육과정 추천기")
st.markdown("""
관심 있는 키워드를 입력하고, 원하는 교육방식을 선택하세요.  
예: `AI`, `엑셀`, `디자인`, `영어`, `리더십` 등
""")

# 검색 섹션
col1, col2 = st.columns([3, 1])
with col1:
    keyword = st.text_input("🔑 관심 키워드 입력", "AI")

# 카테고리 선택 섹션
st.markdown("<div style='font-weight: 600; font-size: 16px; margin-top:20px;'>✅ 교육방식 선택</div>", unsafe_allow_html=True)

# 카테고리 토글 함수
def toggle_category(category):
    if category in st.session_state.selected_categories:
        st.session_state.selected_categories.remove(category)
    else:
        st.session_state.selected_categories.append(category)

# 대분류 버튼 UI
categories = df['대분류'].dropna().unique().tolist()
cols = st.columns(len(categories))

for i, category in enumerate(categories):
    # 현재 카테고리가 선택되었는지 확인
    is_selected = category in st.session_state.selected_categories
    button_label = f"{'✓ ' if is_selected else ''}{category}"
    
    # 버튼 생성
    if cols[i].button(button_label, key=f"btn_{category}", 
                    help=f"{category} 교육방식 {'선택 해제' if is_selected else '선택'}"):
        toggle_category(category)
        st.experimental_rerun()

# 필터링 로직
if keyword:
    results = df[df['추천_본문'].str.contains(keyword, case=False, na=False)]
    if st.session_state.selected_categories:
        results = results[results['대분류'].isin(st.session_state.selected_categories)]
    
    st.markdown(f"### 🔎 '{keyword}' 관련 추천 교육과정: {len(results)}건")
    
    if results.empty:
        st.warning("추천 결과가 없습니다. 다른 키워드를 시도해보세요.")
    else:
        # 검색 결과 표시
        for _, row in results.iterrows():
            with st.expander(row['과정명']):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**출처**: {row['출처']}")
                    st.markdown(f"**카테고리**: {row['대분류']} / {row['카테고리1']} / {row['KG카테고리2']}")
                with col2:
                    st.markdown(f"**학습 인정 시간**: {row['학습인정시간']}시간")
                    st.markdown(f"**수료 기준**: {row['수료기준']}")
                
                st.markdown("---")
                
                # 학습 정보 탭
                tab1, tab2, tab3 = st.tabs(["학습 목표", "학습 내용", "학습 대상"])
                with tab1:
                    st.markdown(f"{row['학습목표']}")
                with tab2:
                    st.markdown(f"{row['학습내용']}")
                with tab3:
                    st.markdown(f"{row['학습대상']}")