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
