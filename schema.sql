CREATE TABLE IF NOT EXISTS `components`(
	`cid`	INT NOT NULL UNIQUE,
  	`maxBom`	INT NOT NULL,
	`minBom`	INT NOT NULL,
	`meanBom`	INT NOT NULL,
	`maxChild`	INT NOT NULL,
`minChild`	INT NOT NULL,
	`meanChild`INT NOT NULL,
	`maxDoc`	INT NOT NULL,
	`minDoc`	INT NOT NULL,
	`meanDoc`	INT NOT NULL,
	`maxMat`	INT NOT NULL,
	`minMat`	INT NOT NULL,
	`meanMat`	INT NOT NULL,
	`nrComponents` INT NOT NULL,
	`date` DATETIME NOT NULL
);

CREATE TABLE IF NOT EXISTS `anomalies`(
	`cid` TEXT NOT NULL,
	`revison` INT NOT NULL
);
