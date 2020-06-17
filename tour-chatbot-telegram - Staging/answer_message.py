"""
answer_message.py

챗봇이 사용자의 질문에 응답(answer)하기 위해 메시지를 생성한다.
- 관광지 정보, 날씨
"""
import traceback
import re

import chatbot_database
import weather_api
import kakao_geo
import locbased_attrac


# 질문한 관광지의 정보 가져오기
def get_place_info(place_name, question_keyword):
    # 관광지 정보 조회(관광지명, 질문키워드)
    place_info = chatbot_database.retrieve_place_info(place_name, question_keyword)

    # 관광지 정보가 존재하지 않을 경우 정보없음 메시지 출력
    if not [x for x in place_info.values() if x]:
        return place_name + "의 정보가 없습니다."

    result_msg = place_info["org_title"] + "의 "  # 답변할 메시지(시작 : [관광지명]의 ~~)
    msg_list = []  # 답변과 관련된 컬럼이 여러개일 경우 list 사용

    # <br>태그 \n으로 변환
    pattern = "\<[br /^>]*\>"
    for key, value in place_info.items():
        place_info[key] = re.sub(pattern=pattern, repl="\n", string=value)

    # 질문키워드별 메시지 생성
    if question_keyword == "AD":
        msg_list.append("주소는\n" + place_info["full_address"] + place_info["detail_address"])

    elif question_keyword == "BC":
        result_msg += "유모차 대여는 " + place_info["baby_carriage"]

    elif question_keyword == "OV":
        place_info["overview"] = re.sub(pattern=pattern, repl="\n", string=place_info["overview"])

        msg_list.append("정보입니다.\n\n" + place_info["overview"])

    elif question_keyword == "PK":
        msg_list.append("주차정보 입니다.\n" + place_info["parking"]) if place_info["parking"] else None
        msg_list.append("주차요금정보 입니다.\n" + place_info["parking_fee"]) if place_info["parking_fee"] else None

    elif question_keyword == "ST":
        result_msg += "소요시간은 " + place_info["spend_time"] if place_info["spend_time"] else None

    elif question_keyword == "TE":
        msg_list.append("전화번호는\n" + place_info["tel"]) if place_info["tel"] else None
        msg_list.append("기타 전화번호는\n" + place_info["info_center"]) if place_info["info_center"] else None

    elif question_keyword == "UF":
        msg_list.append("입장료는 " + place_info["use_fee"]) if place_info["use_fee"] else None
        msg_list.append("할인정보는 " + place_info["discount_info"]) if place_info["discount_info"] else None

    elif question_keyword == "UT":
        msg_list.append("이용 가능한 시간은 " + place_info["use_time"]) if place_info["use_time"] else None
        msg_list.append("이용 가능한 계절은 " + place_info["use_season"]) if place_info["use_season"] else None
        msg_list.append("\n*쉬는 날은 " + place_info["rest_date"]) if place_info["rest_date"] else None

    # 존재하지 않은 키워드에는 답변불가 메시지 출력
    else:
        return "질문에 답변을 할 수 없습니다."

    # 주소, 소개, 이용요금 답변에는 추가로 입장권 구매 링크 전송한다.
    if question_keyword in ["AD", "OV", "UF"]:
        msg_list.append("\n* " + place_name + "의 이용권/입장권을 미리 구매할 수 있어요!\n" + place_info["discount_ticket_url"]) if place_info["discount_ticket_url"] else None

    result_msg += "\n".join(msg_list)

    return result_msg


# 위치기반 관광지 추천(근처 관광지)
def get_location_based_place(place_name):
    lon, lat = kakao_geo.getlonlat(place_name)  # 경도, 위도

    place_list = locbased_attrac.attraction_by_lonlat(lon, lat)

    if not place_list:
        return place_name + " 근처 반경 20km 내에 관광지가 없습니다."

    else:
        result_msg = "'" + place_name + "' 근처 반경 20km내 관광지입니다.\n"

        for idx, place in enumerate(place_list):
            result_msg += str(idx+1) + ". " + place[0] + " (" + place[1] + ")\n"

    return result_msg


# 날씨 기반 관광지 추천
def get_weather_based_place():
    weather = weather_api.weather_today("J")
    inout_code = "O" # I:실내, O:실외, C:실내+실외
    
    # 실내 추천 기준 : 강수확률 70이상, 기온 35도이상, 강수형태 눈/비/소나기인 경우
    if int(weather["POP"]) >= 70 or int(weather["T3H"]) >= 35 or int(weather["PTY"]) > 0:
        inout_code = "I"

    place_list = chatbot_database.retrieve_attraction_by_inout(inout_code)

    if not place_list:
        return "추천할만한 관광지가 없습니다."

    else:
        result_msg = "오늘은 야외관광을 하기 괜찮은 날씨입니다. " if inout_code == "O" else "오늘은 실내관광을 하는 게 좋을 것 같습니다. "
        result_msg += "다음 관광지들을 추천합니다.\n\n"

        for idx, place in enumerate(place_list):
            result_msg += str(idx+1) + ". " + place["title"] + "("+place["category"] +")\n" + place["full_address"] + "\n"

    return result_msg


# 날씨 정보 가져오기
def get_weather(msg):
    city_gubun = "J" if "서귀포" not in msg else "S"

    weather_info = weather_api.weather_today(city_gubun)

    today_gubun = "오늘 " if weather_info["BASE_DATETIME"][:13] == weather_info["FORECAST_DATETIME"][:13] else "내일 "
    
    result_msg = "\n\n기상청에서 " + weather_info["BASE_DATETIME"] + "에 발표한 \n" + today_gubun + weather_info["FORECAST_DATETIME"][-7:] + " 기준 예보입니다.\n"
    result_msg += "제주시 " if city_gubun == "J" else "서귀포시 날씨는 "
    result_msg += "하늘은 '" + weather_info["SKY_TEXT"] + "' 입니다. "
    result_msg += "\n" + weather_info["PTY_TEXT"] + "가(이) 내릴 가능성이 있습니다. " if weather_info["PTY"] != "0" else ""
    result_msg += "\n기온은 " + str(weather_info["T3H"]) + "'C, 습도는 " + str(weather_info["REH"]) + "% 입니다. "
    result_msg += "강수확률은 " + str(weather_info["POP"]) + "% 입니다."

    print(result_msg)

    return result_msg