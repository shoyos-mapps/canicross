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
