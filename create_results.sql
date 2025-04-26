BEGIN;
--
-- Create model RaceResult
--
CREATE TABLE "results_raceresult" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "start_time" datetime NULL, "finish_time" datetime NULL, "base_time" bigint NULL, "official_time" bigint NULL, "status" varchar(20) NOT NULL, "overall_rank" integer unsigned NULL CHECK ("overall_rank" >= 0), "modality_rank" integer unsigned NULL CHECK ("modality_rank" >= 0), "category_rank" integer unsigned NULL CHECK ("category_rank" >= 0), "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "registration_id" bigint NOT NULL UNIQUE REFERENCES "registrations_registration" ("id") DEFERRABLE INITIALLY DEFERRED);
COMMIT;
