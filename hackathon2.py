import http.client
import json
import psycopg2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
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

connection = psycopg2.connect(host=HOSTNAME, user=USERNAME, password=PASSWORD, dbname=DATABASE)
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
        cursor.execute(f"insert into continents (name) values ('{name}') ")
    connection.commit()
    connection.close()

countries = set({})

def get_countries():
    for info in data:
        country = info['country']
        if country is None:
                continue
        countries.add(country)
get_countries()

countries = list(countries)
countries.sort()

def populate_countries():
     for name in countries:
        if name