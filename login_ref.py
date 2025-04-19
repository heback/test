import streamlit as st
import pyrebase



# Firebase 설정
firebaseConfig = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
    "databaseURL": "https://YOUR_PROJECT_ID.firebaseio.com",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT_ID.appspot.com",
    "messagingSenderId": "YOUR_SENDER_ID",
    "appId": "YOUR_APP_ID"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# 세션 상태 초기화
if 'user' not in st.session_state:
    st.session_state['user'] = None

st.title("Streamlit + Firebase 로그인 시스템")

# 회원가입 함수
def signup(email, password):
    try:
        user = auth.create_user_with_email_and_password(email, password)
        st.success("회원가입 성공! 로그인 해주세요.")
    except Exception as e:
        st.error(f"회원가입 실패: {e}")

# 로그인 함수
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state['user'] = user
        st.success("로그인 성공!")
    except Exception as e:
        st.error(f"로그인 실패: {e}")

# 비밀번호 재설정
def reset_password(email):
    try:
        auth.send_password_reset_email(email)
        st.success("비밀번호 재설정 이메일을 보냈습니다.")
    except Exception as e:
        st.error(f"비밀번호 재설정 실패: {e}")

# 로그아웃
def logout():
    st.session_state['user'] = None
    st.success("로그아웃 완료.")

# 회원가입, 로그인, 비밀번호 재설정 폼
menu = st.sidebar.selectbox("메뉴", ["로그인", "회원가입", "비밀번호 재설정"])

if st.session_state['user']:  # 로그인된 경우
    st.subheader("현재 로그인된 사용자 정보")
    st.write(f"이메일: {st.session_state['user']['email']}")
    if st.button("로그아웃"):
        logout()

else:  # 로그인 안 된 경우
    if menu == "로그인":
        st.subheader("로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            login(email, password)

    elif menu == "회원가입":
        st.subheader("회원가입")
        email = st.text_input("회원가입 이메일")
        password = st.text_input("회원가입 비밀번호", type="password")
        if st.button("회원가입"):
            signup(email, password)

    elif menu == "비밀번호 재설정":
        st.subheader("비밀번호 재설정")
        email = st.text_input("비밀번호 재설정 이메일")
        if st.button("비밀번호 재설정 이메일 보내기"):
            reset_password(email)
