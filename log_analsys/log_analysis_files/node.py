
class Node(object):

    def __init__(self, name, in_time, index, out_time=-1, called_by=None, duration=0):
        self.name = name
        self.in_time = in_time[0:len(in_time) - 1]
        self.index = index
        self.out_time = out_time
        self.call_list = []
        self.output = ''
        self.called_by = called_by
        self.duration = duration

    def get_callees(self):
        return self.call_list

    def get_prev(self):
        return self.called_by

    def set_parent(self, parent):
        self.called_by = parent

    def add_callee(self, son):
        if son is None:
            return
        self.call_list.append(son)
        son.set_parent(self)

    def add_out_time(self, time):
        self.out_time = time
        self.calc_duration()

    def print_callees(self):
        for func in self.call_list:
            print(func.name)

    def add_output(self, to_add):
        if self.output == '':
            self.output = [to_add]
        else:
            self.output.append(to_add)

    def get_output(self):
        output_string = ''
        for line in self.output:
            output_string += line + '\n'
        return output_string

    def print_duration(self):
        print(self.name + ' took ' + str(self.duration) + ' seconds')

    def get_index(self):
        return self.index

    def calc_duration(self):
        in_num = [int(x) for x in self.in_time.split(":")[0:3]]
        out_num = [int(y) for y in self.out_time.split(":")[0:3]]
        self.duration = out_num[2] - in_num[2] + 60*(out_num[1] - in_num[1]) + 3600*(out_num[0] - in_num[0])
        return
