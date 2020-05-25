"""
create_question_by_place.py

db에 저장된 관광지명과 base질문을 기준으로 관광지별 질문을 db에 입력한다.
tour_place X base_question -> question테이블
"""
import pymysql
from configparser import ConfigParser

# 설정파일 로드(/config.ini)
conf = ConfigParser()
conf.read("./../config.ini")
db_conf = conf["DB"] # 데이터베이스 정보 불러오기

# database 연결 객체
DB_CONN = None


# database 연결
def connect_db():
    global DB_CONN
    DB_CONN = pymysql.connect(host=db_conf["HOST"],
                              port=int(db_conf["PORT"]),
                              user=db_conf["USER"],
                              password=db_conf["PASSWORD"],
                              db=db_conf["DB_NAME"],
                              charset='utf8mb4',
                              use_unicode=True,
                              cursorclass=pymysql.cursors.DictCursor)


# 테이블에 데이터 입력
def insert_question_list(question_list):
    insert_list = []

    for item in question_list:
        insert_list.append(tuple(item.values()))

    with DB_CONN.cursor() as cur:
        sql = "INSERT INTO question({}) VALUES ({})".format(", ".join(question_list[0].keys()), ", ".join(["%s"] * len(question_list[0])))
        result_cnt = cur.executemany(sql, insert_list)

        print(" * sql >> ", sql)
        print(" * data >> \n", insert_list)

    DB_CONN.commit()

    return result_cnt


# 관광지 데이터 조회
def retrieve_tour_place():
    result = None

    with DB_CONN.cursor() as cur:
        sql = "SELECT content_id, org_title, title1, title2 FROM tour_place ORDER BY org_title ASC"
        cur.execute(sql)
        result = cur.fetchall()

    return result


# 기본 질문 데이터 조회
def retrieve_base_question():
    result = None

    with DB_CONN.cursor() as cur:
        sql = "SELECT bq_id, q_text, q_sep_code FROM base_question ORDER BY bq_id ASC"
        cur.execute(sql)
        result = cur.fetchall()

    return result


# 데이터베이스 연결
connect_db()

try:
    place_list = retrieve_tour_place()
    print("[관광지]데이터수 :", len(place_list))
    base_question_list = retrieve_base_question()
    print("[기본질문]데이터수 :", len(base_question_list))

    cnt = 0  # 생성된 질문개수

    for base in base_question_list:
        org_question_text = base["q_text"]

        for place in place_list:
            place_question_list = []

            base_cp = base.copy()
            base_cp["content_id"] = place["content_id"]

            if place["title1"] != "":
                base_cp["title"] = place["title1"]
                base_cp["q_text"] = org_question_text.replace("@", place["title1"])

                place_question_list.append(base_cp)

            if place["title2"] != "":
                base_cp2 = base_cp.copy()
                base_cp2["title"] = place["title2"]
                base_cp2["q_text"] = org_question_text.replace("@", place["title2"])

                place_question_list.append(base_cp2)

            new_cnt = insert_question_list(place_question_list)

            # 신규 입력 건이 있을 경우
            if new_cnt > 0:
                cnt += new_cnt

    print("생성된 질문개수 :", cnt)


finally:
    # 데이터베이스 연결 해제
    DB_CONN.close()
    print("\n\n##### 프로그램 끝 #####")
