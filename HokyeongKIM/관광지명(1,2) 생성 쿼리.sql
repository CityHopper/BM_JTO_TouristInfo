# title1 생성 -> 괄호 제거
#SELECT trim(REGEXP_REPLACE(org_title,"\\(([^)]+)\\)|\\[([^]]+)\\]", '')) FROM tour_place;

#UPDATE tour_place
#   SET title1 = trim(REGEXP_REPLACE(org_title,"\\(([^)]+)\\)|\\[([^]]+)\\]", ''))

# title2 생성 -> 괄호 안
#SELECT org_title
#     , REGEXP_REPLACE(trim(REPLACE(org_title, title1, '')), "\\(|\\)|\\[|\\]", '')
#  FROM tour_place
# WHERE org_title <> title1
#   AND org_title NOT LIKE '%(제주)%';
   
#UPDATE tour_place
#   SET title2 = REGEXP_REPLACE(trim(REPLACE(org_title, title1, '')), "\\(|\\)|\\[|\\]", '')
# WHERE org_title <> title1
#   AND org_title NOT LIKE '%(제주)%';
 
# 제주올레->올레
SELECT org_title, title1, title2, REPLACE(title2, '제주', '')
  FROM tour_place
 WHERE title2 LIKE '제주올레%';
 
 UPDATE tour_place
    SET title2 = REPLACE(title2, '제주', '')
  WHERE title2 LIKE '제주올레%';
  
SELECT org_title, title1, title2
  FROM tour_place
 WHERE title1 LIKE '%해변%';