## 동네 예보 조회, https://www.data.go.kr/tcs/dss/selectApiDataDetailView.do?publicDataPk=15057682
from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus, unquote
# import pandas as pd
import json
from datetime import datetime, timedelta
import traceback


def weather_today(city_gubun):
    now = datetime.now()
    hour = now.hour

    while True:
        try:
            today = now.strftime('%Y%m%d')
            url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService/getVilageFcst'
            queryParams = '?' + urlencode({
                quote_plus(
                    'serviceKey'): '3Cz8y44yxy3z1fY6VWfk8m8YDvZSMrKJWeJ7uM%2F7ZbPJpXDQ1ljNxEDplkQsyGf1wA9W98rnutPWt76IQV1Tmg%3D%3D',
                quote_plus('pageNo'): '1',
                quote_plus('numOfRows'): '10',
                quote_plus('dataType'): 'JSON',
                quote_plus('base_date'): today,
                quote_plus('base_time'): str(hour) + '00',
                quote_plus('nx'): '53' if city_gubun == "J" else "52",  # 제주시 격자 X값=53, 서귀포시 격자 X값=52
                quote_plus('ny'): '38' if city_gubun == "J" else "33",  # 제주시 격자 Y값=38, 서귀포시 격자 Y값=33
            })

            print(url + unquote(queryParams))
            request = Request(url + unquote(queryParams))
            response_body = urlopen(request).read()
            data = json.loads(response_body)
            # result = pd.DataFrame(data['response']['body']['items']['item'])
            # print(result)

            weather_items = data["response"]["body"]["items"]["item"]
            weather_dict = {}

            for item in weather_items:
                if item["baseDate"] == today:
                    weather_dict[item["category"]] = item["fcstValue"]

            # 강수형태 문자형으로
            precipitation_type = {"0": "없음", "1": "비", "2": "비 또는 눈", "3": "눈", "4": "소나기"}  # 강수형태 정의
            weather_dict["PTY_TEXT"] = precipitation_type[weather_dict["PTY"]]

            # 하늘상태 문자형으로
            sky = int(weather_dict["SKY"])

            if 0 <= sky <= 5:
                weather_dict["SKY_TEXT"] = "맑음"
            elif 6 <= sky <= 8:
                weather_dict["SKY_TEXT"] = "구름많음"
            elif 9 <= sky <= 10:
                weather_dict["SKY_TEXT"] = "흐림"

            # pop = int(result[result['category'] == 'POP']['fcstValue']) # 강수확률(%)
            # pty = int(result[result['category'] == 'PTY']['fcstValue']) # 강수형태 [없음(0), 비(1), 비/눈(2), 눈(3), 소나기(4)]
            # # r06 = int(result[result['category'] == 'R06']['fcstValue'])
            # reh = int(result[result['category'] == 'REH']['fcstValue']) # 습도
            # # s06 = int(result[result['category'] == 'S06']['fcstValue'])
            # sky = int(result[result['category'] == 'SKY']['fcstValue']) # 하늘상태
            # t3h = int(result[result['category'] == 'T3H']['fcstValue']) # 기온 ('C)

            # 발표일시, 예보일시 string형으로
            base_data = data["response"]["body"]["items"]["item"][0]
            base_date = base_data["baseDate"]
            base_time = base_data["baseTime"]
            forecast_date = base_data["fcstDate"]
            forecast_time = base_data["fcstTime"]

            base_datetime = datetime.strptime(base_date + base_time, "%Y%m%d%H%M").strftime(
                "%Y년 %m월 %d일 %H시 %M분".encode('unicode-escape').decode()).encode().decode('unicode-escape')
            forecast_datetime = datetime.strptime(forecast_date + forecast_time, "%Y%m%d%H%M").strftime(
                "%Y년 %m월 %d일 %H시 %M분".encode('unicode-escape').decode()).encode().decode('unicode-escape')

            weather_dict["BASE_DATETIME"] = base_datetime
            weather_dict["FORECAST_DATETIME"] = forecast_datetime

            print(weather_dict)
            return weather_dict

        except KeyError:
            traceback.print_exc()
            now = now + timedelta(hours=-1)
            hour = now.strftime("%H")
            continue


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