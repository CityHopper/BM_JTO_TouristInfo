from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
from chatterbot.trainers import ChatterBotCorpusTrainer

# Create a new chat bot named Charlie
chatbot = ChatBot('Charlie')
# Create a new Trainer
trainer = ChatterBotCorpusTrainer(chatbot)

trainer.train(
 "chatterbot.corpus.english"
)

# The following loop will execute each time the user enters input
while True:
    try:
        user_input = input()
        bot_response = chatbot.get_response(user_input)
        print(bot_response)

# Press ctrl-c or ctrl-d on the keyboard to exit
    except (KeyboardInterrupt, EOFError, SystemExit):
        break

# conversation = [
#     "Hello",
#     "Hi there!",
#     "How are you doing?",
#     "I'm doing great.",
#     "That is good to hear",
#     "Thank you.",
#     "You're welcome.",
#     "Hi, can I help you?",
#     "Sure, I'd like to book a flight to Iceland.",
#     "Your flight has been booked."
# ]
# # Create a new chat bot named Charlie
# chatbot = ChatBot('Charlie')
# # Create a new Trainer
# trainer = ListTrainer(chatbot)
#
# trainer.train(conversation)
# # Get a response to the input text 'Good morning.'
# response = chatbot.get_response("Good morning!")
# print(response)
# # Get a response to the input text 'I would like to book a flight.'
# response = chatbot.get_response('I would like to book a flight.')
# print(response)

'''
# 영화 리뷰 댓글 데이터로 특정 단어의 유사단어 찾는 모델 만들기
import csv
from konlpy.tag import Okt
from gensim.models import word2vec

#네이버 영화 코퍼스를 읽는다.
f = open('./nsmc-master/ratings_train.txt', 'r', encoding='utf-8')
rdr = csv.reader(f, delimiter='\t')
rdw = list(rdr)
f.close()

#트위터 형태소 분석기를 로드한다. Twiter가 KoNLPy v0.4.5 부터 Okt로 변경 되었다.
twitter = Okt()

#텍스트를 한줄씩 처리합니다.
result = []
for line in rdw:
    #형태소 분석하기, 단어 기본형 사용
    malist = twitter.pos(line[1], norm=True, stem=True)
    r = []
    for word in malist:
        #Josa”, “Eomi”, “'Punctuation” 는 제외하고 처리
        if not word[1] in ["Josa","Eomi","Punctuation"]:
            r.append(word[0])
    #형태소 사이에 공백 " "  을 넣습니다. 그리고 양쪽 공백을 지웁니다.
    rl = (" ".join(r)).strip()
    result.append(rl)
    #print(rl)

#형태소들을 별도의 파일로 저장 합니다.
with open("NaverMovie.nlp",'w', encoding='utf-8') as fp:
    fp.write("\n".join(result))

#Word2Vec 모델 만들기
wData = word2vec.LineSentence("NaverMovie.nlp")
wModel = word2vec.Word2Vec(wData, size=200, window=10, hs=1, min_count=2, sg=1)
wModel.save("NaverMovie.model")
print("Word2Vec Modeling finished")

from gensim.models import word2vec
model = word2vec.Word2Vec.load("NaverMovie.model")
print(model.wv.most_similar(positive=["재미"]))
print(model.wv.most_similar(positive=["감독"]))
'''
