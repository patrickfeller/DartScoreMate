CREATE OR REPLACE TABLE `game` (
	`game_mode` SMALLINT NOT NULL,
	`player_A` VARCHAR(63),
	`player_B` VARCHAR(63),
	`score_player_A` SMALLINT NOT NULL,
	`score_player_B` SMALLINT NOT NULL,
	`game_id` SMALLINT AUTO_INCREMENT UNIQUE,
	`active_player` VARCHAR(63),
	`throw_1` VARCHAR(5) NOT NULL,
	`throw_2` VARCHAR(5) NOT NULL,
	`throw_3` VARCHAR(5) NOT NULL,
	`legs_played` TINYINT,
	`first_to` TINYINT,
	`wins_playerA` TINYINT,
	`wins_playerB` TINYINT, 
	PRIMARY KEY(`game_id`)
);

