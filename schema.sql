CREATE TABLE IF NOT EXISTS `components`(
	`cid`	INT NOT NULL UNIQUE,
  	`meanDoc`	INT NOT NULL,
	`meanBom`	INT NOT NULL,
	`meanChild`	INT NOT NULL,
	`maxDoc`	INT NOT NULL,
	`maxBom`	INT NOT NULL,
	`maxChild`	INT NOT NULL,
	`minDoc`	INT NOT NULL,
	`minBom`	INT NOT NULL,
	`minChild`	INT NOT NULL,
	`nrComponents` INT NOT NULL
);

CREATE TABLE IF NOT EXISTS `anomalies`(
	`cid` TEXT NOT NULL,
	`revison` INT NOT NULL
);
