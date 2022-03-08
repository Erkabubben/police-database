import PySimpleGUI as sg

def display_gui(cursor):
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    layout = [[sg.Text('Some text on Row 1')],
              [sg.Text('Firstname'), sg.InputText(key='firstname_input'), sg.Text('Lastname'), sg.InputText(key='lastname_input')],
              [sg.Text('Nationality'), sg.InputText(key='nationality_input'),
                 sg.Radio('All', "gender_input", default=True, key='gender_input_all'),
                 sg.Radio('Male', "gender_input", key='gender_input_m'),
                 sg.Radio('Female', "gender_input", key='gender_input_f')
              ],
              [sg.Combo(key='offense_list', font=('Courier New', 8), values=list_offenses(cursor, 'SELECT * FROM offenses'),
                          size=(128, 20))],
              [sg.Button('Search')],
              [sg.Listbox(key='results', font=('Courier New', 8), values=['Listbox 1', 'Listbox 2', 'Listbox 3'], size=(128, 20))],
              [sg.Button('Exit')]]

    # Create the Window
    window = sg.Window('Window Title', layout)
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        if event == 'Search':
            on_search(values, window, cursor)
        if event == sg.WIN_CLOSED or event == 'Exit':  # if user closes window or clicks cancel
            break
        #print('You entered ', values[0])

    window.close()


def on_search(values, window, cursor):
    # values['results']
    inputs = []
    query = 'SELECT * FROM citizens'
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

    selectedOffenseCode = ''
    if values['offense_list'] and values['offense_list'][0] != '':
        selectedOffenseCode = values['offense_list'].split('|')[1].strip()
        print(selectedOffenseCode)

    if selectedOffenseCode != '':
        query += " JOIN convictions ON convictions.convict_id = citizens.citizen_id WHERE convictions.offense_code = '{}'".format(selectedOffenseCode)
        query = "SELECT citizen_id, firstname, lastname, nationality, gender, date_of_birth FROM ("\
                + query + filters_query.replace('WHERE', 'AND') + ") AS T"

        print(query)

        cursor.execute(query)
        for item in cursor:
            print(item)
    else:
        query += filters_query

    window['results'].update(list_citizens(cursor, query))

def list_citizens(cursor, query):
    cursor.execute(query)
    columns = "| {:<9} | {:<25} | {:<25} | {:<4} | {:<4} | {:<10}"
    # Print column names.
    #print(columns.format('citizen_id', 'firstname', 'lastname', 'ethnicity', 'gender', 'date_of_birth'))
    # Print line to separate column names from tuples.
    #print("-" * 220)

    new_list = []
    # Change null values to 'null' strings before printing.
    for (citizen_id, firstname, lastname, ethnicity, gender, dayOfBirth) in cursor:
        new_list.append(columns.format(citizen_id, firstname, lastname, ethnicity, gender, dayOfBirth))
    return new_list


def list_offenses(cursor, query):
    cursor.execute(query)
    columns = "| {:<8} | {:<20} | {:<100}"
    # Print column names.
    #print(columns.format('offense_code', 'offense_class', 'offense_name'))
    # Print line to separate column names from tuples.
    #print("-" * 220)

    new_list = ['']
    for (offense_code, offense_name, offense_class) in cursor:
        new_list.append(columns.format(offense_code, offense_class, offense_name))
    return new_list
