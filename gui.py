import PySimpleGUI as sg
import tables

current_year = 2022
table_font = 'Courier New'
table_font_size = 10
inputs_width = 120


# Called from Main file to display PySimpleGUI window.
def display_gui(cursor):
    #sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside the window.
    layout = [[sg.Text('ID'), sg.InputText(key='id_input', size=(11)),
               sg.Text('Firstname'), sg.InputText(key='firstname_input', size=(20)),
               sg.Text('Lastname'), sg.InputText(key='lastname_input', size=(20))],
              [sg.Text('Nationality'), sg.InputText(key='nationality_input', size=(20)),
                 sg.Radio('All', "gender_input", default=True, key='gender_input_all'),
                 sg.Radio('Male', "gender_input", key='gender_input_m'),
                 sg.Radio('Female', "gender_input", key='gender_input_f'),
               sg.Text('Age'), sg.InputText(key='min_age_input', size=(3)),
               sg.Text(' to '), sg.InputText(key='max_age_input', size=(3))
              ],
              [sg.Text('Convicted for offense')],
              [sg.Combo(key='offense_list', font=(table_font, table_font_size),
                        values=list_offenses(cursor, 'SELECT * FROM offenses'),
                        size=(inputs_width, 20))],
              [sg.Button('Search')],
              [sg.Text(tables.citizen_columns.format('ID', 'Firstname', 'Lastname', 'Nationality', 'Gender', 'Year of Birth', 'Convictions'), font=(table_font, table_font_size))],
              [sg.Listbox(key='results', enable_events=True, font=(table_font, table_font_size), values=[], size=(inputs_width, 20))],
              [sg.Text('', key='agg_bar', font=(table_font, table_font_size))],
              [sg.Text('Selected citizen')],
              [sg.Multiline(key='selected_citizen_data', font=(table_font, table_font_size), size=(inputs_width, 20))],
              [sg.Button('Exit'), sg.Button('Top Offenders'), sg.Button('Top Offenses')]]

    # Create the Window.
    window = sg.Window('The Police Database', layout)
    # Event Loop to process "events" and get the "values" of the inputs.
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            break
        if event == 'Search':   # User has pressed the 'Search' button.
            on_search(values, window, cursor)
        if values['results'] and values['results'][0] != '':    # Updates Selected Citizen Data based on selected tuple.
            window['selected_citizen_data'].update(values['results'])
            set_selected_citizen_data(values, window, cursor, values['results'][0].split('|')[1].strip())
        else:   # Clears Selected Citizen Data if no tuple is selected in search results.
            window['selected_citizen_data'].update('')
        if event == 'Top Offenders':    # User has pressed the 'Top Offenders' button.
            show_top_offenders(values, window, cursor)
        if event == 'Top Offenses':     # User has pressed the 'Top Offenses' button.
            show_top_offenses(values, window, cursor)

    window.close()


# Displays a popup listing the citizens with the highest amounts of convictions.
def show_top_offenders(values, window, cursor):
    str = 'TOP OFFENDERS\n----------------------------------\n'
    new_list = list_citizens(cursor, 'SELECT * FROM top_offenders')
    for citizen in new_list:
        str += citizen + '\n'
    sg.Popup(str, keep_on_top=True)


# Displays a popup listing the offenses that has the highest amounts of convictions.
def show_top_offenses(values, window, cursor):
    s = 'TOP OFFENSES\n----------------------------------\n'
    cursor.execute('SELECT top_offenses.total, top_offenses.offense_code, offenses.offense_name FROM'
                   '(top_offenses JOIN offenses ON top_offenses.offense_code = offenses.offense_code)')
    for (total, offense_code, offense_name) in cursor:
        s += "| {:<5} | {:<7} | {:<200}".format(total, offense_code, offense_name) + '\n'
    sg.Popup(s, keep_on_top=True)


# Updates the Selected Citizen Data text box to display all info on the citizen selected in the search results list.
def set_selected_citizen_data(values, window, cursor, citizen_id):
    query = 'SELECT * FROM citizens WHERE citizen_id = {}'.format(citizen_id)
    cursor.execute(query)
    for item in cursor:
        s = 'ID: {}\n'.format(item[0])
        s += 'Firstname: {}\n'.format(item[1])
        s += 'Lastname: {}\n'.format(item[2])
        s += 'Nationality: {}\n'.format(item[3])
        s += 'Gender: {}\n'.format(item[4])
        s += 'Year of Birth: {}\n'.format(item[5])
        s += 'Convictions: {}\n'.format(item[6])

    s += '\n'
    s += tables.conviction_columns.format('Conv. ID', 'Code', 'Classification', 'Offense Name')
    s += "-" * 100 + "\n"
    query = 'SELECT convictions.conviction_id, offenses.offense_code, offense_class, offense_name '\
        'FROM convictions JOIN offenses ON convictions.offense_code = offenses.offense_code '\
        'WHERE convict_id = {}'.format(citizen_id)
    cursor.execute(query)

    for item in cursor:
        s += tables.conviction_columns.format(item[0], item[1], item[2], item[3])

    window['selected_citizen_data'].update(s)


