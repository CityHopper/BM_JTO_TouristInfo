-- 생성되어야 할 질문개수
SELECT t1.cnt 질문, t2.cnt 관광지1, t3.cnt 관광지2, t1.cnt * (t2.cnt + t3.cnt) 관광지별질문
   FROM (SELECT COUNT(1) cnt FROM base_question) t1
      , (SELECT COUNT(1) cnt FROM tour_place WHERE title1 <> '') t2
      , (SELECT COUNT(1) cnt FROM tour_place WHERE title2 <> '') t3

;

-- 생성된 질문 조회
SELECT COUNT(1) FROM question;
SELECT * FROM question;