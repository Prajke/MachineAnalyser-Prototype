CREATE TABLE IF NOT EXISTS `products`(
	`cid`	TEXT NOT NULL,
	`revison`	INT NOT NULL,
  `meanDoc`	INT NOT NULL,
	`meanPop`	INT NOT NULL,
	`meanChild`	INT NOT NULL,
	`maxDoc`	INT NOT NULL,
	`maxPop`	INT NOT NULL,
	`maxChild`	INT NOT NULL,
	`minDoc`	INT NOT NULL,
	`minPop`	INT NOT NULL,
	`minChild`	INT NOT NULL,
	`totalComponents` INT NOT NULL
);

CREATE TABLE IF NOT EXISTS `anomalies`(
	`cid` TEXT NOT NULL,
	`revison` INT NOT NULL
);
