CREATE OR REPLACE TABLE `game` (
	`game_mode` SMALLINT NOT NULL,
	`player_A` VARCHAR(63),
	`player_B` VARCHAR(63),
	`score_player_A` SMALLINT,
	`score_player_B` SMALLINT,
	`game_id` SMALLINT AUTO_INCREMENT UNIQUE,
	PRIMARY KEY(`game_id`)
);

