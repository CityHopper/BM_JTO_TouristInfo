from configparser import ConfigParser, ExtendedInterpolation
import sys
import pymysql
import pandas as pd
import pymysql.cursors

# config_test.ini 파일 만들기
config = ConfigParser()
config['DB'] = {
    # config_test.ini,
    'HOST': '172.18.32.5',
    'PORT': '3306',
    'USER': 'root',
    'PASSWORD': "1q2w3e4r5t!",
    'DB_NAME': 'jtodb',
    'charset': 'utf8mb4',
    'use_unicode': True,
    'cursorclass': 'pymysql.cursors.DictCursor'
}
with open('./config_test.ini', 'w') as f:
    config.write(f)


# config 파일 사용 테스트
config.read('config_test.ini')
DB_CONN = config['DB']
# print(DB_CONN)
# for key in config['DB']:
#     print(key)
# print(config.sections())


config.read('config_test.ini')
section = "DB"

DB_CONN = pymysql.connect(host=config.get(section, 'host'), user=config.get(section,'user'), port=int(config.get(section,'port')),
                          password=config.get(section,'password'),  # database 접속 비밀번호
                          db=config.get(section,'db_name'),
                          charset=config.get(section,'charset'))
with DB_CONN.cursor() as cursor:
    cursor.execute('SELECT * FROM tamnao_product')
    rows = cursor.fetchall()
    rows = pd.DataFrame(list(rows))
    print(rows)
    DB_CONN.close()