-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema smartincubator
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema smartincubator
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `smartincubator` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `smartincubator` ;

-- -----------------------------------------------------
-- Table `smartincubator`.`incubator`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `smartincubator`.`incubator` (
  `humidity` FLOAT NULL DEFAULT 0,
  `temperature` FLOAT NULL DEFAULT 0,
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 4
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `smartincubator`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `smartincubator`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(45) NOT NULL,
  `created_on` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE,
  UNIQUE INDEX `password_UNIQUE` (`password` ASC) VISIBLE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


-- -----------------------------------------------------
-- Table `smartincubator`.`configurations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `smartincubator`.`configurations` (
  `id` INT(11) NOT NULL,
  `name` VARCHAR(45) NOT NULL,
  `species` VARCHAR(45) NOT NULL,
  `temperature` VARCHAR(45) NOT NULL,
  `humdity` VARCHAR(45) NOT NULL,
  `duration` VARCHAR(45) NOT NULL,
  `notes` VARCHAR(45) NOT NULL,
  `created_on` DATETIME NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `id_UNIQUE` (`id` ASC) VISIBLE,
  UNIQUE INDEX `name_UNIQUE` (`name` ASC) VISIBLE,
  CONSTRAINT `user_id`
    FOREIGN KEY (`id`)
    REFERENCES `smartincubator`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
