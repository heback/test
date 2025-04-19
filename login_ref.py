import streamlit as st
import pyrebase
from streamlit_js_storage import StreamlitStorage
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from urllib.parse import urlencode

# --- Firebase 설정
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

# Firestore 연결
if not firebase_admin._apps:
    cred = credentials.Certificate("YOUR_SERVICE_ACCOUNT_KEY.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

# --- LocalStorage 연결
storage = StreamlitStorage()

# --- 관리자 이메일 리스트
ADMIN_EMAILS = ["admin1@example.com", "admin2@example.com"]

# --- 세션 초기화
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'idToken' not in st.session_state:
    st.session_state['idToken'] = None
if 'refreshToken' not in st.session_state:
    st.session_state['refreshToken'] = None
if 'token_expiry' not in st.session_state:
    st.session_state['token_expiry'] = None
if 'is_admin' not in st.session_state:
    st.session_state['is_admin'] = False

# --- URL 쿼리로 페이지 관리
def set_page(page_name):
    st.experimental_set_query_params(page=page_name)

def get_page():
    params = st.experimental_get_query_params()
    return params.get("page", ["home"])[0]

# --- Firebase 세션 관리
def load_token_from_storage():
    idToken = storage.get("idToken")
    refreshToken = storage.get("refreshToken")
    token_expiry = storage.get("token_expiry")

    if idToken and refreshToken and token_expiry:
        st.session_state['idToken'] = idToken
        st.session_state['refreshToken'] = refreshToken
        st.session_state['token_expiry'] = datetime.datetime.fromisoformat(token_expiry)
        try:
            user_info = auth.get_account_info(idToken)
            st.session_state['user'] = user_info['users'][0]
            check_admin()
        except:
            logout()

def maintain_session():
    if st.session_state['refreshToken'] and st.session_state['token_expiry']:
        now = datetime.datetime.now()
        if now >= st.session_state['token_expiry']:
            try:
                user = auth.refresh(st.session_state['refreshToken'])
                st.session_state['idToken'] = user['idToken']
                st.session_state['refreshToken'] = user['refreshToken']
                st.session_state['token_expiry'] = now + datetime.timedelta(seconds=int(user['expiresIn']) - 60)
                st.session_state['user'] = auth.get_account_info(st.session_state['idToken'])['users'][0]
                check_admin()

                storage.set("idToken", st.session_state['idToken'])
                storage.set("refreshToken", st.session_state['refreshToken'])
                storage.set("token_expiry", st.session_state['token_expiry'].isoformat())

            except:
                logout()

def check_admin():
    user_email = st.session_state['user'].get('email')
    st.session_state['is_admin'] = user_email in ADMIN_EMAILS

def logout():
    for key in ['user', 'idToken', 'refreshToken', 'token_expiry', 'is_admin']:
        st.session_state[key] = None
    storage.delete("idToken")
    storage.delete("refreshToken")
    storage.delete("token_expiry")

# --- Firestore 공지사항 저장/읽기
def write_notice(title, content, writer_email):
    db.collection("notices").add({
        "title": title,
        "content": content,
        "writer": writer_email,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

def load_notices():
    notices_ref = db.collection("notices").order_by("timestamp", direction=firestore.Query.DESCENDING)
    docs = notices_ref.stream()
    return [doc.to_dict() for doc in docs]

# --- 기본 레이아웃
def menu():
    st.sidebar.title("Navigation")
    st.sidebar.button("🏠 홈", on_click=lambda: set_page("home"))
    if st.session_state['user'] is None:
        st.sidebar.button("🔑 로그인", on_click=lambda: set_page("login"))
        st.sidebar.button("🆕 회원가입", on_click=lambda: set_page("signup"))
        st.sidebar.button("🔑 비밀번호 재설정", on_click=lambda: set_page("reset"))
    else:
        st.sidebar.button("📢 공지사항", on_click=lambda: set_page("notice"))
        if st.session_state['is_admin']:
            st.sidebar.button("👑 관리자 페이지", on_click=lambda: set_page("admin"))
        st.sidebar.button("🚪 로그아웃", on_click=logout)

# --- 페이지별 화면
def page_home():
    st.title("🏠 홈")
    if st.session_state['user']:
        st.success(f"{st.session_state['user'].get('email')}님, 환영합니다!")

def page_login():
    st.title("🔑 로그인")
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.session_state['idToken'] = user['idToken']
            st.session_state['refreshToken'] = user['refreshToken']
            st.session_state['token_expiry'] = datetime.datetime.now() + datetime.timedelta(seconds=int(user['expiresIn']) - 60)
            st.session_state['user'] = auth.get_account_info(st.session_state['idToken'])['users'][0]
            check_admin()
            storage.set("idToken", st.session_state['idToken'])
            storage.set("refreshToken", st.session_state['refreshToken'])
            storage.set("token_expiry", st.session_state['token_expiry'].isoformat())
            st.success("로그인 성공!")
            set_page("home")
        except Exception as e:
            st.error(f"로그인 실패: {e}")

def page_signup():
    st.title("🆕 회원가입")
    email = st.text_input("회원가입 이메일")
    password = st.text_input("회원가입 비밀번호", type="password")
    if st.button("회원가입"):
        try:
            auth.create_user_with_email_and_password(email, password)
            st.success("회원가입 성공! 로그인 해주세요.")
            set_page("login")
        except Exception as e:
            st.error(f"회원가입 실패: {e}")

def page_reset():
    st.title("🔑 비밀번호 재설정")
    email = st.text_input("비밀번호 재설정 이메일")
    if st.button("비밀번호 재설정 이메일 보내기"):
        try:
            auth.send_password_reset_email(email)
            st.success("비밀번호 재설정 이메일을 보냈습니다.")
        except Exception as e:
            st.error(f"비밀번호 재설정 실패: {e}")

def page_notice():
    st.title("📢 공지사항")
    notices = load_notices()
    if notices:
        for notice in notices:
            st.subheader(notice.get('title', '제목 없음'))
            st.write(notice.get('content', '내용 없음'))
            st.caption(f"작성자: {notice.get('writer', '미상')}")
            st.divider()
    else:
        st.info("등록된 공지사항이 없습니다.")

def page_admin():
    if st.session_state['is_admin']:
        st.title("👑 관리자 페이지")
        st.write("공지사항 작성")
        title = st.text_input("공지 제목")
        content = st.text_area("공지 내용")
        if st.button("공지사항 등록"):
            if title and content:
                write_notice(title, content, st.session_state['user']['email'])
                st.success("공지사항 작성 완료!")
    else:
        st.error("관리자 권한이 없습니다.")

# --- 메인
def main():
    load_token_from_storage()
    maintain_session()
    menu()

    page = get_page()

    if page == "home":
        page_home()
    elif page == "login":
        page_login()
    elif page == "signup":
        page_signup()
    elif page == "reset":
        page_reset()
    elif page == "notice":
        page_notice()
    elif page == "admin":
        page_admin()

if __name__ == "__main__":
    main()
