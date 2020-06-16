# 위치 기반 관광지 추천 XML -
import requests
from xml.etree.ElementTree import fromstring
#from kakao_geo import getlonlat

#lon, lat = getlonlat("제주시청")

# 위도, 경도 값의 반경 10km의 관광지 목록 조회
def attraction_by_lonlat(lon, lat):

    url = 'http://api.visitkorea.or.kr/openapi/service/rest/KorService/locationBasedList?'
    headers = {
        'serviceKey': requests.utils.unquote('3Cz8y44yxy3z1fY6VWfk8m8YDvZSMrKJWeJ7uM%2F7ZbPJpXDQ1ljNxEDplkQsyGf1wA9W98rnutPWt76IQV1Tmg%3D%3D'),
        'numOfRows': '10',
        'pageNo': '1',
        'MobileOS': 'ETC',
        'MobileApp': 'AppTest',
        'arrange': 'A',
        'contentTypeId': '12',
        'mapX': lon,
        'mapY': lat,
        'radius': '1000', # 반경 10km
        'listYN': 'Y',
        'modifiedtime': ''
    }

    response = requests.get(url, params=headers)

    # print(response) # response [200]: 페이지랑 서버에 문제 없다는 뜻
    print(response.url)
    root = fromstring(response.text)
    recommended_attraction = []
    for item in root.findall('./body/items/item'):
        recommended_attraction.append([item.find("title").text, item.find("addr1").text])
        # print(item.find("title").text)
        # print(item.find("addr1").text)

    howmany = 3 # 추천할 관광지 개수
    if len(recommended_attraction) >= howmany:
        recommended_attraction = recommended_attraction[0:howmany]
    elif len(recommended_attraction) == 0:
        recommended_attraction = None

    return recommended_attraction # 리스트 안의 리스트로 관광지 이름과 주소 반환

#print(attraction_by_lonlat(lon, lat))