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

def get_country():
    name = input("Input your Country of choice: ")
    query = f"SELECT c.name AS country_name, cn.name AS continent_name, c.population, ca.New AS new_cases, ca.Active AS active_cases, ca.Critical AS critical_cases, ca.Recovered AS recovered_cases, ca.Total AS total_cases, d.New AS new_deaths, d.Total AS total_deaths, t.total AS total_tests, c.date_now, c.time_now FROM Countries c JOIN Continents cn ON c.continent_id = cn.id JOIN Cases ca ON c.id = ca.country_id JOIN Deaths d ON c.id = d.country_id JOIN Tests t ON c.id = t.country_id where c.name = '{name}';"
    cursor.execute(query)
    results = cursor.fetchall()
    print(results)


def update_table():
    query = f"TRUNCATE TABLE continents RESTART IDENTITY CASCADE"
    cursor.execute(query)
    connection.commit()
    populate_continents()
    populate_countries()
    populate_cases()
    populate_deaths()
    populate_tests()
    get_country()


update_table()



# GRAPHICAL REPRESENTATION
def case_table():
    continent_query = "SELECT cnt.name as continent_name, SUM(ca.Total) AS total_cases FROM Countries c \
                       JOIN Continents cnt ON c.continent_id = cnt.id \
                       JOIN Cases ca ON c.id = ca.country_id \
                       GROUP BY cnt.name"
    continent_df = pd.read_sql(continent_query, connection)

    plt.bar(continent_df['continent_name'], continent_df['total_cases'])
    plt.title('COVID Cases by Continent')
    plt.xlabel('Continent')
    plt.ylabel('Total Cases')
    plt.show()


# Function to plot bar chart of total cases by country
def plot_cases_by_country(connection):
    query = '''
        SELECT c.name AS country, SUM(cases.total) AS total_cases
        FROM countries c
        JOIN cases ON c.id = cases.country_id
        GROUP BY c.name
        ORDER BY total_cases DESC
        LIMIT 10
    '''
    df = pd.read_sql_query(query, connection)
    plt.bar(df['country'], df['total_cases'], color='cornflowerblue')
    plt.title('Total Cases by Country (Top 10)')
    plt.xlabel('Country')
    plt.xticks(rotation=45)
    plt.ylabel('Total Cases')
    plt.show()

# Function to plot scatter plot of deaths vs cases by continent
def plot_deaths_vs_cases_by_continent(connection):
    query = '''
        SELECT cont.name AS continent, SUM(cases.total) AS total_cases, SUM(deaths.total) AS total_deaths
        FROM continents cont
        JOIN countries c ON cont.id = c.continent_id
        JOIN cases ON c.id = cases.country_id
        JOIN deaths ON c.id = deaths.country_id
        GROUP BY cont.name
    '''
    df = pd.read_sql_query(query, connection)
    plt.scatter(df['total_cases'], df['total_deaths'], s=150, alpha=0.7, color='tomato')
    for i, txt in enumerate(df['continent']):
        plt.annotate(txt, (df['total_cases'][i], df['total_deaths'][i]))
    plt.title('Deaths vs Cases by Continent')
    plt.xlabel('Total Cases')
    plt.ylabel('Total Deaths')
    plt.show()

# Function to plot pie chart of active cases by continent
def plot_active_cases_by_continent(connection):
    query = '''
        SELECT cont.name AS continent, SUM(cases.active) AS active_cases
        FROM continents cont
        JOIN countries c ON cont.id = c.continent_id
        JOIN cases ON c.id = cases.country_id
        GROUP BY cont.name
    '''
    df = pd.read_sql_query(query, connection)
    plt.pie(df['active_cases'], labels=df['continent'], autopct='%1.1f%%', startangle=90, colors=['gold', 'lightgreen', 'pink', 'lightblue'])
    plt.title('Active Cases by Continent')
    plt.axis('equal')
    plt.show()

# Function to plot line graph of new cases by day for a country
def plot_new_cases_by_day(connection, country_name):
    query = f'''
        SELECT date_now AS day, New AS new_cases
        FROM countries c
        JOIN cases ON c.id = cases.country_id
        WHERE c.name = '{country_name}'
        ORDER BY day
    '''
    df = pd.read_sql_query(query, connection)
    plt.plot(df['day'], df['new_cases'], color='purple')
    plt.title(f'New Cases by Day for {country_name}')
    plt.xlabel('Day')
    plt.xticks(rotation=45)
    plt.ylabel('New Cases')
    plt.show()

