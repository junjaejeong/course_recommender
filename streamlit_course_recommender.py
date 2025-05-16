import streamlit as st
import pandas as pd
from kiwipiepy import Kiwi
import re
import streamlit.components.v1 as components

# ✅ Google Analytics(GA4) 삽입 - 높이 조정 및 스크립트 수정
components.html(
    """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-BKJ1BJRKE8"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-BKJ1BJRKE8', {
        'send_page_view': true,
        'debug_mode': true
      });
      console.log('GA4 스크립트가 로드되었습니다.');
    </script>
    """,
    height=100  # 높이 값을 높여서 스크립트가 실행될 수 있도록 함
)

# 추가 GA4 이벤트 트리거 함수
def send_ga_event():
    components.html(
        """
        <script>
        // GA4 이벤트 트리거
        if (typeof gtag === 'function') {
            gtag('event', 'page_view', {
                'page_title': 'KGM 교육 추천',
                'page_location': window.location.href
            });
            console.log('GA4 이벤트가 전송되었습니다.');
        } else {
            console.error('gtag 함수를 찾을 수 없습니다. GA4가 제대로 로드되지 않았습니다.');
        }
        </script>
        """,
        height=0
    )

# 페이지 로드 완료 후 GA4 이벤트 트리거
st.onload(send_ga_event)

# ✅ CSS 스타일 (기존과 동일)
st.markdown(
    """
    <style>
    .block-container {
        max-width: 100% !important;
        padding-left: 10% !important;
        padding-right: 10% !important;
    }

    .card {
        padding: 1rem;
        margin-bottom: 1rem;
        border: 1px solid #66bb6a;
        border-radius: 10px;
        background-color: #e8f5e9;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1), 0 1px 3px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        min-height: 280px;
        display: flex;
        flex-direction: column;
    }

    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 12px rgba(0,0,0,0.15);
    }

    .card-title {
        font-size: 1.1rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #2e7d32;
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
        margin-top: auto;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ✅ 형태소 분석기 초기화
kiwi = Kiwi()

# ✅ 데이터 불러오기 (이하 코드는 동일)
# ... 기존 코드와 동일 ...

# 사용자 상호작용 이벤트 추적 함수
def track_event(event_name, event_params=None):
    if event_params is None:
        event_params = {}
    
    event_params_str = ', '.join([f"'{k}': '{v}'" for k, v in event_params.items()])
    components.html(
        f"""
        <script>
        if (typeof gtag === 'function') {{
            gtag('event', '{event_name}', {{{event_params_str}}});
            console.log('이벤트 전송: {event_name}');
        }}
        </script>
        """,
        height=0
    )

# 검색 버튼 클릭 시 이벤트 추적 예시
if submitted:  # 이 부분은 기존 코드에 추가
    track_event('search_submit', {'keyword': keyword})
