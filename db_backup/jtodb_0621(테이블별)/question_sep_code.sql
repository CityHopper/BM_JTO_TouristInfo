-- --------------------------------------------------------
-- 호스트:                          127.0.0.1
-- 서버 버전:                        10.4.12-MariaDB - mariadb.org binary distribution
-- 서버 OS:                        Win64
-- HeidiSQL 버전:                  11.0.0.5919
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;

-- 테이블 jtodb.question_sep_code 구조 내보내기
DROP TABLE IF EXISTS `question_sep_code`;
CREATE TABLE IF NOT EXISTS `question_sep_code` (
  `code` char(2) NOT NULL,
  `code_name` varchar(100) NOT NULL DEFAULT '',
  `rel_col` varchar(1000) DEFAULT '',
  PRIMARY KEY (`code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='질문 구분(카테고리) 코드';

-- 테이블 데이터 jtodb.question_sep_code:~11 rows (대략적) 내보내기
DELETE FROM `question_sep_code`;
/*!40000 ALTER TABLE `question_sep_code` DISABLE KEYS */;
INSERT INTO `question_sep_code` (`code`, `code_name`, `rel_col`) VALUES
	('AD', '주소', 'full_address,detail_address,discount_ticket_url'),
	('BC', '유모차대여', 'baby_carriage'),
	('OV', '소개', 'overview,discount_ticket_url'),
	('PK', '주차정보', 'parking,parking_fee'),
	('RC', '위치기반추천', 'inout'),
	('ST', '소요시간', 'spend_time'),
	('TE', '연락처', 'tel,info_center'),
	('UF', '입장료', 'use_fee,discount_info,discount_ticket_url'),
	('UT', '이용시간', 'use_time,use_season,rest_date'),
	('WR', '날씨기반추천', 'inout'),
	('WT', '날씨', '');
/*!40000 ALTER TABLE `question_sep_code` ENABLE KEYS */;

/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IF(@OLD_FOREIGN_KEY_CHECKS IS NULL, 1, @OLD_FOREIGN_KEY_CHECKS) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
