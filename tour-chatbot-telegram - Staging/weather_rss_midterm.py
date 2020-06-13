# 기상청 중기 예보
# http://www.weather.go.kr/weather/lifenindustry/sevice_rss.jsp?sido=5000000000&x=36&y=9&gugun=1159000000&dong=1159068000


import urllib.request, re

url = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=184'
ufile = urllib.request.urlopen(url)
contents = ufile.read().decode('utf-8')
locations = re.findall(r'<location wl_ver="3">.+?</location>',contents, re.DOTALL)

for loc in locations:
    province = re.search(r'<province>(.+)</province>', loc)
    city = re.search(r'<city>(.+)</city>', loc)

    print(province.group(1))
    print(city.group(1))

    data = re.findall(r'<data>.+?</data>', loc, re.DOTALL)

    for item in data:
        mode = re.search(r'<mode>(.+)</mode>', item)
        tmEf = re.search(r'<tmEf>(.+)</tmEf>', item)
        wf = re.search(r'<wf>(.+)</wf>', item)
        tmn = re.search(r'<tmn>(.+)</tmn>', item)
        tmx = re.search(r'<tmx(.+)</tmx>', item)
        reli = re.search(r'<reliability>(.+)</reliability>', item)

        print('  ', mode.group(1), tmEf.group(1), wf.group(1), tmn.group(1), tmx.group(1))
