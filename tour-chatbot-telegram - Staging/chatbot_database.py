"""
chatbot_database.py

Database 연결 및 query 실행
"""
import traceback
from configparser import ConfigParser
import pymysql


# 설정파일 로드(/config.ini)
conf = ConfigParser()
conf.read("./config.ini")


# 데이터베이스 연결
def connect():
    db_conf = conf["DB"] # 데이터베이스 정보 불러오기

    conn = pymysql.connect(host=db_conf["HOST"],
                           port=int(db_conf["PORT"]),
                           user=db_conf["USER"],
                           password=db_conf["PASSWORD"],
                           db=db_conf["DB_NAME"],
                           charset='utf8mb4',
                           use_unicode=True,
                           cursorclass=pymysql.cursors.DictCursor)

    return conn


# SQL로 데이터 목록 조회(여러개)
def retrieve_list(sql):
    result = None
    conn = connect()

    print("******************************** DB Connect(retrieve_list) ********************************")
    try:
        with conn.cursor() as cur:
            print(sql)
            cur.execute(sql)
            result = cur.fetchall()

    finally:
        conn.close()
        print("******************************** DB Close(retrieve_list) ********************************")

    return result


# SQL로 데이터 단건 조회
def retrieve_one(sql):
    result = None
    conn = connect()

    print("******************************** DB Connect(retrieve_one) ********************************")
    try:
        with conn.cursor() as cur:
            print(sql)
            cur.execute(sql)
            result = cur.fetchone()

    finally:
        conn.close()
        print("******************************** DB Close(retrieve_one) ********************************")

    return result


# 챗봇으로 대화한 기록 저장
def insert_chat_log(chat):
    conn = connect()

    print("******************************** DB Connect(insert_chat_log) ********************************")
    try:
        with conn.cursor() as cur:
            insert_sql = "INSERT INTO tour_chat({}) VALUES ({})".format(",".join(chat.keys()), ",".join(["%s"] * len(chat)))
            print(insert_sql)
            cur.execute(insert_sql, tuple(chat.values()))
            print(tuple(chat.values()))

            conn.commit()

    finally:
        conn.close()
        print("******************************** DB Close(insert_chat_log) ********************************")


# 모델 훈련을 위한 db에 저장된 모든 질문과 답변 조회 쿼리 실행
def retrieve_all_question_list():
    sql = "SELECT q.q_text AS Q, concat(q.q_sep_code, ' ', q.title) AS A FROM question q"
    return retrieve_list(sql)


# keyword(code, 질문의 키워드)에 해당하는 연관된 컬럼(rel_col)들을 가져오고, 관광지명(place_name)에 해당하는 컬럼(rel_col)의 데이터 조회
def retrieve_place_info(q_place_name, q_keyword):
    # 질문 키워드와 관련된 컬럼명 조회
    sql_rel_cols = "SELECT sc.rel_col AS cols FROM question_sep_code sc WHERE sc.code = '{keyword}'".format(keyword = q_keyword)
    rel_cols = retrieve_one(sql_rel_cols)
    
    # 질문 키워드에 해당하는 관광지 정보 조회
    sql_info = "SELECT {cols} " \
               "  FROM tour_place " \
               " WHERE org_title LIKE REPLACE('%{place_name}%', ' ', '') " \
               "    OR title1 LIKE REPLACE('%{place_name}%', ' ', '') " \
               "    OR title2 LIKE REPLACE('%{place_name}%', ' ', '')".format(cols = rel_cols["cols"], place_name = q_place_name)

    result_info = retrieve_one(sql_info)

    # 데이터 중 None -> ""(null) 변환(나중에 string으로 사용하게 되므로 미리 변환한다.)
    result_info = dict(map(lambda item: (item[0], "") if item[1] is None else item, result_info.items()))

    return result_info


# IN/OUT별 관광지 조회
def retrieve_attraction_by_inout(inout_code):
    sql = "SELECT t1.org_title AS title, CONCAT(t1.full_address, ' ',t1.detail_address) AS full_address, t2.category3_name AS category " \
          "FROM tour_place t1 JOIN tour_code t2 ON t1.category3_code = t2.category3_code " \
          "WHERE t1.inout IN ('{inout_code}','C') " \
          "ORDER BY RAND() " \
          "LIMIT 5".format(inout_code = inout_code)

    return retrieve_list(sql)