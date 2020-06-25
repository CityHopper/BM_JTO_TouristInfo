"""
main.py
텔레그램 연결 시작
"""
import tensorflow as tf
import data
import model as ml
from configs import DEFINES
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
from configparser import ConfigParser
import traceback

import chatbot_database
import answer_message


# 설정파일 로드(/config.ini)
conf = ConfigParser()
conf.read("./config.ini")

# estimator
classifier = None

# 단어 사전 변수
char2idx = None
idx2char = None
predict_output_dec = None
predict_target_dec = None
vocabulary_length = 0


# 제주관광공사_테스트봇 텔레그램 TOKEN
TELEGRAM_TOKEN = conf["TELEGRAM"]["TOKEN"]


# 사용자에게 메시지(질문) 받아서 처리
def get_message_handler(bot, update):
    message = update.message if update.message != None else update.callback_query.message

    # 사용자로부터 받은 메시지 정보
    received_from_user_message_info = {"update_id": update.update_id,
                                       "chat_id": message.chat_id,
                                       "message_id": message.message_id,
                                       "first_name": message.chat.first_name,
                                       "last_name": message.chat.last_name,
                                       "message_date": message.date,
                                       "message": message.text if update.message != None else update.callback_query.data}

    # 사용자에게 전송할 메시지 정보
    send_to_user_message_info = {"chat_id": message.chat_id,
                                 "update_id": -1,
                                 "first_name": bot.username,
                                 "last_name": bot.username}

    conn = chatbot_database.connect()

    try:
        print("db connect")

        # 받은 메시지 기록 저장
        chatbot_database.insert_chat_log(received_from_user_message_info)

        # 봇->사용자 답장 object
        result_send_info = None

        # command 메시지인 경우
        if len(message.entities) > 0 and message.entities[0].type == "bot_command":
            command_message = {"START" : call_start_command}
            command_func = command_message[message.text[1:].upper()] # command 메시지는 /로 시작
            command_reply = command_func(message)

            command_reply["chat_id"] = message.chat_id
            result_send_info = bot.sendMessage(**command_reply)

        # command callback 메시지
        elif update.callback_query != None:
            reply_text = "커맨드콜백:{}이(가) 선택되었습니다".format(update.callback_query.data)
            result_send_info = bot.edit_message_text(text=reply_text, chat_id=message.chat_id, message_id=message.message_id)

        # 일반 텍스트 메시지인 경우
        else:
            reply_text = get_text_message(message)
            result_send_info = bot.sendMessage(text=reply_text, chat_id=message.chat_id)

        # 보낸 메시지 log 저장
        send_to_user_message_info["message"] = result_send_info.text
        send_to_user_message_info["message_id"] = result_send_info.message_id
        send_to_user_message_info["message_date"] = result_send_info.date

        chatbot_database.insert_chat_log(send_to_user_message_info)

    except Exception as e:
        print("에러 : get_message_handler()")
        traceback.print_exc()

    finally:
        conn.close()
        print("db close")


