import requests
from docx import Document
import urllib.parse
import json
import pandas as pd
import email_action
import scheduler

USERNAME = 'ericm@fusmobile.com'
PASSWORD = 'PresharedKey1!'
WORKSPACE_ID = '898485829'
LOGIN_INFO = {'email': USERNAME, 'password': PASSWORD, 'workspaceId': WORKSPACE_ID}


def get_token_header():
    response = requests.post('https://api.arenasolutions.com/v1/login', json=LOGIN_INFO)
    j_response = response.json()
    return {'arena_session_id': j_response['arenaSessionId']}


def parse_title(title):
    split_title = title.split()
    sys_name = split_title[-1]
    sys_name_split = sys_name.split('_')
    sys_name = sys_name_split[-1]
    return sys_name


def parse_date(date):
    return_date = []
    splitted = date.split('T')
    y_m_d = splitted[0].split('-')
    for i in range(len(y_m_d)):
        return_date.append(y_m_d[i])
    hour = splitted[1].strip('Z').split(':')
    for i in range(len(hour)):
        return_date.append(hour[i])

    return return_date


files_request = 'https://api.arenasolutions.com/v1/files?title=QF-00005*&format=docx'


def compare_dates(date1, date2):
    if date1 is None or is_nan(date1):
        return 1
    if date2 is None or is_nan(date2):
        return -1
    idx = 0
    while idx < 6:
        if date1[idx] < date2[idx]:
            return 1
        elif date1[idx] > date2[idx]:
            return -1
        idx += 1
    return 0


def is_nan(num):
    if type(num) != float:
        return False
    return num != num


def get_latest_form(forms):
    if forms:
        latest = forms[0]
        for form in forms:
            if compare_dates(parse_date(latest['creationDateTime']), parse_date(form['creationDateTime'])) == 1:
                latest = form
        return latest


def get_file(guid):
    return


def get_working_systems(access_header):
    systems = {}
    req = 'https://api.arenasolutions.com/v1/items?criteria='
    criteria= '[ [ { "attribute": "category.name", "value": "DHR Neurolyser XR System", "operator": "IS_EQUAL_TO" } ] ]'
    encoded_req = req + urllib.parse.quote(criteria)
    response = requests.get(encoded_req, headers=access_header)
    for result in response.json()['results']:
        if result['lifecyclePhase']['name'] == 'Design' and result['number'].startswith('NXR100-0000'):
            systems[result['number']] = {'guid': result['guid']}
    return systems


def get_calibration_files(access_header, systems):
    req = 'https://api.arenasolutions.com/v1/items/'
    for sys in systems:
        files = systems[sys]['guid'] + '/files'
        files_request = req + files
        response = requests.get(files_request, headers=access_header)
        qf5s = []
        qf24s = []
        for result in response.json()['results']:
            if result['file']['title'].find('QF-00005') != -1:
                qf5s.append(result['file'])
            if result['file']['title'].find('QF-00024') != -1:
                qf24s.append(result['file'])
            if result['file']['title'].find('Log files') != -1 or result['file']['title'].find('Log Files') != -1:
                systems[sys]['log guid'] = result['file']['guid']
                systems[sys]['log date'] = parse_date(result['file']['creationDateTime'])
        latest_qf5 = get_latest_form(qf5s)
        latest_qf24 = get_latest_form(qf24s)
        systems[sys]['QF5 guid'] = latest_qf5['guid']
        systems[sys]['QF5 date'] = parse_date(latest_qf5['creationDateTime'])
        if latest_qf24:
            systems[sys]['QF24 guid'] = latest_qf24['guid']
            systems[sys]['QF24 date'] = parse_date(latest_qf24['creationDateTime'])
    return systems


def update_table(systems):
    current_systems = pd.read_csv('Acoustic_Calibration_Master_Table.csv', index_col=0).to_dict()
    print(current_systems)
    existing_list = [sys for sys in current_systems]
    sys_list = [sys for sys in systems]
    new_systems = [sys for sys in sys_list if sys not in existing_list]
    for sys_number in new_systems:  # if there is a new system, put it in master table
        current_systems[sys_number] = systems.pop(sys_number)
        # set_notifications(sys_number)

    for sys_number in existing_list:  # if there is a new QF5, update
        if compare_dates(current_systems[sys_number]['QF5 date'], systems[sys_number]['QF5 date']) == 1:
            current_systems[sys_number] = systems[sys_number]
            # set_notifications(sys_number)
    df = pd.DataFrame(current_systems)
    df.to_csv('Acoustic_Calibration_Master_Table.csv')


def set_notifications(system_number):  # TODO - implement
    return


if __name__ == '__main__':
    '''header = get_token_header()
    syss = get_working_systems(header)
    sys_w_files = get_calibration_files(header, syss)
    update_table(sys_w_files)'''
    document = Document('QAD-00007_Neurolyser XR Traceability_ver_1.2.docx')
    table = document.tables[0]
    data = []
    keys = None
    for i, row in enumerate(table.rows):
        text = (cell.text for cell in row.cells)
        if i == 0:
            keys = tuple(text)
            continue
        row_data = dict(zip(keys, text))
        data.append(row_data)
    print(data)

'''class CalibrationForm:

    def __init__(self, date, guid, file_num, category_uid):
        self.type = file_num
        self.date = parse_date(date)
        self.guid = guid
        self.category_guid = category_uid
        self.path = None
        self.system = None

    def set_system(self, sys):
        self.system = sys

    def compare(self, form):
        try:
            if self.type != form.type:
                raise TypeError
            idx = 0
            while idx < 6:
                if self.date[idx] < form.date[idx]:
                    return False
            return True
        except TypeError:
            return None

    def format_date(self):
        return self.date[0] + '-' + self.date[1] + '-' + self.date[2]



'''

