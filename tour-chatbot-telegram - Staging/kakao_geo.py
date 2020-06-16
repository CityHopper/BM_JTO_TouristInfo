import requests

MYAPP_KEY = 'efc49d30d1ce74b230d8735843f48b59'


# 장소의 위도, 경도 조회
def getlonlat(keyword):
    keyword = ("제주" if "제주" not in keyword else "") + str(keyword)

    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(keyword)
    headers = {
        'Authorization': 'KakaoAK {}'.format(MYAPP_KEY)
    }

    result_json = requests.get(url, headers=headers).json()

    results = result_json['documents'][0]
    lon = results.get('x') # 경도
    lat = results.get('y') # 위도

    return lon, lat

#print(getlonlat("아트센터"))