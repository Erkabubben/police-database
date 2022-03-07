import mysql.connector
from mysql.connector import errorcode
import csv

cnx = mysql.connector.connect(user='root',
                              password='root',
                              host='localhost',
                              port=3306
                              )

DB_NAME = 'policedb'

cursor = cnx.cursor()


# Creates a database with the given name.
def create_database(cursor, DB_NAME):
    try:
        cursor.execute("CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
    except mysql.connector.Error as err:
        print("Failed to create database {}".format(err))
        exit(1)


# Defines a schema and attempts to create a citizens table in the database.
def create_table_citizens(cursor):
    create_citizens = "CREATE TABLE `citizens` (" \
                     "  `ssn` int(11) NOT NULL," \
                     "  `firstname` varchar(30) NOT NULL," \
                     "  `lastname` varchar(30) NOT NULL," \
                     "  `ethnicity` varchar(3)," \
                     "  `gender` char(1)," \
                     "  `dayOfBirth` int(9)," \
                     "  PRIMARY KEY (`ssn`)" \
                     ") ENGINE=InnoDB"
    try_create_table(cursor, create_citizens)


# Defines a schema and attempts to create a species table in the database.
def create_table_species(cursor):
    create_species = "CREATE TABLE `species` (" \
                     "  `name` varchar(30) NOT NULL," \
                     "  `classification` varchar(45)," \
                     "  `designation` varchar(45)," \
                     "  `average_height` int(11)," \
                     "  `skin_colors` varchar(45)," \
                     "  `hair_colors` varchar(45)," \
                     "  `eye_colors` varchar(45)," \
                     "  `average_lifespan` int(11)," \
                     "  `language` varchar(45)," \
                     "  `homeworld` varchar(45)," \
                     "  PRIMARY KEY (`name`)" \
                     ") ENGINE=InnoDB"
    try_create_table(cursor, create_species)


# Attempts to create a table from the given schema query.
def try_create_table(cursor, query):
    try:
        print("Creating table: " + query)
        cursor.execute(query)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("Table already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


# Replaces NA and N/A strings with null values.
def replace_na(str):
    if str == 'NA' or str == 'N/A':
        return 'DEFAULT'
    else:
        return "'" + str + "'"


# Inserts data from a planets list into the planets table.
def insert_into_planets(cursor, planetslist):
    insert_sql = [
        "INSERT INTO planets (name, rotation_period, orbital_period, diameter, climate, gravity, terrain, surface_water, population)"
        "VALUES ('Alderaan', '24', '364', '12500', 'temperate', '1 standard','grasslands, mountains', '40', '2000000000');"
        ]

    insert_sql = []

    for planet in planetslist:
        p = []
        for val in planet:
            p.append(replace_na(val))

        insert_sql.append(
            "INSERT INTO planets (name, rotation_period, orbital_period, diameter, climate, gravity, terrain, surface_water, population)"
            "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {});"
            .format(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8]))

    run_insert_queries(insert_sql)


# Inserts data from a species list into the species table.
def insert_into_species(cursor, specieslist):
    insert_sql = []

    for species in specieslist:
        p = []
        for val in species:
            p.append(replace_na(val))

        insert_sql.append(
            "INSERT INTO species (name, classification, designation, average_height, skin_colors, hair_colors, eye_colors, average_lifespan, language, homeworld)"
            "VALUES ({}, {}, {}, {}, {}, {}, {}, {}, {}, {});"
            .format(p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9]))

    run_insert_queries(insert_sql)


# Runs a list of SQL queries.
def run_insert_queries(queries):
    for query in queries:
        try:
            print("SQL query {}: ".format(query), end='')
            cursor.execute(query)
        except mysql.connector.Error as err:
            print(err.msg)
        else:
            # Make sure data is committed to the database.
            cnx.commit()
            print("OK")


# Reads a .csv file and returns its contents as a list.
def read_csv_to_list(csvpath, delimiter):
    csvlist = []
    with open(csvpath, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter=delimiter, quotechar='"')
        for row in reader:
            if row[0] != 'NA' and row[0] != 'N/A':
                csvlist.append(row)
    return csvlist


# Reads a .csv file and returns its contents as a list.
def read_population_data(filepath, delimiter):
    # Using readline()
    file1 = open(filepath, encoding='utf-8')
    count = 0
    insert_sql = []

    while True:
        count += 1

        # Get next line from file
        line = file1.readline()

        # if line is empty end of file is reached
        if not line:
            break

        print("Line{}: {}".format(count, line.strip()))

        a = line.split('|')
        insert_sql.append(
            "INSERT INTO citizens (ssn, firstname, lastname, ethnicity, gender, dayOfBirth)"
            "VALUES ({}, '{}', '{}', '{}', '{}', {});"
                .format(count - 1, a[0], a[1], a[2], a[3], a[4]))

    file1.close()
    run_insert_queries(insert_sql)



# Replaces a null value with a 'null' string - necessary to prevent errors when printing.
def set_to_null_string(val):
    if val is None:
        return 'null'
    else:
        return val


# Prints a table of citizens to the console.
def print_citizens(cursor, query):
    cursor.execute(query)
    columns = "| {:<9} | {:<25} | {:<25} | {:<4} | {:<4} | {:<10}"
    # Print column names.
    print(columns.format('ssn', 'firstname', 'lastname', 'ethnicity', 'gender', 'dayOfBirth'))
    # Print line to separate column names from tuples.
    print("-" * 220)

    # Change null values to 'null' strings before printing.
    for (ssn, firstname, lastname, ethnicity, gender, dayOfBirth) in cursor:
        print(columns.format(ssn, firstname, lastname, ethnicity, gender, dayOfBirth))


