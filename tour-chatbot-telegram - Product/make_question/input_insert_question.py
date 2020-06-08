"""
input_insert_question.py

질문 입력 프로그램(base)
- 질문을 입력하면 base_question테이블에 입력된다.
- 예) @는 어디인가요?/ad (@:관광지명, /:질문text-질문구분코드 구분자, 영문2자:질문구분코드)
- 여기서 만들어진 질문이 관광지 데이터와 합쳐져서 관광지별 질문을 생성할 것이다.
"""
import pymysql
import pandas as pd
from pyautogui import typewrite
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


# 질문 구분코드 데이터 조회
def retrieve_question_sep_code():
    cur = DB_CONN.cursor()
    sql = "SELECT code, code_name FROM question_sep_code ORDER BY code_name ASC"

    cur.execute(sql)

    return cur.fetchall()


# base 질문 데이터 중복 조회
def retrieve_dup_question(q_txt):
    cur = DB_CONN.cursor()
    sql = "SELECT count(*) AS cnt FROM base_question WHERE REPLACE(q_text, ' ', '') = REPLACE('" + q_txt + "', ' ', '')"

    cur.execute(sql)

    return True if cur.fetchone()["cnt"] > 0 else False


# base 질문 테이블에 데이터 입력
def insert_question_data(xml_data):
    cur = DB_CONN.cursor()
    sql = "INSERT INTO base_question({}) VALUES ({})".format(",".join(xml_data.keys()),
                                                             ", ".join(["%s"] * len(xml_data)))
    result = 0
    try:
        cur.execute(sql, tuple(xml_data.values()))
        DB_CONN.commit()

        print("입력 성공 data >> ", tuple(xml_data.values()))
        result = 1

    except:
        print("아마 코드값이 잘못입력된거 같아여. 다시 입력해주세여.", end="\n\n")

    return result


# 데이터베이스 연결
connect_db()

try:
    code_data = retrieve_question_sep_code()

    # 질문 구분코드표 출력
    code_df = pd.DataFrame(code_data)
    print(code_df, end="\n\n")

    # 코드 list
    code_list = []
    for item in code_data:
        code_list.append(item["code"])

    cnt = 0  # 입력한 질문개수
    before_question_txt = ""

    while True:
        #input_question = input("(종료:Q(q)) >> ", )
        print("종료:Q(q) >> ")
        typewrite(before_question_txt)
        input_question = input()
        print()

        if input_question.upper() == "Q":
            break

        if "@" not in input_question:
            print("@를 포함해서 입력하세여")
            before_question_txt = input_question
            continue

        if "/" not in input_question:
            print("/를 포함해서 질문구분코드값을 입력하세여")
            before_question_txt = input_question
            continue

        question_data = input_question.split("/")
        question_txt = question_data[0]
        question_sep_code = question_data[1]

        if question_txt == "" or question_sep_code == "":
            print("질문(@포함)이나 질문구분코드값(영문2자)을 입력안했어여. 다시 입력해주세여~")
            before_question_txt = input_question
            continue

        if question_sep_code.upper() not in code_list:
            print("질문구분코드값이 존재하지않아여. 표를 보고 다시 입력해주세여~")
            before_question_txt = input_question
            print(code_df, end="\n\n")
            continue

        if retrieve_dup_question(question_txt):
            print("중복된 질문이 있어여. 다른 질문 입력해주세여!")
            before_question_txt = question_txt
            continue

        in_data = {"q_text": question_txt, "q_sep_code": question_sep_code.upper()}  # insert 할 데이터
        new_insert_cnt = insert_question_data(in_data)  # 질문 insert

        # 신규 입력 건이 존재할 경우
        if new_insert_cnt > 0:
            cnt += new_insert_cnt
            before_question_txt = ""

    print("신규 입력한 질문개수 :", cnt)

finally:
    # 데이터베이스 연결 해제
    DB_CONN.close()
    print("\n\n##### 프로그램 끝 #####")
