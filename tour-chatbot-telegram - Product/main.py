import tensorflow as tf
import data
import model as ml
from configs import DEFINES
from telegram.ext import Updater, MessageHandler, CommandHandler, Filters, CallbackQueryHandler
from configparser import ConfigParser
import pymysql


# 설정파일 로드(/config.ini)
conf = ConfigParser()
conf.read("./config.ini")

# estimator
classifier = None

# 단어 사전 변수
char2idx = None
idx2char = None
vocabulary_length = 0

# 제주관광공사_테스트봇 텔레그램 TOKEN
TELEGRAM_TOKEN = conf["TELEGRAM"]["TOKEN"]

# 사용자에게 메시지 받아서 처리
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

    conn = connect_database()

    try:
        print("db connect")

        # 받은 메시지 기록 저장
        insert_chat_log(conn, received_from_user_message_info)

        # 봇->사용자 답장
        result_send_info = None

        # command 메시지
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

        # 일반 텍스트 메시지
        else:
            reply_text = get_text_message(message)
            result_send_info = bot.sendMessage(text=reply_text, chat_id=message.chat_id)

        # 보낸 메시지 기록 저장
        send_to_user_message_info["message"] = result_send_info.text
        send_to_user_message_info["message_id"] = result_send_info.message_id
        send_to_user_message_info["message_date"] = result_send_info.date

        insert_chat_log(conn, send_to_user_message_info)

    except Exception as e:
        print("에러!!!!!!!!!!!!!!!!!!!!!!!!!")
        print(e)

    finally:
        conn.close()
        print("db close")

# 일반 텍스트 메시지
def get_text_message(message):
    txt_message = message.text

    predict_input_enc, predict_input_enc_length = data.enc_processing([txt_message], char2idx)
    predict_output_dec, predict_output_dec_length = data.dec_output_processing([""], char2idx)
    predict_target_dec = data.dec_target_processing([""], char2idx)

    predictions = classifier.predict(input_fn=lambda: data.eval_input_fn(predict_input_enc, predict_output_dec, predict_target_dec, 1))
    answer, finished = data.pred_next_string(predictions, idx2char)

    print("result :", answer)

    return "받은메시지: " + txt_message + "\n" + "결과값: " + answer

# start command 메시지(/start) *대화방 대화 시작 시 자동실행
def call_start_command(message):
    user_name = message.chat.last_name + " " + message.chat.first_name
    print(user_name + "님 새로운 대화 시작")

    return {"text" : user_name + "님 안녕하세요.\n대화창에 질문을 입력해주세요."}

# command 메시지 callback
def get_command_callback_handler(bot, update):
    print("callback")
    get_message_handler(bot, update)

# 데이터베이스 연결
def connect_database():
    db_conf = conf["DB"] # 데이터베이스 정보 불러오기
    conn = pymysql.connect(host=db_conf["HOST"],
                           port=int(db_conf["PORT"]),
                           user=db_conf["USER"],
                           password=db_conf["PASSWORD"],
                           db=db_conf["DB_NAME"],
                           charset='utf8mb4',
                           use_unicode=True,
                           cursorclass=pymysql.cursors.DictCursor)

    return conn

# 대화 기록 저장
def insert_chat_log(conn, chat):
    cur = conn.cursor()
    insert_sql = "INSERT INTO tour_chat({}) VALUES ({})".format(",".join(chat.keys()), ",".join(["%s"] * len(chat)))

    cur.execute(insert_sql, tuple(chat.values()))

    conn.commit()

    print(insert_sql)
    print(tuple(chat.values()))

############################################## 프로그램 시작 ##############################################
if __name__ == '__main__':
    # 사전 load
    char2idx, idx2char, vocabulary_length = data.load_vocabulary()

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
