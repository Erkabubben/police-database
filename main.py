import mysql.connector
from mysql.connector import errorcode
import gui
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
    create_table = "CREATE TABLE `citizens` (" \
                     "  `citizen_id` int(11) NOT NULL," \
                     "  `firstname` varchar(30) NOT NULL," \
                     "  `lastname` varchar(30) NOT NULL," \
                     "  `nationality` varchar(3)," \
                     "  `gender` char(1)," \
                     "  `date_of_birth` int(9)," \
                     "  PRIMARY KEY (`citizen_id`)" \
                     ") ENGINE=InnoDB"
    try_create_table(cursor, create_table)


# Defines a schema and attempts to create a citizens table in the database.
def create_table_offenses(cursor):
    create_table = "CREATE TABLE `offenses` (" \
                     "  `offense_code` varchar(8) NOT NULL," \
                     "  `offense_name` varchar(300) NOT NULL," \
                     "  `offense_class` varchar(30) NOT NULL," \
                     "  PRIMARY KEY (`offense_code`)" \
                     ") ENGINE=InnoDB"
    try_create_table(cursor, create_table)


# Defines a schema and attempts to create a citizens table in the database.
def create_table_convictions(cursor):
    create_table = "CREATE TABLE `convictions` (" \
                     "  `conviction_id` varchar(8) NOT NULL," \
                     "  `convict_id` int(11) NOT NULL," \
                     "  `offense_code` varchar(8) NOT NULL," \
                     "  PRIMARY KEY (`conviction_id`)" \
                     ") ENGINE=InnoDB"
    try_create_table(cursor, create_table)


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


# Runs a list of SQL queries.
def run_insert_queries(queries):
    errors = 0
    for query in queries:
        try:
            #print("SQL query {}: ".format(query), end='')
            cursor.execute(query)
        except mysql.connector.Error as err:
            print(err.msg)
            errors += 1
        else:
            # Make sure data is committed to the database.
            cnx.commit()
            #print("OK")
    print("Errors running insert queries: {}".format(errors))

def OnReadCitizensLine(insert_sql, line, count):
    a = line.split('|')
    insert_sql.append(
        "INSERT INTO citizens (citizen_id, firstname, lastname, nationality, gender, date_of_birth)"
        "VALUES ({}, '{}', '{}', '{}', '{}', {});"
            .format(count - 1, a[0].replace('\'', ' '), a[1].replace('\'', ' '), a[2], a[3], a[4]))


def OnReadOffensesLine(insert_sql, line, count):
    a = line.split('\t')
    insert_sql.append(
        "INSERT INTO offenses (offense_code, offense_name, offense_class)"
        "VALUES ({}, '{}', '{}');".format(a[2].strip(), a[0].strip(), a[1].strip()))


def OnReadConvictionsLine(insert_sql, line, count):
    a = line.split('|')
    insert_sql.append(
        "INSERT INTO convictions (conviction_id, convict_id, offense_code)"
        "VALUES ('{}', '{}', '{}');".format(a[0].strip(), a[1].strip(), a[2].strip()))


def read_txt_data(filepath, operation_id):
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

        #print("Line{}: {}".format(count, line.strip()))

        if operation_id == 0:
            OnReadCitizensLine(insert_sql, line, count)
        elif operation_id == 1:
            OnReadOffensesLine(insert_sql, line, count)
        elif operation_id == 2:
            OnReadConvictionsLine(insert_sql, line, count)

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
    print(columns.format('citizen_id', 'firstname', 'lastname', 'nationality', 'gender', 'date_of_birth'))
    # Print line to separate column names from tuples.
    print("-" * 220)

    # Change null values to 'null' strings before printing.
    for (citizen_id, firstname, lastname, nationality, gender, dayOfBirth) in cursor:
        print(columns.format(citizen_id, firstname, lastname, nationality, gender, dayOfBirth))


# Prints a table of citizens to the console.
def print_offenses(cursor, query):
    cursor.execute(query)
    columns = "| {:<8} | {:<20} | {:<100}"
    # Print column names.
    print(columns.format('offense_code', 'offense_class', 'offense_name'))
    # Print line to separate column names from tuples.
    print("-" * 220)

    # Change null values to 'null' strings before printing.
    for (offense_code, offense_name, offense_class) in cursor:
        print(columns.format(offense_code, offense_class, offense_name))

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

reset_tables = False;

if (reset_tables):
    cursor.execute("DROP TABLE citizens")
    cursor.execute("DROP TABLE offenses")
    cursor.execute("DROP TABLE convictions")

    # Create tables.
    create_table_citizens(cursor)
    create_table_offenses(cursor)
    create_table_convictions(cursor)

    # Read .csv data to lists.
    read_txt_data('population.txt', 0)
    read_txt_data('offenses.txt', 1)
    read_txt_data('convictions.txt', 2)

#for citizen in citizens_list:
#    print("{}, {}, {}, {}, {}, {}".format(citizen[0], citizen[1], citizen[2], citizen[3], citizen[4], citizen[5]))

# Insert data from lists into tables.
print_citizens(cursor, 'SELECT * FROM citizens')
print_offenses(cursor, 'SELECT * FROM offenses')
#print_convictions(cursor, 'SELECT * FROM convictions')

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

gui.display_gui(cursor)
