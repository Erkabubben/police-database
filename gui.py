import PySimpleGUI as sg
import tables

citizen_columns = "| {:<9} | {:<23} | {:<23} | {:<18} | {:<6} | {:<13} | {:<10}"
conviction_columns = "| {:<8} | {:<8} | {:<16} | {:<200}"
current_year = 2022
table_font = 'Courier New'
table_font_size = 10
inputs_width = 120

def display_gui(cursor):
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.Text('ID'), sg.InputText(key='id_input', size=(11)), sg.Text('Firstname'), sg.InputText(key='firstname_input', size=(20)), sg.Text('Lastname'), sg.InputText(key='lastname_input', size=(20))],
              [sg.Text('Nationality'), sg.InputText(key='nationality_input', size=(20)),
                 sg.Radio('All', "gender_input", default=True, key='gender_input_all'),
                 sg.Radio('Male', "gender_input", key='gender_input_m'),
                 sg.Radio('Female', "gender_input", key='gender_input_f'),
               sg.Text('Age'), sg.InputText(key='min_age_input', size=(3)), sg.Text(' to '), sg.InputText(key='max_age_input', size=(3))
              ],
              [sg.Text('Convicted for offense')],
              [sg.Combo(key='offense_list', font=(table_font, table_font_size), values=list_offenses(cursor, 'SELECT * FROM offenses'),
                          size=(inputs_width, 20))],
              [sg.Button('Search')],
              [sg.Text(citizen_columns.format('ID', 'Firstname', 'Lastname', 'Nationality', 'Gender', 'Year of Birth', 'Convictions'), font=(table_font, table_font_size))],
              [sg.Listbox(key='results', enable_events=True, font=(table_font, table_font_size), values=[], size=(inputs_width, 20))],
              [sg.Text('', key='agg_bar', font=(table_font, table_font_size))],
              [sg.Text('Selected citizen')],
              [sg.Multiline(key='selected_citizen_data', font=(table_font, table_font_size), size=(inputs_width, 20))],
              [sg.Button('Exit')]]

    # Create the Window
    window = sg.Window('The Police Database', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            break
        if event == 'Search':
            on_search(values, window, cursor)
        if values['results'] and values['results'][0] != '':
            window['selected_citizen_data'].update(values['results'])
            set_selected_citizen_data(values, window, cursor, values['results'][0].split('|')[1].strip())
        else:
            window['selected_citizen_data'].update('')
        #print('You entered ', values[0])

    window.close()


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
    s += conviction_columns.format('Conv. ID', 'Code', 'Classification', 'Offense Name')
    s += "-" * 100 + "\n"
    query = 'SELECT convictions.conviction_id, offenses.offense_code, offense_class, offense_name FROM convictions JOIN offenses ON convictions.offense_code = offenses.offense_code WHERE convict_id = {}'.format(citizen_id)
    cursor.execute(query)

    for item in cursor:
        s += conviction_columns.format(item[0], item[1], item[2], item[3])

    window['selected_citizen_data'].update(s)


def on_search(values, window, cursor):
    inputs = []
    query = 'SELECT DISTINCT * FROM citizens'
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
        age_query = 'date_of_birth <= {} AND citizens.date_of_birth >= {}'.format(int(current_year) - min_age, int(current_year) - max_age)
        if inputsAmount == 0:
            filters_query += " WHERE {}".format(age_query)
        elif inputsAmount > 0:
            filters_query += " AND {}".format(age_query)
        inputsAmount += 1

    selectedOffenseCode = ''
    if values['offense_list'] and values['offense_list'][0] != '':
        selectedOffenseCode = values['offense_list'].split('|')[1].strip()
        print(selectedOffenseCode)

    if selectedOffenseCode != '':
        query += " JOIN convictions ON convictions.convict_id = citizens.citizen_id WHERE convictions.offense_code = '{}'".format(selectedOffenseCode)
        query = "SELECT DISTINCT citizen_id, firstname, lastname, nationality, gender, date_of_birth, total_convictions FROM ("\
                + query + filters_query.replace('WHERE', 'AND') + ") AS T1"
    else:
        query += filters_query

    cursor.execute('DROP TABLE IF EXISTS temptable')
    cursor.execute('CREATE TEMPORARY TABLE temptable SELECT * FROM citizens WHERE 1 = 0')

    query = 'INSERT INTO temptable (SELECT * FROM (' + query + ')AS T2)'
    cursor.execute(query)

    window['results'].update(list_citizens(cursor, 'SELECT * FROM temptable'))
    set_aggregations_text(window, cursor)
    cursor.execute('DROP TABLE IF EXISTS temptable')


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
    query = "SELECT avg(date_of_birth), max(date_of_birth), min(date_of_birth) FROM temptable"
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


def list_citizens(cursor, query):
    cursor.execute(query)
    new_list = []
    for (citizen_id, firstname, lastname, ethnicity, gender, dayOfBirth, total_convictions) in cursor:
        new_list.append(citizen_columns.format(citizen_id, firstname, lastname, ethnicity, gender, dayOfBirth, total_convictions))
    return new_list


def list_offenses(cursor, query):
    cursor.execute(query)
    columns = "| {:<6} | {:<16} | {:<100}"
    # Print column names.
    #print(columns.format('offense_code', 'offense_class', 'offense_name'))
    # Print line to separate column names from tuples.
    #print("-" * 220)

    new_list = ['']
    for (offense_code, offense_name, offense_class) in cursor:
        new_list.append(columns.format(offense_code, offense_class, offense_name))
    return new_list
