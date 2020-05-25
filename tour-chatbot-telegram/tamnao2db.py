import pymysql
import pandas as pd
import pymysql.cursors
import time
from bs4 import BeautifulSoup

from selenium import webdriver
driver = webdriver.Chrome('C:/Users/CPBGame001/Downloads/chromedriver_win32/chromedriver.exe')
url = 'https://www.tamnao.com/web/sp/productList.do;jsessionid=uW6wrzWS4atXaYpsxs6OaglpwL8hCil83dCmLIJJ7vPBVY9t4fkq1JOX3ysgxacd.DB_servlet_engine2?sCtgr=C200'
driver.get(url)


SCROLL_PAUSE_TIME = 1

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

while True:
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # Wait to load page
    time.sleep(SCROLL_PAUSE_TIME)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight-50);")
    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    new_height = driver.execute_script("return document.body.scrollHeight")

    if new_height == last_height:
        break

    last_height = new_height

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')

attractions = soup.select('div.product-item-area > ul.col4 > li')

titles = []
titles_none = []
urls = []
urls_none = []

for i in range(len(attractions)):
    try:
        title = attractions[i].select('div.title')[0].text
        titles.append(title)
        url = 'www.tamnao.com'+attractions[i].find("a").get('href')
        urls.append(url)
    except:
        title2 = attractions[i].find("img").get("alt")
        titles_none.append(title2)
        url2 = 'www.tamnao.com'+attractions[i].find("a").get('href')
        urls_none.append(url2)

######################################## DB에 삽입
# try:
#     DB_CONN = pymysql.connect(host='172.18.32.5', user='root', port=3306,
#                               password='1q2w3e4r5t!',  # database 접속 비밀번호
#                               db='jtodb',
#                               charset='utf8mb4',
#                               use_unicode=True,
#                               cursorclass=pymysql.cursors.DictCursor)
#
#     try:
#         with DB_CONN.cursor() as cursor:
#             cursor.executemany('INSERT INTO tamnao_product (title, url) VALUES (%s, %s)', list(zip(titles, urls)))
#         DB_CONN.commit()
#         print('Data Inserted')
#     except:
#         print("An error has occurred")
#     finally:
#         DB_CONN.close()
#         print("---------------")
# except:
#     print("connection ERROR")

