-- create table Continents(
-- 	id serial primary key,
-- 	name varchar(50)
-- );

-- create table Countries(
-- 	id serial primary key,
-- 	name varchar(100),
-- 	population int,
-- 	continent_id int,
-- 	FOREIGN KEY (continent_id) REFERENCES Continents (id)
-- );

-- create table Cases(
-- 	id serial primary key,
-- 	New int,
-- 	Active int,
-- 	Critical int,
-- 	Recovered int,
-- 	Total int,
-- 	country_id int,
-- 	FOREIGN KEY (country_id) REFERENCES Countries (id)
-- );

-- create table deaths( 
-- 	id serial primary key,
-- 	new int,
-- 	total INT,
-- 	country_id int,
--  	FOREIGN KEY (country_id) REFERENCES Countries (id)
-- );

-- create table tests(
-- 	id serial primary key,
-- 	total INT,
-- 	country_id int,
--  	FOREIGN KEY (country_id) REFERENCES Countries (id)
-- );

alter TABLE countries add column date_now date;
alter TABLE countries add column time_now time;
