import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pyrebase
import datetime

# Firebase 설정
firebaseConfig = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.firebasestorage.app",
    "messagingSenderId": "812186368395",
    "appId": "1:812186368395:web:be2f7291ce54396209d78e"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()

# 세션 상태 초기화
if "user" not in st.session_state:
    st.session_state["user"] = None
if "idToken" not in st.session_state:
    st.session_state["idToken"] = None

# localStorage에서 토큰 불러오기 (앱 시작 시 1회 실행)
if st.session_state["idToken"] is None:
    id_token = streamlit_js_eval(js_expressions="localStorage.getItem('idToken')", key="load_token")
    if id_token and isinstance(id_token, str):
        try:
            user_info = auth.get_account_info(id_token)
            st.session_state["user"] = user_info["users"][0]
            st.session_state["idToken"] = id_token
            st.success(f"{st.session_state['user']['email']}님 자동 로그인되었습니다.")
        except:
            st.warning("저장된 로그인 정보가 만료되었습니다. 다시 로그인해주세요.")

# 로그인 처리
def login(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state["idToken"] = user["idToken"]
        st.session_state["user"] = auth.get_account_info(user["idToken"])["users"][0]
        # 브라우저 localStorage에 저장
        streamlit_js_eval(js_expressions=f"localStorage.setItem('idToken', '{user['idToken']}')", key="save_token")
        st.success("로그인 성공!")
    except Exception as e:
        st.error(f"로그인 실패: {e}")

# 로그아웃 처리
def logout():
    streamlit_js_eval(js_expressions="localStorage.removeItem('idToken')", key="clear_token")
    for key in ["user", "idToken"]:
        st.session_state[key] = None
    st.success("로그아웃 완료")

# 회원가입 처리
def signup(email, password):
    try:
        auth.create_user_with_email_and_password(email, password)
        st.success("회원가입 성공! 로그인 해주세요.")
    except Exception as e:
        st.error(f"회원가입 실패: {e}")

# 비밀번호 재설정
def reset_password(email):
    try:
        auth.send_password_reset_email(email)
        st.success("비밀번호 재설정 이메일을 보냈습니다.")
    except Exception as e:
        st.error(f"비밀번호 재설정 실패: {e}")

# UI
st.title("🔐 Firebase 로그인 시스템 (localStorage 적용)")

menu = st.radio("메뉴", ["로그인", "회원가입", "비밀번호 재설정", "내 정보"])

if st.session_state["user"]:
    st.success(f"{st.session_state['user']['email']}님 로그인 중입니다.")
    if st.button("로그아웃"):
        logout()

elif menu == "로그인":
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
    email = st.text_input("이메일")
    if st.button("비밀번호 재설정 메일 보내기"):
        reset_password(email)

elif menu == "내 정보":
    st.subheader("내 정보")
    if st.session_state["user"]:
        st.write("이메일:", st.session_state["user"].get("email"))
        st.write("UID:", st.session_state["user"].get("localId"))
    else:
        st.warning("로그인이 필요합니다.")
