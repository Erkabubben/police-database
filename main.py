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


# Appends a citizen Insert command to the insert_sql list.
def on_read_citizens_line(insert_sql, line, count):
    a = line.split('|')
    insert_sql.append(
        "INSERT INTO citizens (citizen_id, firstname, lastname, nationality, gender, year_of_birth, total_convictions)"
        "VALUES ({}, '{}', '{}', '{}', '{}', {}, {});"
            .format(count - 1, a[0].replace('\'', ' '), a[1].replace('\'', ' '), a[2], a[3], a[4], a[5]))


# Appends an offense Insert command to the insert_sql list.
def on_read_offenses_line(insert_sql, line):
    a = line.split('\t')
    insert_sql.append(
        "INSERT INTO offenses (offense_code, offense_name, offense_class)"
        "VALUES ({}, '{}', '{}');".format(a[2].strip(), a[0].strip(), a[1].strip()))


# Appends a conviction Insert command to the insert_sql list.
def on_read_convictions_line(insert_sql, line):
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

        # Get next line from file.
        line = file1.readline()

        # If line is empty end of file is reached.
        if not line:
            break

        # Append new Insert command to insert_sql list depending on selected operation.
        if operation_id == 0:
            on_read_citizens_line(insert_sql, line, count)
        elif operation_id == 1:
            on_read_offenses_line(insert_sql, line)
        elif operation_id == 2:
            on_read_convictions_line(insert_sql, line)

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
    # Print column names.
    print(tables.citizen_columns.format(
        'id', 'firstname', 'lastname', 'nationality', 'gender', 'year_of_birth', 'total_convictions'))
    # Print line to separate column names from tuples.
    print("-" * 220)
    for (citizen_id, firstname, lastname, nationality, gender, year_of_birth, total_convictions) in cursor:
        print(tables.citizen_columns.format(
            citizen_id, firstname, lastname, nationality, gender, year_of_birth, total_convictions))


# Prints a table of offenses to the console.
def print_offenses(cursor, query):
    cursor.execute(query)
    # Print column names.
    print(tables.offense_columns.format('offense_code', 'offense_class', 'offense_name'))
    # Print line to separate column names from tuples.
    print("-" * 220)
    for (offense_code, offense_name, offense_class) in cursor:
        print(tables.offense_columns.format(offense_code, offense_class, offense_name))


# Prints a table of convictions to the console.
def print_convictions(cursor, query):
    cursor.execute(query)
    # Print column names.
    columns = "| {:<8} | {:<8} | {:<16}"
    print(columns.format('conviction_id', 'convict_id', 'offense_code'))
    # Print line to separate column names from tuples.
    print("-" * 220)
    for (conviction_id, convict_id, offense_code) in cursor:
        print(columns.format(conviction_id, convict_id, offense_code))


# Resets tables and views and parses and adds data to the new tables.
def reset_tables(cursor):
    cursor.execute("DROP TABLE IF EXISTS citizens")
    cursor.execute("DROP TABLE IF EXISTS offenses")
    cursor.execute("DROP TABLE IF EXISTS convictions")

    # Create tables.
    tables.create_table_citizens(cursor)
    tables.create_table_offenses(cursor)
    tables.create_table_convictions(cursor)

    # Read .csv data to lists.
    read_txt_data('population.txt', 0)
    read_txt_data('offenses.txt', 1)
    read_txt_data('convictions.txt', 2)

    # Create Views
    cursor.execute('DROP VIEW IF EXISTS top_offenders')
    cursor.execute("CREATE VIEW top_offenders AS SELECT * FROM citizens ORDER BY total_convictions DESC LIMIT 10")
    cursor.execute('DROP VIEW IF EXISTS top_offenses')
    cursor.execute("CREATE VIEW top_offenses AS SELECT convictions.offense_code, count(convictions.offense_code)"
                   "AS total FROM convictions GROUP BY offense_code ORDER BY total DESC LIMIT 10")


# Print data from tables to console to check that tuples have been added successfully.
def print_tables_to_console(cursor):
    print_citizens(cursor, 'SELECT * FROM citizens')
    print_offenses(cursor, 'SELECT * FROM offenses')
    print_convictions(cursor, 'SELECT * FROM convictions')


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

if True:
    reset_tables(cursor)

if False:
    print_tables_to_console(cursor)

gui.display_gui(cursor)
