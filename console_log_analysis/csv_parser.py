import csv
import math
import os
import pandas as pd
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot


class Parser(QObject):

    finished_parsing = pyqtSignal(dict)

    @pyqtSlot(str)
    def file_to_parse(self, log_file):
        session = parse_csv(log_file)
        self.finished_parsing.emit(session)


class SonicationItem:

    def __init__(self, id, attributes):
        self.id = id
        self.attributes = attributes
        self.delivered_acoustic_energy = []
        self.time_stamps = []
        self.raw_data = []
        self.temp = []
        self.fwd = {}
        self.rev = {}
        self.ticks_adj = {}
        self.const_data_per_channel = {}  # base ticks, avg deviation, max deviation
        self.error_code = None

    def add_out_time(self, time):
        self.attributes.update({'Out Time': time})
        self.calc_duration()

    def calc_duration(self):
        in_num = time_str_to_int(self.attributes['In Time'])
        out_num = time_str_to_int(self.attributes['Out Time'])
        duration = str(out_num - in_num)
        self.attributes.update({'Duration': duration})

    def power_per_channel(self):
        return float(self.attributes['Electrical Power (W)'])/len(self.fwd.keys())

    def max_deviation(self, channel):
        ppc = self.power_per_channel()
        max_dev = math.max(self.fwd[channel])
        return max_dev/ppc

    def avg_deviation(self, channel):
        avg_power = sum(self.fwd[channel])/len(self.fwd[channel])
        return avg_power/self.power_per_channel()


def csv_reader_to_dict(path):
    if os.path.getsize(path) == 0:
        return None, None
    with open(path, 'r') as file:
        csv_file = csv.reader(file)
        header = get_header(next(csv_file))
        keys = [cell for cell in next(csv_file) if cell]
        rows_as_dict = []
        for row in csv_file:
            if len(row) > 4 and row[3] == 'ACTIVE':
                row.pop(25)  # remove an empty cell in row
            rows_as_dict.append(dict(zip(keys, row)))
            try:
                if row[3] == 'ACTIVE':
                    validate_row(rows_as_dict[len(rows_as_dict) - 1])
            except Exception:
                return None, None
    return header, rows_as_dict


def parse_csv(path):
    header, csv_dict = csv_reader_to_dict(path)
    sonication = {'header': header}
    if not csv_dict:
        return {}
    items = []
    in_session = False
    num = 1
    measurement_counter = -1
    for row in csv_dict:
        if not in_session and row['Unit State'] == 'ACTIVE':
            in_session = True
            get_sonication_data(row, items, num, prev_row)
        elif in_session and (row['Unit State'] == 'CEASE' or row['Unit State'] == 'ALARM'):
            in_session = False
            end_sonication(row, items[num - 1], prev_row_time)
            num += 1
            measurement_counter = -1
        if in_session and row['Unit State'] == 'ACTIVE':
            measurement_counter += 1
            update_measurements(row, items[num - 1], measurement_counter)
        prev_row_time = row['Time']
        prev_row = row
    set_raw_data_format(items)
    sonication.update({'sonications': items})
    sonication.update({'channel count': len(items[0].fwd.keys())})
    #get_error_codes()
    return sonication


'''Mid Parsing Functions'''


"""def get_header_updated(header_row):
    header_dict = {header_row[:6][i]: header_row[:6][i + 1] for i in range(0, len(header_row[:6]), 2)}
    gain_pot = {header_row[8:16][i]: header_row[8:16][i + 1] for i in range(0, len(header_row[8:16]), 2)}
    header_dict[header_row[7]] = gain_pot
    header = pd.DataFrame(header_dict)
    return header"""


def get_header(header_row):
    header_list = header_row[:6] + header_row[7:16]
    header = '                                                            '
    for i in range(len(header_list)):
        header += header_list[i]
        if i == 0 or i == 2 or i == 4:
            header += ':'
        header += ' '
    return header


def get_sonication_data(row, items, index, prev_row):
    static_fieldnames = ['Date', 'Time', 'Unit State', 'Electrical Energy (J)', 'Time Setting (s)',
                         'Electrical Power (W)', 'Cal Factor (A)', 'Sonication Mode']
    data_per_channel = ['Base Ticks (A)', 'Base Ticks (B)', 'Base Ticks (C)', 'Base Ticks (D)']
    attributes = {key: row[key] for key in row if key in static_fieldnames}
    attributes['Cal Factor'] = attributes.pop('Cal Factor (A)')
    attributes['In Time'] = attributes.pop('Time')
    item = SonicationItem(index, attributes)
    if prev_row and prev_row['Unit State']:
        item.raw_data.append(prev_row)
    item.raw_data.append(row)
    i = 1
    ticks_dict = {}
    for key in data_per_channel:
        ticks_dict[i] = row[key]
        i += 1
    item.const_data_per_channel = {'Base Ticks': ticks_dict}
    items.append(item)


def update_measurements(row, item, time):
    enum_fwd = enumerate([float(row[key]) for key in row.keys() if key.endswith('FWD')], 1)
    enum_rev = enumerate([float(row[key]) for key in row.keys() if key.endswith('REV')], 1)
    enum_adj = enumerate([float(row[key]) for key in row.keys() if key.startswith('Adj')], 1)
    if not item.time_stamps:
        item.fwd = {idx: [data] for idx, data in enum_fwd}
        item.rev = {idx: [data] for idx, data in enum_rev}
        item.ticks_adj = {idx: [data] for idx, data in enum_adj}
    else:
        for idx, data in enum_fwd:
            item.fwd[idx].append(data)
        for idx, data in enum_rev:
            item.rev[idx].append(data)
        for idx, data in enum_adj:
            item.ticks_adj[idx].append(data)
    item.raw_data.append(row)
    item.temp.append(float(row.get('Unit Temperature (C)')))
    item.delivered_acoustic_energy.append(float(row.get('Delivered Acoustic Energy (J)')))
    item.time_stamps.append(time)


