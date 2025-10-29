import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph.graph import MessagesState
import datetime

# travel-agent 모듈에서 graph 가져오기
from travel_agent import graph

# 페이지 설정
st.set_page_config(
    page_title="AI 여행 플래너",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"  # 사이드바 기본으로 열림
)

# 세션 상태 초기화
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# 메인 UI
st.title("✈️ AI 여행 플래너")
st.markdown("---")

# 사이드바
with st.sidebar:

    # 예시 표시
    with st.expander("💡 사용 예시"):
        st.markdown("""
        ### 이렇게 사용해보세요:

        1. **여행 목적지**: 제주도
        2. **출발일**: 2024년 12월 22일
        3. **도착일**: 2024년 12월 24일
        4. **선호사항**: 자연 경관과 맛집 위주

        AI가 자동으로:
        - 관련 여행 정보를 검색하고
        - 맞춤형 일정을 작성해드립니다!
        """)
        
    st.header("📋 여행 정보 입력")

    # 여행지 입력
    destination = st.text_input("여행 목적지", placeholder="예: 제주도, 파리, 도쿄")

    # 날짜 선택
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "출발일",
            value=datetime.date.today(),
            min_value=datetime.date.today()
        )
    with col2:
        end_date = st.date_input(
            "도착일",
            value=datetime.date.today() + datetime.timedelta(days=2),
            min_value=datetime.date.today()
        )

    # 여행 일수 계산
    if end_date >= start_date:
        travel_days = (end_date - start_date).days + 1
        st.info(f"총 {travel_days}일 여행")
    else:
        st.error("도착일은 출발일 이후여야 합니다.")

    # 추가 정보 (선택사항)
    st.markdown("### 추가 정보 (선택)")
    preferences = st.text_area(
        "여행 선호사항",
        placeholder="예: 자연 경관, 맛집 투어, 역사 문화, 휴양 등",
        height=100
    )

    # 일정 생성 버튼
    generate_btn = st.button("🗓️ 여행 일정 생성", type="primary", use_container_width=True)

    st.markdown("---")

    # 초기화 버튼
    if st.button("🔄 새로운 여행 계획", use_container_width=True):
        st.session_state.chat_history = []
        st.rerun()

# 메인 컨텐츠 영역
if generate_btn:
    if not destination:
        st.error("여행 목적지를 입력해주세요.")
    elif end_date < start_date:
        st.error("도착일은 출발일 이후여야 합니다.")
    else:
        # 사용자 쿼리 생성
        user_query = f"나는 {start_date.strftime('%Y년 %m월 %d일')}부터 {end_date.strftime('%Y년 %m월 %d일')}까지 {destination} 여행을 가려고 해"
        if preferences:
            user_query += f". 여행 선호사항: {preferences}"
        user_query += ". 이에 맞게 여행 일정을 작성해주세요."

        # 채팅 히스토리에 추가
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query
        })

        # 에이전트 실행
        try:
            # 진행 상황 표시
            progress_placeholder = st.empty()
            progress_placeholder.info("🚀 여행 계획을 시작합니다...")

            # 초기 상태 생성
            initial_state = MessagesState(messages=[HumanMessage(content=user_query)])

            # 스트리밍 실행
            messages = []
            for i, chunk in enumerate(graph.stream(initial_state, stream_mode="values")):
                messages = chunk['messages']
                last_msg = messages[-1]

                # 진행 상황 업데이트
                if hasattr(last_msg, 'name'):
                    if last_msg.name == 'research_agent_node':
                        progress_placeholder.info("🔍 여행지 정보를 조사 중입니다...")
                    elif last_msg.name == 'planner_agent_node':
                        progress_placeholder.info("📝 여행 일정을 작성 중입니다...")

            # 최종 결과 추출
            final_result = messages[-1].content

            # 채팅 히스토리에 추가
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": final_result
            })

            progress_placeholder.success("✅ 여행 일정이 완성되었습니다!")

        except Exception as e:
            st.error(f"오류가 발생했습니다: {str(e)}")

# 채팅 히스토리 표시
if st.session_state.chat_history:
    st.markdown("## 💬 여행 계획")

    for message in st.session_state.chat_history:
        if message["role"] == "user":
            with st.chat_message("user", avatar="🧳"):
                st.markdown(message["content"])
        else:
            with st.chat_message("assistant", avatar="✈️"):
                st.markdown(message["content"])
else:
    # 빈 상태 메시지
    st.info("👈 왼쪽 사이드바에서 여행 정보를 입력하고 '여행 일정 생성' 버튼을 클릭해주세요!")


# 푸터
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Made by <a href='https://github.com/gimseonjin' target='_blank' style='color: gray; text-decoration: none;'>Kerry Kim</a></div>",
    unsafe_allow_html=True
)
