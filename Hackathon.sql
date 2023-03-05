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

-- alter TABLE countries add column date_now date;
-- alter TABLE countries add column time_now time;

SELECT c.name AS country_name,
       cn.name AS continent_name,
       c.population,
       ca.New AS new_cases,
       ca.Active AS active_cases,
       ca.Critical AS critical_cases,
       ca.Recovered AS recovered_cases,
       ca.Total AS total_cases,
       d.New AS new_deaths,
       d.Total AS total_deaths,
       t.total AS total_tests,
	   c.date_now,
       c.time_now
FROM Countries c
JOIN Continents cn ON c.continent_id = cn.id
JOIN Cases ca ON c.id = ca.country_id
JOIN Deaths d ON c.id = d.country_id
JOIN Tests t ON c.id = t.country_id
--where c.name = 'Nigeria';
