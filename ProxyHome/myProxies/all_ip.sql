-- use ipHome;

DROP TABLE allip;

CREATE DATABASE allip CHARSET 'utf8';

CREATE TABLE allip (
    id INT UNSIGNED PRIMARY KEY NOT NULL AUTO_INCREMENT,
    `ip` VARCHAR(50) NOT NULL COMMENT '代理IP地址',
    `port` VARCHAR(30) NOT NULL COMMENT '该IP的端口',
    `type` VARCHAR(10) NOT NULL COMMENT '代理类型'
);