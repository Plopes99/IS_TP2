-- Active: 1705772418513@@localhost@10001@is@public
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";



CREATE TABLE public.categories (
	id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
	category_name   VARCHAR(255) NOT NULL,
	accidents_types VARCHAR(255),
	damage_types    VARCHAR(255),
	created_on      TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_on      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE public.countries(
	id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
	country_name    VARCHAR(250) UNIQUE NOT NULL,
	category_id     uuid,
	created_on      TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_on      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE public.disasters(
	id              uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
	date            DATE,
	geom            JSONB,
    aircraft_type   VARCHAR(255),
    operator        VARCHAR(255),
    fatalities      INT,
    country_id      uuid,
	created_on      TIMESTAMP NOT NULL DEFAULT NOW(),
	updated_on      TIMESTAMP NOT NULL DEFAULT NOW()
);

ALTER TABLE disasters
    ADD CONSTRAINT country_id_FK
        FOREIGN KEY (country_id) REFERENCES countries
            ON DELETE CASCADE;

ALTER TABLE countries
    ADD CONSTRAINT category_id_FK
        FOREIGN KEY (category_id) REFERENCES categories
            ON DELETE SET NULL;


