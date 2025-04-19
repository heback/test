import sqlite3
import json

# 1. JSON 파일에서 데이터 읽기
with open('timetable_full.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2. SQLite 연결 및 커서 생성
conn = sqlite3.connect('timetable.db')
cur = conn.cursor()

# 3. timetable 테이블 생성 (JSON 키 기준)
create_table_sql = '''
CREATE TABLE IF NOT EXISTS timetable (
    ATPT_OFCDC_SC_CODE TEXT,
    ATPT_OFCDC_SC_NM TEXT,
    SD_SCHUL_CODE TEXT,
    SCHUL_NM TEXT,
    AY TEXT,
    SEM TEXT,
    ALL_TI_YMD TEXT,
    DGHT_CRSE_SC_NM TEXT,
    GRADE TEXT,
    CLASS_NM TEXT,
    PERIO TEXT,
    ITRT_CNTNT TEXT,
    LOAD_DTM TEXT
)
'''
cur.execute(create_table_sql)

# 4. row 데이터가 있는 경우에만 INSERT 수행
for item in data:
    if "row" in item.get("data", {}):
        for row in item["data"]["row"]:
            columns = ', '.join(row.keys())
            placeholders = ', '.join(['?'] * len(row))
            values = list(row.values())
            insert_sql = f'INSERT INTO timetable ({columns}) VALUES ({placeholders})'
            cur.execute(insert_sql, values)

# 5. 변경사항 저장 및 종료
conn.commit()
conn.close()
