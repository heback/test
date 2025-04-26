import streamlit as st
import sqlite3
from datetime import datetime

# 데이터베이스 연결 함수
def get_connection():
    return sqlite3.connect('timetable.db')

# weektable에서 학년과 학급 목록 가져오기
def get_grade_class_options():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT grade, class_nm FROM weektable ORDER BY grade, class_nm")
    rows = cursor.fetchall()
    conn.close()
    return rows

# Streamlit 화면 구현
st.title('시간표 변경 등록')

# 학년, 학급 선택
grade_class_options = get_grade_class_options()
selected_option = st.selectbox('학년과 학급 선택', grade_class_options, format_func=lambda x: f"{x[0]}학년 {x[1]}반")

if selected_option:
    grade, class_ = selected_option

    # 과목 입력
    subject = st.text_input('과목명')

    # 변경 전 일자 및 교시 입력
    old_date = st.date_input('변경 전 일자', format="YYYY-MM-DD")
    old_period = st.number_input('변경 전 교시', min_value=1, max_value=10, step=1)

    # 변경 후 일자 및 교시 입력
    new_date = st.date_input('변경 후 일자', format="YYYY-MM-DD")
    new_period = st.number_input('변경 후 교시', min_value=1, max_value=10, step=1)

    # 선생님 입력
    teacher = st.text_input('선생님')

    # 장소 입력
    location = st.text_input('장소')

    # 등록 버튼
    if st.button('변경 등록'):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO timetable_history 
            (grade, class, subject, old_date, old_period, new_date, new_period, teacher, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (grade, class_, subject, old_date.strftime('%Y-%m-%d'), old_period, new_date.strftime('%Y-%m-%d'), new_period, teacher, location))
        conn.commit()
        conn.close()
        st.success('변경 내역이 성공적으로 등록되었습니다.')
