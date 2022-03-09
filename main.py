import mysql.connector
from mysql.connector import errorcode
import gui
import tables
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
    tables.create_table_citizens(cursor)
    tables.create_table_offenses(cursor)
    tables.create_table_convictions(cursor)

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


gui.display_gui(cursor)