def end_sonication(row, item, time):
    avg_val_dict, max_val_dict = avg_max_deviations_vals(item.fwd, item.power_per_channel())
    item.const_data_per_channel['Average Deviation (W)'], item.const_data_per_channel['Max Deviation (W)']\
        = avg_val_dict, max_val_dict
    item.const_data_per_channel['Average Deviation (%)'], item.const_data_per_channel['Max Deviation (%)']\
        = avg_max_deviations_percentage(max_val_dict, avg_val_dict, item.power_per_channel(), item.fwd)
    item.const_data_per_channel['SNR'] = calc_snr(avg_val_dict)
    item.add_out_time(time)
    item.raw_data.append(row)
    if row.get('Unit State') == 'ALARM':
        item.error_code = row.get('Error/Reason')


'''FORMAT ADJUSTMENT FUNCTIONS'''


def set_raw_data_format(items_list):
    for item in items_list:
        raw_data_format(item)


def raw_data_format(item):
    raw_data_dict_not_active = {key: [] for key in item.raw_data[0].keys()}
    raw_data_dict = {key: [] for key in item.raw_data[1].keys()} # raw_data[0] is in state ARMED, fields Y - AH missing
    missing_keys = [key for key in raw_data_dict if key not in raw_data_dict_not_active]
    rows = item.raw_data
    for row in rows:
        if row['Unit State'] != 'ACTIVE':
            for key in missing_keys:
                row[key] = ''
        for key in raw_data_dict.keys():
            raw_data_dict[key].append(row[key])
    fixed_format = pd.DataFrame(raw_data_dict)
    item.raw_data = fixed_format


def time_str_to_int(time):
    time_list = [int(x) for x in time.split(":")[0:3]]
    return time_list[2] + 60*time_list[1] + 3600*time_list[0]


'''DEVIATION CALCULATION'''


def avg_max_deviations_vals(fwd_dict, ppc):
    avg_dict = {}
    max_dict = {}
    for key in fwd_dict.keys():
        avg_dict[key] = float(format(sum(fwd_dict[key])/len(fwd_dict[key]) - ppc, ".2f"))
        max_dict[key] = float(format(max([abs(val) for val in fwd_dict[key]]) - ppc, ".2f"))
    return avg_dict, max_dict


def avg_max_deviations_percentage(max, avg, ppc, dict):
    avg_dict = {}
    max_dict = {}
    for key in dict.keys():
        max_dict[key] = format(max[key]/ppc*100, ".2f")
        avg_dict[key] = format(avg[key] / ppc * 100, ".2f")
    return avg_dict, max_dict


def deviation_margins_10_percent(ppc):
    return 0.9*ppc, 1.1*ppc


def deviation_margins_30_percent(ppc):
    return 0.7*ppc, 1.3*ppc


def max_deviation_overall(max_dict):
    max_val_per_channel = max_dict.values()
    return max(max_val_per_channel)


def calc_snr(avg_val_dict):
    snr_dict = {}
    for key in avg_val_dict:
        try:
            snr_dict[key] = format(1/abs(avg_val_dict[key]), '.2f')
        except ZeroDivisionError:
            snr_dict[key] = 'Inf'
    return snr_dict



'''VALIDATION FUNCTIONS'''


def validate_row(row):
    try:
        integer_fields = ['Electrical Energy (J)', 'Time Setting (s)', 'Unit Temperature (C)', 'Base Ticks (A)',
                          'Base Ticks (B)', 'Base Ticks (C)', 'Base Ticks (D)', 'Adj Ticks (A)', 'Adj Ticks (B)',
                          'Adj Ticks (C)', 'Adj Ticks (D)']
        float_fields = ['Electrical Power (W)', 'Chan A FWD', 'Chan B FWD', 'Chan C FWD', 'Chan D FWD', 'Chan A REV',
                        'Chan B REV', 'Chan C REV', 'Chan D REV', 'Delivered Acoustic Energy (J)', 'Cal Factor (A)',
                        'Cal Factor (B)', 'Cal Factor (C)', 'Cal Factor (D)']
        for key in integer_fields:
            if row[key]:
                validate_integer(row[key])
            elif row['Unit State'] == 'ACTIVE':
                raise ValueError
        for key in float_fields:
            if row[key]:
                validate_float(row[key])
            elif row['Unit State'] == 'ACTIVE':
                raise ValueError
        validate_time(row['Time'])
    except KeyError:
        raise
    except ValueError:
        raise


def validate_integer(val):
    try:
        if val.startswith('-'):
            val_fixed = val.strip('-')
        else:
            val_fixed = val
        if not val_fixed.isdigit():
            raise ValueError
    except ValueError:
        raise


def validate_float(val):
    try:
        num = float(val)
        if num < 0:
            raise ValueError
    except ValueError:
        raise


def validate_time(time):
    try:
        time_list = [int(i) for i in time.split(':')]
        for i in time_list:
            if i < 0:
                break
        if not (time_list[0] < 24 and time_list[1] < 60 and time_list[2] < 60):
            raise ValueError
    except ValueError:
        raise


def get_error_codes():
    with open('ECodes.h', 'r') as file:
        lines = file.readlines()
        splited = [line.split() for line in lines]
        error_codes = {}
        for line in splited:
            if line and line[0] == 'const':
                error_codes[line[4].strip(';')] = line[2]
    return error_codes


if __name__ == '__main__':
    parse_csv('50.CSV')
