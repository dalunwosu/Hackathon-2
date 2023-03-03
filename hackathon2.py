import http.client
import json
import psycopg2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import time
from datetime import datetime

conn = http.client.HTTPSConnection("covid-193.p.rapidapi.com")
headers = {
    'X-RapidAPI-Key': "f5f1a9c5b0msh646ff2a97d048ccp16a068jsna1f5daf62d31",
    'X-RapidAPI-Host': "covid-193.p.rapidapi.com"
}
conn.request("GET", "/statistics", headers=headers)
res = conn.getresponse()
data = res.read()
json_data = json.loads(data.decode("utf-8"))
data = json_data['response']

USERNAME = "postgres"
PASSWORD = "daza"
DATABASE = "Hackathon-2"
HOSTNAME = "localhost"

connection = psycopg2.connect(
    host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
cursor = connection.cursor()

continents = set({})


def get_continents():
    for info in data:
        continent = info['continent']
        if continent is None:
            continue
        continents.add(continent)


get_continents()

continents = list(continents)
continents.sort()


def populate_continents():
    for name in continents:
        cursor.execute(f"insert into continents (name) values ('{name}'); ")
    connection.commit()


def continent_id(continent_name: str) -> int:
    query = f"select id from continents where name = '{continent_name}'"

    cursor.execute(query)
    id = cursor.fetchall()
    if len(id) == 0:
        return None

    id = id[0][0]
    return id


countries = set({})


def get_countries():
    for info in data:
        continent = info['continent']
        cont_id = continent_id(continent)
        country = info['country']
        population = info['population']
        date = info['day']
        time = info['time']
        time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S+00:00')
        time = time.strftime('%H:%M:%S')
        if country is None:
            continue
        if population is None:
            population = 0
        countries.add((country, cont_id, population,date,time))


get_countries()

countries = list(countries)
countries.sort(key=lambda t: t[0])


def populate_countries():
    for name_contid in countries:
        if name_contid[1] is None:
            continue
        query = f"insert into countries(name, continent_id, population,date_now,time_now) values ('{name_contid[0]}', {name_contid[1]}, {name_contid[2]},'{name_contid[3]}','{name_contid[4]}');"
        cursor.execute(query)
    connection.commit()


def country_id(country_name):
    query = f"select id from countries where name = '{country_name}'"
    cursor.execute(query)
    id = cursor.fetchall()
    if len(id) == 0:
        return None
    id = id[0][0]
    return id


cases = {}


def get_cases():
    for info in data:
        country = info['country']
        con_id = country_id(country)
        cases[con_id] = {
            "New": info["cases"]["new"],
            "Active": info["cases"]["active"],
            "Critical": info["cases"]["critical"],
            "Recovered": info["cases"]["recovered"],
            "Total": info["cases"]["total"]
        }


get_cases()
cases = {k: {k2: v2 if v2 is not None else 0 for k2, v2 in v.items()}
         for k, v in cases.items()}
cases = {k: v for k, v in cases.items() if k is not None}
cases = sorted(cases.items(), key=lambda x: x[0])


def populate_cases():
    for case in cases:
        query = f"insert into cases (new,active,critical,recovered,total,country_id) values ({case[1]['New']},{case[1]['Active']},{case[1]['Critical']},{case[1]['Recovered']},{case[1]['Total']},{case[0]});"
        cursor.execute(query)
    connection.commit()


deaths = {}


def get_deaths():
    for info in data:
        country = info['country']
        con_id = country_id(country)
        deaths[con_id] = {
            "new": info['deaths']['new'],
            "total": info['deaths']['total']
        }


get_deaths()

deaths = {k: {k2: v2 if v2 is not None else 0 for k2, v2 in v.items()}
          for k, v in deaths.items()}
deaths = {k: v for k, v in deaths.items() if k is not None}
deaths = sorted(deaths.items(), key=lambda x: x[0])


def populate_deaths():
    for death in deaths:
        query = f"insert into deaths (new,total,country_id) values ({death[1]['new']},{death[1]['total']},{death[0]})"
        cursor.execute(query)
    connection.commit()

tests = {}

def get_tests():
    for info in data:
        country = info['country']
        con_id = country_id(country)
        tests[con_id] = {
            "total": info['tests']['total']
        }
get_tests()

tests = {k: {k2: v2 if v2 is not None else 0 for k2, v2 in v.items()}
          for k, v in tests.items()}
tests = {k: v for k, v in tests.items() if k is not None}
tests = sorted(tests.items(), key=lambda x: x[0])



def populate_tests():
    for test in tests:
        query = f"insert into tests (total,country_id) values ({test[1]['total']},{test[0]})"
        cursor.execute(query)
    connection.commit()

def update_table():
    query = f"TRUNCATE TABLE continents RESTART IDENTITY CASCADE"
    cursor.execute(query)
    connection.commit()
    populate_continents()
    populate_countries()
    populate_cases()
    populate_deaths()
    populate_tests()

update_table()