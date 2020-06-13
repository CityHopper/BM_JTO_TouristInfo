import requests

MYAPP_KEY = 'efc49d30d1ce74b230d8735843f48b59'


def getlonlat(keyword):
    keyword = str(keyword)
    url = 'https://dapi.kakao.com/v2/local/search/keyword.json?query={}'.format(keyword)
    headers = {
        'Authorization': 'KakaoAK {}'.format(MYAPP_KEY)
    }

    results = requests.get(url, headers=headers).json()['documents'][0]
    # print(results)
    # print((requests.get(url, headers=headers)).url)
    lon = results.get('x')
    lat = results.get('y')
    return lon, lat

# print(getlonlat("협재"))