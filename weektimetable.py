import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# DB 연결
conn = sqlite3.connect('timetable.db')
cur = conn.cursor()

# 1. 날짜 필터: 2025년 3월 셋째 주 (3월 17일 ~ 21일)
start_date = '20250317'
end_date = '20250321'

# 2. 전체 시간표 불러오기
query = f"""
SELECT * FROM timetable
WHERE ALL_TI_YMD BETWEEN '{start_date}' AND '{end_date}'
"""
df = pd.read_sql_query(query, conn)

# 3. 요일 컬럼 추가
df['요일'] = pd.to_datetime(df['ALL_TI_YMD']).dt.dayofweek
df['요일'] = df['요일'].map({
    0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일'
})

# 4. 선택 위젯 구성
학년_목록 = sorted(df['GRADE'].dropna().unique())
반_목록 = sorted(df['CLASS_NM'].dropna().unique())
요일_목록 = ['월요일', '화요일', '수요일', '목요일', '금요일']

선택_학년 = st.selectbox("학년 선택", 학년_목록)
선택_반 = st.selectbox("반 선택", 반_목록)
선택_요일 = st.selectbox("요일 선택", 요일_목록)

# 5. 필터링
filtered_df = df[
    (df['GRADE'] == str(선택_학년)) &
    (df['CLASS_NM'] == str(선택_반)) &
    (df['요일'] == 선택_요일)
]

# 6. 교시 기준 정렬 및 중복 제거
filtered_df = filtered_df.sort_values(by='PERIO')
filtered_df = filtered_df.drop_duplicates(subset=['GRADE', 'CLASS_NM', '요일', 'PERIO'])

# 7. 출력용 컬럼 선택
output_df = filtered_df[['GRADE', 'CLASS_NM', '요일', 'PERIO', 'ITRT_CNTNT']]
output_df.columns = ['학년', '반', '요일', '교시', '수업내용']

# 8. 출력
st.subheader("시간표")
st.dataframe(output_df, use_container_width=True)

# 연결 종료
conn.close()
