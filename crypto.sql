/*
 Navicat MySQL Data Transfer

 Source Server         : localhost_phpstudy
 Source Server Type    : MySQL
 Source Server Version : 50553
 Source Host           : localhost:3306
 Source Schema         : crypto

 Target Server Type    : MySQL
 Target Server Version : 50553
 File Encoding         : 65001

 Date: 14/03/2023 14:53:16
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for group
-- ----------------------------
DROP TABLE IF EXISTS `group`;
CREATE TABLE `group`  (
  `uid` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT 'id',
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL COMMENT '账号',
  `groupname` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL COMMENT '名称',
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT 'password' COMMENT '密码',
  `membernums` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL DEFAULT '0' COMMENT '组成员的数量',
  `e` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `s` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `r` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `G` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `H` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `member` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `com1_1` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `com2_1` text CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `resp1_1` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `resp2_1` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of group
-- ----------------------------

-- ----------------------------
-- Table structure for management
-- ----------------------------
DROP TABLE IF EXISTS `management`;
CREATE TABLE `management`  (
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `identity` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`username`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of management
-- ----------------------------
INSERT INTO `management` VALUES ('manage_admin', 'manage_admin_passwd', 'manage');
INSERT INTO `management` VALUES ('counting_admin', 'counting_admin_passwd', 'counting');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `uid` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NOT NULL,
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `ri` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL,
  `belong` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`uid`) USING BTREE
) ENGINE = MyISAM CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------

-- ----------------------------
-- Table structure for vote_contents
-- ----------------------------
DROP TABLE IF EXISTS `vote_contents`;
CREATE TABLE `vote_contents`  (
  `tid` tinyint(50) NOT NULL AUTO_INCREMENT,
  `themes` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `isvoters` char(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT 'NO',
  `deadtime` datetime NULL DEFAULT NULL,
  `user_submit` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  `isvalid` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin NULL DEFAULT NULL,
  PRIMARY KEY (`tid`) USING BTREE
) ENGINE = MyISAM AUTO_INCREMENT = 18 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_bin ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of vote_contents
-- ----------------------------

SET FOREIGN_KEY_CHECKS = 1;
