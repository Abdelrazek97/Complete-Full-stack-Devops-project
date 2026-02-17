
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255) NOT NULL,
  `password` VARCHAR(255) NOT NULL,
  `department` VARCHAR(255) NOT NULL,
  `role` VARCHAR(50) NOT NULL DEFAULT 'user',
  `full_name` VARCHAR(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `Evaluation_aspects` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `Develop_courses` INT DEFAULT NULL,
  `Prepare_file` INT DEFAULT NULL,
  `Electronic_tests` INT DEFAULT NULL,
  `Prepare_material_content` INT DEFAULT NULL,
  `Use_learning_effectively` INT DEFAULT NULL,
  `teaching_methods` INT DEFAULT NULL,
  `Methods_student` INT DEFAULT NULL,
  `preparing_test_questions` INT DEFAULT NULL,
  `Provide_academic_guidance` INT DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Develop_courses_Evaluation` INT DEFAULT NULL,
  `Prepare_file_Evaluation` INT DEFAULT NULL,
  `Electronic_tests_Evaluation` INT DEFAULT NULL,
  `Prepare_material_Evaluation` INT DEFAULT NULL,
  `Use_learning_Evaluation` INT DEFAULT NULL,
  `teaching_methods_Evaluation` INT DEFAULT NULL,
  `Methods_student_Evaluation` INT DEFAULT NULL,
  `preparing_test_Evaluation` INT DEFAULT NULL,
  `Provide_academic_Evaluation` INT DEFAULT NULL,
  `aspects_sum` INT DEFAULT NULL,
  `evaluation_sum` INT DEFAULT NULL,
  `evaluation_year` INT GENERATED ALWAYS AS (YEAR(`created_at`)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_evaluation_aspects_user_year` (`evaluation_year`, `user_id`),
  KEY `idx_evaluation_aspects_user` (`user_id`),
  CONSTRAINT `fk_evaluation_aspects_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `Scientific_production` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `Scientific_research` INT NOT NULL,
  `supervision_Graduation` INT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `Scientific_research_Evaluation` INT DEFAULT NULL,
  `supervision_Graduation_Evaluation` INT DEFAULT NULL,
  `evaluation_year` INT GENERATED ALWAYS AS (YEAR(`created_at`)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_scientific_production_user_year` (`evaluation_year`, `user_id`),
  KEY `idx_scientific_production_user` (`user_id`),
  CONSTRAINT `fk_scientific_production_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `Scientific_research` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `scientific_output` TEXT,
  `Authors_names` TEXT,
  `Publisher` TEXT,
  `Agency` TEXT,
  `year` VARCHAR(20) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `research_type` TEXT,
  `DOI` TEXT,
  PRIMARY KEY (`id`),
  KEY `idx_scientific_research_user` (`user_id`),
  CONSTRAINT `fk_scientific_research_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `University_Service` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `task_level` TEXT,
  `task_type` TEXT,
  `notes` TEXT,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_university_service_user` (`user_id`),
  CONSTRAINT `fk_university_service_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `academic_data` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `semester` VARCHAR(100) NOT NULL,
  `course_code` VARCHAR(100) NOT NULL,
  `num_students` INT DEFAULT NULL,
  `teaching_load` VARCHAR(255) DEFAULT NULL,
  `course_name` VARCHAR(255) DEFAULT NULL,
  `semester_type` VARCHAR(50) DEFAULT NULL,
  `credit_hours` INT DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_academic_data_user` (`user_id`),
  CONSTRAINT `fk_academic_data_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `activity_data` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `activity_title` TEXT,
  `activity_date` DATE DEFAULT NULL,
  `duration` TEXT,
  `participation_type` TEXT,
  `place` TEXT,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_activity_data_user` (`user_id`),
  CONSTRAINT `fk_activity_data_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `ethics_responsibility` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `professional_values` INT NOT NULL,
  `offer_encouragement` INT NOT NULL,
  `respect_leaders` INT NOT NULL,
  `take_responsibility` INT NOT NULL,
  `decent_appearance` INT NOT NULL,
  `punctuality` INT NOT NULL,
  `office_hours` INT NOT NULL,
  `professional_values_evaluation` INT DEFAULT NULL,
  `offer_encouragement_evaluation` INT DEFAULT NULL,
  `respect_leaders_evaluation` INT DEFAULT NULL,
  `take_responsibility_evaluation` INT DEFAULT NULL,
  `decent_appearance_evaluation` INT DEFAULT NULL,
  `punctuality_evaluation` INT DEFAULT NULL,
  `office_hours_evaluation` INT DEFAULT NULL,
  `aspects_sum` INT DEFAULT NULL,
  `evaluation_sum` INT DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `evaluation_year` INT GENERATED ALWAYS AS (YEAR(`created_at`)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_ethics_responsibility_user_year` (`evaluation_year`, `user_id`),
  KEY `idx_ethics_responsibility_user` (`user_id`),
  CONSTRAINT `fk_ethics_responsibility_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `participate_conference` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `location` TEXT,
  `type_part` TEXT,
  `place` TEXT,
  `year` VARCHAR(20) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_participate_conference_user` (`user_id`),
  CONSTRAINT `fk_participate_conference_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `questions` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `question_text` TEXT NOT NULL,
  `topic` TEXT NOT NULL,
  `main_slo` TEXT NOT NULL,
  `enabling_slos` TEXT NOT NULL,
  `complexity_level` TEXT NOT NULL,
  `student_level` TEXT NOT NULL,
  `options` TEXT NOT NULL,
  `correct_answer` TEXT NOT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `university_evaluation` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `department_load` INT DEFAULT NULL,
  `workshop_develop` INT DEFAULT NULL,
  `program_bank` INT DEFAULT NULL,
  `medical_services` INT DEFAULT NULL,
  `department_load_Evaluation` INT DEFAULT NULL,
  `workshop_develop_Evaluation` INT DEFAULT NULL,
  `program_bank_Evaluation` INT DEFAULT NULL,
  `medical_services_Evaluation` INT DEFAULT NULL,
  `aspects_sum` INT DEFAULT NULL,
  `evaluation_sum` INT DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `evaluation_year` INT GENERATED ALWAYS AS (YEAR(`created_at`)) STORED,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_university_evaluation_user_year` (`evaluation_year`, `user_id`),
  KEY `idx_university_evaluation_user` (`user_id`),
  CONSTRAINT `fk_university_evaluation_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
