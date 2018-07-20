-- DROP DATABASE ipHome;
--
-- CREATE DATABASE ipHome charset 'utf8';
--
-- use ipHome;

use allip;

CREATE TABLE ipipip (
    id INT UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `ip` VARCHAR(50) NOT NULL COMMENT '代理IP地址',
    `port` VARCHAR(30) NOT NULL COMMENT '该IP的端口',
    `type` VARCHAR(10) NOT NULL COMMENT '代理类型',
    `nmd` VARCHAR(50) COMMENT '代理匿名度',
    `wz` VARCHAR(50) COMMENT '代理所处的位置',
    `xysd` VARCHAR(50) COMMENT '响应速度',
    `zhyzsj` VARCHAR(50) COMMENT '最后验证时间',
    `score` VARCHAR(10) COMMENT '代理得分'
);