# Called when the user presses the 'Search' buttons.
def on_search(values, window, cursor):
    inputs = []
    query = 'SELECT DISTINCT * FROM citizens'

    # Sets the filters_query depending on the contents of the filter inputs.
    if values['id_input'] != "":
        inputs.append(('citizen_id', values['id_input']))
    if values['firstname_input'] != "":
        inputs.append(('firstname', values['firstname_input']))
    if values['lastname_input'] != "":
        inputs.append(('lastname', values['lastname_input']))
    if values['nationality_input'] != "":
        inputs.append(('nationality', values['nationality_input']))
    if not values['gender_input_all']:
        if values['gender_input_m']:
            inputs.append(('gender', 'm'))
        elif values['gender_input_f']:
            inputs.append(('gender', 'f'))

    inputsAmount = 0
    filters_query = ''
    for inp in inputs:
        if inputsAmount == 0:
            filters_query += " WHERE {} LIKE '{}'".format(inp[0], inp[1])
        elif inputsAmount > 0:
            filters_query += " AND {} LIKE '{}'".format(inp[0], inp[1])
        inputsAmount += 1

    if values['min_age_input'] != "" or values['max_age_input'] != "":
        min_age = -1
        max_age = 9999
        if values['min_age_input'] != "" and values['min_age_input'].isnumeric():
            min_age = int(values['min_age_input'])
        if values['max_age_input'] != "" and values['max_age_input'].isnumeric():
            max_age = int(values['max_age_input'])
        age_query = 'year_of_birth <= {} AND citizens.year_of_birth >= {}'.format(
            int(current_year) - min_age, int(current_year) - max_age)
        if inputsAmount == 0:
            filters_query += " WHERE {}".format(age_query)
        elif inputsAmount > 0:
            filters_query += " AND {}".format(age_query)
        inputsAmount += 1

    # Gets the code of the currently selected offense, if one is selected.
    selected_offense_code = ''
    if values['offense_list'] and values['offense_list'][0] != '':
        selected_offense_code = values['offense_list'].split('|')[1].strip()

    # Uses the selected_offense_code and filters_query to determine the search query.
    if selected_offense_code != '':
        query += " JOIN convictions ON convictions.convict_id = citizens.citizen_id WHERE convictions.offense_code = '{}'".format(selected_offense_code)
        query = "SELECT DISTINCT citizen_id, firstname, lastname, nationality, gender, year_of_birth, total_convictions FROM ("\
                + query + filters_query.replace('WHERE', 'AND') + ") AS T1"
    else:
        query += filters_query

    cursor.execute('DROP TABLE IF EXISTS temptable')
    cursor.execute('CREATE TEMPORARY TABLE temptable SELECT * FROM citizens WHERE 1 = 0')

    query = 'INSERT INTO temptable (SELECT * FROM (' + query + ')AS T2)'
    cursor.execute(query)

    # Executes search and updates the Results text box, then updates the Aggregations Bar.
    window['results'].update(list_citizens(cursor, 'SELECT * FROM temptable'))
    set_aggregations_text(window, cursor)
    cursor.execute('DROP TABLE IF EXISTS temptable')


# Updates the Aggregations Bar based on the current search results.
def set_aggregations_text(window, cursor):
    query = "SELECT gender, count(gender) FROM temptable GROUP BY gender"
    cursor.execute(query)
    agg_text = ''
    males = 0
    females = 0
    total = 0
    for item in cursor:
        if item[0] == 'm':
            males += item[1]
        elif item[0] == 'f':
            females += item[1]
    total = males + females
    if total == 0:
        agg_text += 'Male: 0% Female: 0%'
    else:
        agg_text += 'Results: {} Male: {}% Female: {}%'.format(total, '{:.2f}'.format(
            males / total * 100), "{:.2f}".format(females / total * 100))
    query = "SELECT avg(year_of_birth), max(year_of_birth), min(year_of_birth) FROM temptable"
    cursor.execute(query)
    average_age = 0
    youngest = 0
    oldest = 0
    for item in cursor:
        average_age = item[0]
        youngest = item[1]
        oldest = item[2]
        if not (average_age is None or youngest is None or oldest is None):
            agg_text += ' Average Age: {}'.format('{:.2f}'.format(current_year - average_age))
            agg_text += ' Youngest: {}'.format('{:.2f}'.format(current_year - youngest))
            agg_text += ' Oldest: {}'.format('{:.2f}'.format(current_year - oldest))
    window['agg_bar'].update(agg_text)


# Returns a formatted list of the citizens in the cursor.
def list_citizens(cursor, query):
    cursor.execute(query)
    new_list = []
    for (citizen_id, firstname, lastname, ethnicity, gender, year_of_birth, total_convictions) in cursor:
        new_list.append(tables.citizen_columns.format(
            citizen_id, firstname, lastname, ethnicity, gender, year_of_birth, total_convictions))
    return new_list


# Returns a formatted list of the offenses in the cursor.
def list_offenses(cursor, query):
    cursor.execute(query)
    new_list = ['']
    for (offense_code, offense_name, offense_class) in cursor:
        new_list.append(tables.offense_columns.format(
            offense_code, offense_class, offense_name))
    return new_list
