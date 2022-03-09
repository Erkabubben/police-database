import mysql.connector
from mysql.connector import errorcode

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


# Defines a schema and attempts to create a citizens table in the database.
def create_table_citizens(cursor):
    create_table = "CREATE TABLE `citizens` (" \
                     "  `citizen_id` int(11) NOT NULL," \
                     "  `firstname` varchar(30) NOT NULL," \
                     "  `lastname` varchar(30) NOT NULL," \
                     "  `nationality` varchar(20)," \
                     "  `gender` char(1)," \
                     "  `date_of_birth` int(9)," \
                     "  `total_convictions` int(9)," \
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