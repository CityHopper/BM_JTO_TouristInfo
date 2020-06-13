### 동네 예보 조회, https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15057682
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus, unquote
import pandas as pd
import json
from datetime import datetime

def weather_today():
    today = datetime.today().strftime('%Y%m%d')
    hour = datetime.now().hour - 1
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst'
    queryParams = '?' + urlencode({
        quote_plus('serviceKey'): '3Cz8y44yxy3z1fY6VWfk8m8YDvZSMrKJWeJ7uM%2F7ZbPJpXDQ1ljNxEDplkQsyGf1wA9W98rnutPWt76IQV1Tmg%3D%3D',
        quote_plus('pageNo'): '1',
        quote_plus('numOfRows'): '10',
        quote_plus('dataType'): 'JSON',
        quote_plus('base_date'): today,
        quote_plus('base_time'): str(hour)+'00',
        quote_plus('nx'): '53', # 제주시 격자 X값=53, 서귀포시 격자 X값=52
        quote_plus('ny'): '38', # 제주시 격자 Y값=38, 서귀포시 격자 Y값=33
    })

    print(url + unquote(queryParams))
    request = Request(url + unquote(queryParams))
    response_body = urlopen(request).read()
    data = json.loads(response_body)
    result = pd.DataFrame(data['response']['body']['items']['item'])
    # print(result)

    pop = int(result[result['category'] == 'POP']['fcstValue'])
    pty = int(result[result['category'] == 'PTY']['fcstValue'])
    r06 = int(result[result['category'] == 'R06']['fcstValue'])
    reh = int(result[result['category'] == 'REH']['fcstValue'])
    s06 = int(result[result['category'] == 'S06']['fcstValue'])
    sky = int(result[result['category'] == 'SKY']['fcstValue'])
    t3h = int(result[result['category'] == 'T3H']['fcstValue'])

    return pop, pty, r06, reh, s06, sky, t3h
'''
- 동네예보 결과값 코드 설명(단위)
POP 강수확률 (%)
PTY 강수형태 (코드값) [없음(0), 비(1), 비/눈(2), 눈(3), 소나기(4) 여기서 비/눈은 비와 눈이 섞여 오는 것을 의미 (진눈개비)]
R06 6시간 강수량 (1mm)
REH 습도 (%)
S06 6시간 신적설 (1cm)
SKY 하늘 상태 (코드값)
T3H 3시간 기온 ('C)
UUU 풍속(동서성분) - 사용 X
VEC 풍향 (m/s) - 사용 X
VVV 풍속(남북성분) - 사용 X
'''

