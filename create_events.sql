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
