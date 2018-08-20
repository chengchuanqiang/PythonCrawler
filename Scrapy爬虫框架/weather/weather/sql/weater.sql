CREATE TABLE `weather` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `date` char(24) DEFAULT NULL,
  `week` char(24) DEFAULT NULL,
  `img` char(128) DEFAULT NULL,
  `temperature` char(24) DEFAULT NULL,
  `weather` char(24) DEFAULT NULL,
  `wind` char(24) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8;