input_data = '판교에 지금 주문해줘'
output_data = ''

request = {
    "intent_id": " ",
    "input_data": input_data,
    "request_type": "text",
    "story_slot_entity": {},
    "output_data": output_data
}

intent_list = {
    "주문": ["주문", "배달"],
    "예약": ["예약", "잡아줘"],
    "정보": ["정보", "알려"]
}

story_slot_entity = {"주문": {"메뉴": None, "장소": None, "날짜": None},
                     "예약": {"장소": None, "날짜": None},
                     "정보": {"대상": None}
                     }

from konlpy.tag import Mecab

mecab = Mecab("경로/mecab-ko-dic")
preprocessed = mecab.pos(request.get(input_data))
print(preprocessed)

intent_id = '주문'
slot_value = story_slot_entity.get('주문')

menu_list = ['피자', '햄버거', '치킨']
loc_list = ['판교', '야탑', '서현']
date_list = ['지금', '내일', '모레']

for pos_tag in preprocessed:
    for i in range(0, len(preprocessed)):
        if pos_tag[i] in ['NNG', 'NNP', 'SL', 'MAG']:
            if pos_tag[0] in menu_list:
                slot_value['메뉴'] = pos_tag[0]
            elif pos_tag[0] in loc_list:
                slot_value['장소'] = pos_tag[0]
            elif pos_tag[0] in date_list:
                slot_value['날짜'] = pos_tag[0]
print(story_slot_entity.get('주문'))