# Prints a table of planets to the console.
def print_planets(cursor, query):
    cursor.execute(query)
    columns = "| {:<15} | {:<15} | {:<15} | {:<8} | {:<25} | {:<40} | {:<42} | {:<15} | {:<15}"
    # Print column names.
    print(columns.format('name', 'rotation_period', 'orbital_period', 'diameter', 'climate', 'gravity', 'terrain',
                         'surface_water', 'population'))
    # Print line to separate column names from tuples.
    print("-" * 220)

    # Change null values to 'null' strings before printing.
    for (
    name, rotation_period, orbital_period, diameter, climate, gravity, terrain, surface_water, population) in cursor:
        name = set_to_null_string(name)
        rotation_period = set_to_null_string(rotation_period)
        orbital_period = set_to_null_string(orbital_period)
        diameter = set_to_null_string(diameter)
        climate = set_to_null_string(climate)
        gravity = set_to_null_string(gravity)
        terrain = set_to_null_string(terrain)
        surface_water = set_to_null_string(surface_water)
        population = set_to_null_string(population)
        print(columns.format(name, rotation_period, orbital_period, diameter, climate, gravity, terrain, surface_water,
                             population))


# Prints a table of species to the console.
def print_species(cursor, query):
    cursor.execute(query)
    columns = "| {:<15} | {:<15} | {:<15} | {:<15} | {:<40} | {:<35} | {:<42} | {:<17} | {:<15} | {:<15}"
    # Print column names.
    print(columns.format('name', 'classification', 'designation', 'average_height', 'skin_colors', 'hair_colors',
                         'eye_colors', 'average_lifespan', 'language', 'homeworld'))
    # Print line to separate column names from tuples.
    print("-" * 270)

    # Change null values to 'null' strings before printing.
    for (
    name, classification, designation, average_height, skin_colors, hair_colors, eye_colors, average_lifespan, language,
    homeworld) in cursor:
        name = set_to_null_string(name)
        classification = set_to_null_string(classification)
        designation = set_to_null_string(designation)
        average_height = set_to_null_string(average_height)
        skin_colors = set_to_null_string(skin_colors)
        hair_colors = set_to_null_string(hair_colors)
        eye_colors = set_to_null_string(eye_colors)
        average_lifespan = set_to_null_string(average_lifespan)
        language = set_to_null_string(language)
        homeworld = set_to_null_string(homeworld)
        print(columns.format(name, classification, designation, average_height, skin_colors, hair_colors, eye_colors,
                             average_lifespan, language, homeworld))


# Prints the main menu.
def print_menu():
    print("1. List all planets.")
    print("2. Search for planet details.")
    print("3. Search for species with height higher than given number.")
    print("4. What is the most likely desired climate of the given species?")
    print("5. What is the average lifespan per species classification?")
    print("Q. Quit")
    print("----------")
    print("Please choose one option:")


# Attempts to set the database and creates a new one if none exists.
try:
    cursor.execute("USE {}".format(DB_NAME))
except mysql.connector.Error as err:
    print("Database {} does not exist".format(DB_NAME))
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        create_database(cursor, DB_NAME)
        print("Database {} created successfully.".format(DB_NAME))
        cnx.database = DB_NAME
    else:
        print(err)

cursor.execute("DROP TABLE citizens")

# Create tables.
create_table_citizens(cursor)
#create_table_species(cursor)

# Read .csv data to lists.
read_population_data('population.txt', '|')
#specieslist = read_csv_to_list('species.csv')

#for citizen in citizens_list:
#    print("{}, {}, {}, {}, {}, {}".format(citizen[0], citizen[1], citizen[2], citizen[3], citizen[4], citizen[5]))

# Insert data from lists into tables.
#insert_into_planets(cursor, planetslist)
#insert_into_species(cursor, specieslist)

print_citizens(cursor, 'SELECT * FROM citizens')
# print_species(cursor, 'SELECT * FROM species')

# Display menu until user enters 'Q'
print('')
selected = 'Q'
while selected != 'Q':
    #print_menu()
    #selected = input()
    # User selects option 1: List all planets.
    if selected == '1':
        print_planets(cursor, 'SELECT * FROM planets')
    # User selects option 2: Search for planet details.
    if selected == '2':
        print('Enter planet name:')
        planetname = input()
        print_planets(cursor, "SELECT * FROM planets WHERE name = '{}'".format(planetname))
        input()
    # User selects option 3: Search for species with height higher than given number.
    if selected == '3':
        print('Enter species height:')
        height = input()
        try:
            height = int(height)
            print_species(cursor, "SELECT * FROM species WHERE average_height > {}".format(height))
            input()
        except Exception as err:
            print('Incorrect input - height must be a number.')
    # User selects option 4: What is the most likely desired climate of the given species?
    if selected == '4':
        print('Enter species name:')
        speciesname = input()
        cursor.execute("SELECT climate FROM planets, species WHERE planets.name = species.homeworld AND species.name = '{}'".format(speciesname))
        for row in cursor:
            if isinstance(row[0], str):
                print('Preferred climate: ' + row[0])
                input()
    # User selects option 5: What is the average lifespan per species classification??
    if selected == '5':
        # Get a list of all classifications in the species table.
        cursor.execute("SELECT classification FROM species")
        classifications = []
        for row in cursor:
            if not row[0] in classifications:
                classifications.append(row[0])
        # Loop through the classifications list and display average lifespan.
        for classification in classifications:
            cursor.execute(
                "SELECT AVG(average_lifespan) FROM species WHERE classification = '{}'".format(classification))
            for r in cursor:
                if not r[0] is None:
                    print(classification + ': ' + str(r[0]))
        # Await user input before proceeding.
        input()
    # Always print a blank line before re-printing menu.
    print('')