def scatterplot_new_cases_deaths_by_country(connection):
    query = """
    SELECT c.name AS country_name, Cases.New AS new_cases, deaths.new AS new_deaths
    FROM Countries c
    JOIN Cases ON c.id = Cases.country_id
    JOIN deaths ON c.id = deaths.country_id
    """
    df = pd.read_sql_query(query, connection)

    plt.scatter(df['new_cases'], df['new_deaths'], alpha=0.5)
    plt.xlabel('New Cases')
    plt.ylabel('New Deaths')
    plt.title('New Cases vs New Deaths by Country')
    plt.show()

def barplot_total_tests_per_continent(connection):
    query = """
    SELECT c.name AS continent_name, SUM(tests.total) AS total_tests
    FROM Continents c
    JOIN Countries ON c.id = Countries.continent_id
    JOIN tests ON Countries.id = tests.country_id
    GROUP BY c.name
    """
    df = pd.read_sql_query(query, connection)

    plt.bar(df['continent_name'], df['total_tests'], color=['green', 'red', 'blue', 'purple', 'orange', 'brown'])
    plt.xticks(rotation=45)
    plt.xlabel('Continent')
    plt.ylabel('Total Tests')
    plt.title('Total COVID-19 Tests per Continent')
    plt.show()

def piechart_active_cases_by_continent(connection):
    query = """
    SELECT c.name AS continent_name, SUM(Cases.Active) AS active_cases
    FROM Continents c
    JOIN Countries ON c.id = Countries.continent_id
    JOIN Cases ON Countries.id = Cases.country_id
    GROUP BY c.name
    """
    df = pd.read_sql_query(query, connection)

    plt.pie(df['active_cases'], labels=df['continent_name'], autopct='%1.1f%%', startangle=90)
    plt.axis('equal')
    plt.title('Active COVID-19 Cases by Continent')
    plt.show()

def lineplot_new_cases_over_time_by_country(connection, country_name):
    query = """
    SELECT countries.date_now, Cases.New AS new_cases
    FROM Cases
    JOIN Countries ON Cases.country_id = Countries.id
    WHERE Countries.name = '{}'
    """.format(country_name)
    df = pd.read_sql_query(query, connection)

    plt.plot(df['date_now'], df['new_cases'])
    plt.xticks(rotation=45)
    plt.xlabel('Date')
    plt.ylabel('New Cases')
    plt.title('New COVID-19 Cases over Time for {}'.format(country_name))
    plt.show()

def deaths_by_country(connection):
    """
    Plots a bar chart of the total deaths by country
    
    Parameters:
    connection: psycopg2.extensions.connection
                A psycopg2 connection to a PostgreSQL database
    
    Returns:
    None
    """
    # Create a cursor object
    cur = connection.cursor()
    
    # Execute the query to get total deaths by country
    cur.execute("""
                SELECT c.name, SUM(d.total) as total_deaths
                FROM countries c
                JOIN deaths d ON c.id = d.country_id
                GROUP BY c.name
                ORDER BY total_deaths DESC
                LIMIT 10;
                """)
    
    # Fetch the results
    results = cur.fetchall()
    
    # Close the cursor
    cur.close()
    
    # Extract the country names and total deaths into separate lists
    countries = [result[0] for result in results]
    total_deaths = [result[1] for result in results]
    
    # Plot the bar chart
    plt.bar(countries, total_deaths, color='red')
    plt.title("Total Deaths by Country")
    plt.xlabel("Country")
    plt.ylabel("Total Deaths")
    plt.xticks(rotation=90)
    plt.show()

def stackedbarplot_total_cases_deaths_by_country(connection):
    query = """
    SELECT
        countries.name AS name,
        SUM(cases.total) AS total_cases,
        SUM(deaths.total) AS total_deaths
    FROM
        cases
        JOIN countries ON cases.country_id = countries.id
    GROUP BY
        countries.name
    ORDER BY
        total_cases DESC
    """
    df = pd.read_sql(query, connection)
    
    fig, ax = plt.subplots(figsize=(20, 10))

    totals = df['total'].values.ravel()
    
    ax.bar(df['name'], totals, label='Total Cases')
    ax.bar(df['name'], df['total_deaths'], bottom=totals, label='Total Deaths')

    ax.set_ylabel('Cases')
    ax.set_title('Total Cases and Deaths by Country')
    ax.legend()

    plt.xticks(rotation=90)

    plt.show()

country_name = input("Give your desired country: ")

case_table()
plot_cases_by_country(connection)
plot_deaths_vs_cases_by_continent(connection)
plot_active_cases_by_continent(connection)
plot_new_cases_by_day(connection, country_name)
scatterplot_new_cases_deaths_by_country(connection)
barplot_total_tests_per_continent(connection)
piechart_active_cases_by_continent(connection)
lineplot_new_cases_over_time_by_country(connection,country_name)
deaths_by_country(connection)
stackedbarplot_total_cases_deaths_by_country(connection)

