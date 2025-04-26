BEGIN;
--
-- Create model User
--
CREATE TABLE "accounts_user" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "password" varchar(128) NOT NULL, "last_login" datetime NULL, "is_superuser" bool NOT NULL, "username" varchar(150) NOT NULL UNIQUE, "first_name" varchar(150) NOT NULL, "last_name" varchar(150) NOT NULL, "email" varchar(254) NOT NULL, "is_staff" bool NOT NULL, "is_active" bool NOT NULL, "date_joined" datetime NOT NULL, "user_type" varchar(20) NOT NULL, "phone_number" varchar(20) NULL, "profile_picture" varchar(100) NULL);
CREATE TABLE "accounts_user_groups" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED, "group_id" integer NOT NULL REFERENCES "auth_group" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE "accounts_user_user_permissions" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "user_id" bigint NOT NULL REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED, "permission_id" integer NOT NULL REFERENCES "auth_permission" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "accounts_user_groups_user_id_group_id_59c0b32f_uniq" ON "accounts_user_groups" ("user_id", "group_id");
CREATE INDEX "accounts_user_groups_user_id_52b62117" ON "accounts_user_groups" ("user_id");
CREATE INDEX "accounts_user_groups_group_id_bd11a704" ON "accounts_user_groups" ("group_id");
CREATE UNIQUE INDEX "accounts_user_user_permissions_user_id_permission_id_2ab516c2_uniq" ON "accounts_user_user_permissions" ("user_id", "permission_id");
CREATE INDEX "accounts_user_user_permissions_user_id_e4f0a161" ON "accounts_user_user_permissions" ("user_id");
CREATE INDEX "accounts_user_user_permissions_permission_id_113bb443" ON "accounts_user_user_permissions" ("permission_id");
COMMIT;
BEGIN;
--
-- Create model Category
--
CREATE TABLE "events_category" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "gender" varchar(1) NOT NULL, "min_age" smallint unsigned NOT NULL CHECK ("min_age" >= 0), "max_age" smallint unsigned NOT NULL CHECK ("max_age" >= 0), "description" text NOT NULL);
--
-- Create model Event
--
CREATE TABLE "events_event" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(255) NOT NULL, "slug" varchar(255) NOT NULL UNIQUE, "description" text NOT NULL, "location" varchar(255) NOT NULL, "start_date" date NOT NULL, "end_date" date NOT NULL, "rules" text NOT NULL, "registration_start" datetime NOT NULL, "registration_end" datetime NOT NULL, "required_documents" text NOT NULL CHECK ((JSON_VALID("required_documents") OR "required_documents" IS NULL)), "required_vaccines" text NOT NULL CHECK ((JSON_VALID("required_vaccines") OR "required_vaccines" IS NULL)), "status" varchar(20) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL);
--
-- Create model Modality
--
CREATE TABLE "events_modality" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "description" text NOT NULL);
--
-- Create model PenaltyType
--
CREATE TABLE "events_penaltytype" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "description" text NOT NULL, "time_penalty" bigint NULL, "is_disqualification" bool NOT NULL);
--
-- Create model Race
--
CREATE TABLE "events_race" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(255) NOT NULL, "distance" decimal NOT NULL, "description" text NOT NULL, "start_type" varchar(10) NOT NULL, "participants_per_interval" smallint unsigned NOT NULL CHECK ("participants_per_interval" >= 0), "interval_seconds" smallint unsigned NOT NULL CHECK ("interval_seconds" >= 0), "max_participants" integer unsigned NOT NULL CHECK ("max_participants" >= 0), "race_date" date NOT NULL, "race_time" time NOT NULL, "actual_start_time" datetime NULL, "event_id" bigint NOT NULL REFERENCES "events_event" ("id") DEFERRABLE INITIALLY DEFERRED, "modality_id" bigint NOT NULL REFERENCES "events_modality" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model RaceCategory
--
CREATE TABLE "events_racecategory" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "price" decimal NOT NULL, "quota" integer unsigned NOT NULL CHECK ("quota" >= 0), "category_id" bigint NOT NULL REFERENCES "events_category" ("id") DEFERRABLE INITIALLY DEFERRED, "race_id" bigint NOT NULL REFERENCES "events_race" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "events_race_event_id_3ec775f3" ON "events_race" ("event_id");
CREATE INDEX "events_race_modality_id_b8639d9c" ON "events_race" ("modality_id");
CREATE UNIQUE INDEX "events_racecategory_race_id_category_id_0cd10fea_uniq" ON "events_racecategory" ("race_id", "category_id");
CREATE INDEX "events_racecategory_category_id_1e549310" ON "events_racecategory" ("category_id");
CREATE INDEX "events_racecategory_race_id_a88ffc90" ON "events_racecategory" ("race_id");
COMMIT;
BEGIN;
--
-- Create model Participant
--
CREATE TABLE "participants_participant" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "first_name" varchar(100) NOT NULL, "last_name" varchar(100) NOT NULL, "id_document" varchar(20) NOT NULL, "date_of_birth" date NOT NULL, "gender" varchar(1) NOT NULL, "email" varchar(254) NOT NULL, "phone" varchar(20) NOT NULL, "address" varchar(255) NOT NULL, "city" varchar(100) NOT NULL, "state_province" varchar(100) NOT NULL, "country" varchar(100) NOT NULL, "postal_code" varchar(20) NOT NULL, "club" varchar(100) NOT NULL, "emergency_contact_name" varchar(200) NOT NULL, "emergency_contact_phone" varchar(20) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "user_id" bigint NULL UNIQUE REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Dog
--
CREATE TABLE "participants_dog" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(100) NOT NULL, "breed" varchar(100) NOT NULL, "date_of_birth" date NULL, "gender" varchar(1) NOT NULL, "microchip_number" varchar(100) NOT NULL, "veterinary_book_number" varchar(100) NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "owner_id" bigint NOT NULL REFERENCES "participants_participant" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "participants_dog_owner_id_63959766" ON "participants_dog" ("owner_id");
COMMIT;
BEGIN;
--
-- Create model Registration
--
CREATE TABLE "registrations_registration" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "bib_number" integer unsigned NULL CHECK ("bib_number" >= 0), "registration_status" varchar(20) NOT NULL, "payment_status" varchar(20) NOT NULL, "payment_method" varchar(50) NOT NULL, "payment_reference" varchar(100) NOT NULL, "ai_vaccine_status" varchar(20) NOT NULL, "vet_check_status" varchar(20) NOT NULL, "vet_check_time" datetime NULL, "vet_checker_details" text NOT NULL, "kit_delivered" bool NOT NULL, "kit_delivery_time" datetime NULL, "checked_in" bool NOT NULL, "checkin_time" datetime NULL, "notes" text NOT NULL, "waiver_accepted" bool NOT NULL, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "dog_id" bigint NOT NULL REFERENCES "participants_dog" ("id") DEFERRABLE INITIALLY DEFERRED, "participant_id" bigint NOT NULL REFERENCES "participants_participant" ("id") DEFERRABLE INITIALLY DEFERRED, "race_id" bigint NOT NULL REFERENCES "events_race" ("id") DEFERRABLE INITIALLY DEFERRED, "race_category_id" bigint NOT NULL REFERENCES "events_racecategory" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ParticipantAnnotation
--
CREATE TABLE "registrations_participantannotation" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "status" varchar(20) NOT NULL, "notes" text NOT NULL, "location" varchar(100) NOT NULL, "recorded_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "confirmed_by_id" bigint NULL REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED, "penalty_type_id" bigint NOT NULL REFERENCES "events_penaltytype" ("id") DEFERRABLE INITIALLY DEFERRED, "recorded_by_id" bigint NOT NULL REFERENCES "accounts_user" ("id") DEFERRABLE INITIALLY DEFERRED, "registration_id" bigint NOT NULL REFERENCES "registrations_registration" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Document
--
CREATE TABLE "registrations_document" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "document_type" varchar(50) NOT NULL, "file" varchar(100) NOT NULL, "description" varchar(255) NOT NULL, "ocr_raw_text" text NOT NULL, "ocr_status" varchar(20) NOT NULL, "ocr_analysis_result" text NOT NULL CHECK ((JSON_VALID("ocr_analysis_result") OR "ocr_analysis_result" IS NULL)), "uploaded_at" datetime NOT NULL, "registration_id" bigint NOT NULL REFERENCES "registrations_registration" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX "registrations_registration_race_id_bib_number_f59f4f6c_uniq" ON "registrations_registration" ("race_id", "bib_number");
CREATE INDEX "registrations_registration_dog_id_984f76c5" ON "registrations_registration" ("dog_id");
CREATE INDEX "registrations_registration_participant_id_eb34944f" ON "registrations_registration" ("participant_id");
CREATE INDEX "registrations_registration_race_id_24787062" ON "registrations_registration" ("race_id");
CREATE INDEX "registrations_registration_race_category_id_3334deee" ON "registrations_registration" ("race_category_id");
CREATE INDEX "registrations_participantannotation_confirmed_by_id_18d405e5" ON "registrations_participantannotation" ("confirmed_by_id");
CREATE INDEX "registrations_participantannotation_penalty_type_id_d3fa7212" ON "registrations_participantannotation" ("penalty_type_id");
CREATE INDEX "registrations_participantannotation_recorded_by_id_cdfbdf84" ON "registrations_participantannotation" ("recorded_by_id");
CREATE INDEX "registrations_participantannotation_registration_id_756c8521" ON "registrations_participantannotation" ("registration_id");
CREATE INDEX "registrations_document_registration_id_cefacdab" ON "registrations_document" ("registration_id");
COMMIT;
BEGIN;
--
-- Create model RaceResult
--
CREATE TABLE "results_raceresult" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "start_time" datetime NULL, "finish_time" datetime NULL, "base_time" bigint NULL, "official_time" bigint NULL, "status" varchar(20) NOT NULL, "overall_rank" integer unsigned NULL CHECK ("overall_rank" >= 0), "modality_rank" integer unsigned NULL CHECK ("modality_rank" >= 0), "category_rank" integer unsigned NULL CHECK ("category_rank" >= 0), "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "registration_id" bigint NOT NULL UNIQUE REFERENCES "registrations_registration" ("id") DEFERRABLE INITIALLY DEFERRED);
COMMIT;
