import sqlite3
import pandas as pd

# DB 연결
conn = sqlite3.connect('timetable.db')

# 1. 3월 셋째 주 시간표 조회
query = """
SELECT * FROM timetable
WHERE ALL_TI_YMD BETWEEN '20250317' AND '20250321'
"""
df = pd.read_sql_query(query, conn)

# 2. 요일 컬럼 추가 (0=월, ..., 4=금)
df['요일'] = pd.to_datetime(df['ALL_TI_YMD']).dt.dayofweek
df['요일'] = df['요일'].map({
    0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일'
})

# 3. 중복 제거 (학년, 반, 요일, 교시 기준)
dedup_df = df.drop_duplicates(subset=['GRADE', 'CLASS_NM', '요일', 'PERIO'])

# 4. 필요한 컬럼만 추출 및 재정렬
weektable_df = dedup_df[['GRADE', 'CLASS_NM', '요일', 'PERIO', 'ITRT_CNTNT']]
weektable_df.columns = ['GRADE', 'CLASS_NM', 'WEEKDAY', 'PERIO', 'CONTENT']

# 5. 기존 weektable 테이블 삭제 (있을 경우)
conn.execute("DROP TABLE IF EXISTS weektable")

# 6. 새로운 weektable 테이블 생성
create_sql = """
CREATE TABLE weektable (
    GRADE TEXT,
    CLASS_NM TEXT,
    WEEKDAY TEXT,
    PERIO TEXT,
    CONTENT TEXT
)
"""
conn.execute(create_sql)

# 7. 데이터 삽입
weektable_df.to_sql('weektable', conn, if_exists='append', index=False)

# 8. 완료 후 연결 종료
conn.commit()
conn.close()

print("✅ weektable 저장 완료!")