# 일반 텍스트 메시지
def get_text_message(message):
    txt_message = message.text
    txt_message_without_whitespace = txt_message.replace(" ", "") # 사용자 질문에서 모든 공백제거
    result = ""
    
    # 근처 관광지 추천 질문 구분
    word_in_RC = ["근처", "가까운", "가까이", "옆에", "주위"]

    for word in word_in_RC:
        if word in txt_message_without_whitespace:
            place_name = txt_message_without_whitespace[:txt_message_without_whitespace.index(word)]
            result = "RC " + place_name
            break

    # 날씨 질문이거나 날씨 관련한 관광지 추천 질문 구분
    if not result:
        word_in_weather = ["날씨", "더워", "추워", "더운", "추운", "습한", "습해", "찜찜", "찝찝", "비내", "비오", "비와", "비가", "눈내", "눈와", "눈오", "눈이", "기상", "오늘"]  # 날씨 관련 질문 공통단어
        word_in_WR = ["추천", "관광지", "구경", "갈데", "명소", "유명", "갈만"]
        word_in_WR2 = ["어디", "곳", "장소", "관람", "볼거리", "볼거"] # 모델에서도 읽히는 단어 예외적으로 정의
        
        # 날씨 기반 관광지 추천
        for word2 in word_in_WR:
            if word2 in txt_message_without_whitespace:
                result = "WR"
                break
        
        # 날씨 정보
        if not result:
            for word in word_in_weather:
                if word in txt_message_without_whitespace:
                    result = "WT"

                    # 질문에 날씨+장소를 묻는 질문인 경우 ex) 날씨가 더운데 어디갈까?
                    for word_WR in word_in_WR2:
                        if word_WR in txt_message_without_whitespace:
                            result = "WR"
                            break

    if not result:
        # 질문에서 관광지명, 질문키워드(분류) 예측
        predict_input_enc, predict_input_enc_length = data.enc_processing([txt_message], char2idx)

        predictions = classifier.predict(input_fn=lambda: data.eval_input_fn(predict_input_enc, predict_output_dec, predict_target_dec, 1))
        result, finished = data.pred_next_string(predictions, idx2char)

    print("result :", result)

    # 답변 메시지 생성
    try:
        result_sep = result.split(" ")
        answer_key = result_sep[0].strip() # 질문키워드
        answer_place_name = result_sep[1].strip() if len(result_sep) > 1 else "" # 관광지명

        # 날씨 정보 답변
        if answer_key == "WT":
            return answer_message.get_weather(txt_message)

        # 날씨기반 관광지 답변
        elif answer_key == "WR":
            return answer_message.get_weather_based_place()

        # 위치기반 관광지 답변(근처 관광지)
        elif answer_key == "RC":
            return answer_message.get_location_based_place(answer_place_name)

        # 관광지 정보 답변
        else:
            return answer_message.get_place_info(answer_place_name, answer_key)

    except Exception as e:
        traceback.print_exc()

        return "제가 이해할 수 없는 질문이에요. 다른 질문을 해주시겠어요?" \
               "\n\n예시)"\
               "\n- 삼성혈 위치"\
               "\n- 오늘 날씨 어때"\
               "\n- 천지연폭포 유모차 대여 되나요?"\
               "\n- 제주시청 근처 관광지 (장소명)"\
               "\n- 광양9길10 근처 관광지 (주소)"\
               "\n- 관광지 추천해주세요!"


# start command 메시지(/start) *대화방 대화 시작 시 자동실행
def call_start_command(message):
    user_name = message.chat.last_name + " " + message.chat.first_name
    print(user_name + "님 새로운 대화 시작")

    return {"text" : user_name + "님 안녕하세요."
                                 "\n대화창에 제주 관광지에 대한 궁금한 것을 입력해주세요."
                                 "\n\n예시)"
                                 "\n- 삼성혈 위치"
                                 "\n- 오늘 날씨 어때"
                                 "\n- 천지연폭포 유모차 대여 되나요?"
                                 "\n- 제주시청 스타벅스 근처 관광지 (장소명)"
                                 "\n- 광양9길10 근처 관광지 (주소)"
                                 "\n- 관광지 추천해주세요!"
            }


# command 메시지 callback
def get_command_callback_handler(bot, update):
    print("callback")
    get_message_handler(bot, update)


############################################## 프로그램 시작 ##############################################
if __name__ == '__main__':
    # 사전 load
    char2idx, idx2char, vocabulary_length = data.load_vocabulary()

    predict_output_dec, predict_output_dec_length = data.dec_output_processing([""], char2idx)
    predict_target_dec = data.dec_target_processing([""], char2idx)

    # estimator 구성
    classifier = tf.estimator.Estimator(
            model_fn=ml.Model,  # 모델 등록한다.
            model_dir=DEFINES.check_point_path,  # 체크포인트 위치 등록한다.
            params={  # 모델 쪽으로 파라메터 전달한다.
                'model_hidden_size': DEFINES.model_hidden_size,  # 가중치 크기 설정한다.
                'ffn_hidden_size': DEFINES.ffn_hidden_size,
                'attention_head_size': DEFINES.attention_head_size,
                'learning_rate': DEFINES.learning_rate,  # 학습율 설정한다.
                'vocabulary_length': vocabulary_length,  # 딕셔너리 크기를 설정한다.
                'embedding_size': DEFINES.embedding_size,  # 임베딩 크기를 설정한다.
                'layer_size': DEFINES.layer_size,
                'max_sequence_length': DEFINES.max_sequence_length,
                'xavier_initializer': DEFINES.xavier_initializer
            })

    # 텔레그램 연결
    updater = Updater(TELEGRAM_TOKEN)

    # 핸들러 등록
    command_start_handler = CommandHandler("start", get_message_handler)
    command_callback_handler = CallbackQueryHandler(get_command_callback_handler)
    message_handler = MessageHandler(Filters.text, get_message_handler)

    updater.dispatcher.add_handler(command_start_handler)
    updater.dispatcher.add_handler(command_callback_handler)
    updater.dispatcher.add_handler(message_handler)

    # 텔레그램 메시지 응답 대기 시작
    updater.start_polling(timeout=10)
    updater.idle()