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

    /* 카드 스타일: 초록색 계열 + 최소 높이 지정 */
    .card {
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #66bb6a; /* 초록색 외곽선 */
        border-radius: 10px;
        background-color: #e8f5e9; /* 연한 초록 배경색 */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        /* 👇 최소 높이 지정 */
        min-height: 280px; /* 예시 높이: 이미지의 콘텐츠를 포함할 수 있도록 조정 */
        display: flex; /* 내부 요소 정렬을 위해 flexbox 사용 */
        flex-direction: column; /* 내부 요소를 세로로 배치 */
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
    }

    .card-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #2e7d32; /* 진한 초록색 텍스트 */
    }

    .card-content {
        font-size: 0.9rem;
        color: #555;
        margin-bottom: 0.5rem;
    }

    .rating {
        color: #66bb6a;
        font-size: 1.2rem;
        margin-bottom: 0.5rem;
    }

    .category-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin: 1.5rem 0 0.5rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #4CAF50;
        color: #2e7d32;
    }

    details {
        margin-top: auto; /* 상세 정보 expander를 카드 하단으로 밀착 */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ... (이후 코드는 이전과 동일) ...
