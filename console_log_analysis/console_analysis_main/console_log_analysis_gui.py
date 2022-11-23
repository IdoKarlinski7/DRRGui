from PyQt5.QtWidgets import QMainWindow, QTableWidgetItem, QListWidgetItem, QFileDialog
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavToolBar
from PyQt5 import QtCore
from PyQt5.uic import loadUi
import numpy as np
import csv_parser as cp
import graph_obj as go
import table_model as table
import pandas.plotting._matplotlib


error_codes = cp.get_error_codes()


class ConsoleLogMainWindow(QMainWindow):

    parse_log = QtCore.pyqtSignal(str)

    def __init__(self):
        super(ConsoleLogMainWindow, self).__init__()
        loadUi('console_layout.ui', self)
        self.link_menu_bar_functions()
        self.init_threading()
        self.set_graph_widget()
        self.showMaximized()

        """ INIT METHODS """
    def link_menu_bar_functions(self):
        self.actionOpen.triggered.connect(self.get_file)
        self.actionClear.triggered.connect(self.clear_all)
        self.actionSave.triggered.connect(self.save_as_png)

    def init_threading(self):
        self.parser = cp.Parser()
        self.parsing_thread = QtCore.QThread()
        self.parser.moveToThread(self.parsing_thread)
        self.parsing_thread.start()
        self.parse_log.connect(self.parser.file_to_parse)
        self.parser.finished_parsing.connect(self.on_finish_parsing)

    def set_graph_widget(self):
        self.graph_canvas = go.PlotCanvas()
        self.graph_toolbar = NavToolBar(self.graph_canvas, self.centralwidget)
        self.graphWidget.layout().addWidget(self.graph_toolbar)
        self.graphWidget.layout().addWidget(self.graph_canvas)

    """ GUI HANDLING """
    def on_finish_parsing(self, sonication):
        if not sonication:
            self.headerBar.setText('Log file is corrupted, please inspect file.')
            return
        self.items = sonication['sonications']
        self.channel_count = sonication['channel count']
        self.headerBar.setText(sonication['header'])
        self.set_items_list()

    def set_items_list(self):
        self.insert_channels_columns()
        self.detailWidget.setShowGrid(True)
        self.channelDataWidget.setShowGrid(True)
        for item in self.items:
            list_item = QListWidgetItem('Sonication Number ' + str(item.id))
            self.itemsWidget.addItem(list_item)
        self.itemsWidget.itemDoubleClicked.connect(self.on_item_click)

    """ INTERACTIVE METHODS - ITEMS LIST WIDGET """

    def on_item_click(self):
        self.detailWidget.clearContents()
        self.channelDataWidget.clearContents()
        current = self.itemsWidget.currentItem()
        index = self.get_item_index(current)
        curr_sonic = self.items[index]
        self.set_table_widget_info(curr_sonic)
        self.set_raw_data_table(curr_sonic)
        self.gen_graphs(curr_sonic)

    def set_table_widget_info(self, item):
        if 'Unit State' in item.attributes.keys():
            item.attributes.pop('Unit State')
        self.fill_data_per_channel(item.const_data_per_channel)
        self.fill_data_per_sonication(item.attributes, item.error_code)
        self.detailWidget.resizeColumnsToContents()

    def gen_graphs(self, item):
        self.graph_canvas.clear_graphs()
        self.connect_interactive_funcs()
        self.gen_fwd_graph(item)
        self.gen_acoustic_graph(item)
        self.gen_ticks_graph(item)

    def set_raw_data_table(self, item):
        raw_data_model = table.RawDataModel(item.raw_data)
        self.tableView.setModel(raw_data_model)
        self.tableView.resizeColumnsToContents()

    """ SONICATION AND CHANNELS DATA DISPLAYING METHODS """

    def insert_channels_columns(self):
        if self.channelDataWidget.columnCount() < 3:
            for i in range(self.channel_count):
                self.channelDataWidget.insertColumn(i)
                channel_header = QTableWidgetItem(chr(65 + i))
                self.channelDataWidget.setHorizontalHeaderItem(i, channel_header)
                self.channelDataWidget.verticalHeader().setVisible(False)
            channel_header = QTableWidgetItem(' ')
            self.channelDataWidget.insertColumn(self.channel_count)
            self.channelDataWidget.setHorizontalHeaderItem(self.channel_count, channel_header)
        self.channelDataWidget.horizontalHeader().setVisible(True)
        self.channelDataWidget.resizeColumnsToContents()

    def fill_data_per_channel(self, dpc_dict):
        row_for_data_pc = 0
        for key in dpc_dict.keys():
            if not self.channelDataWidget.verticalHeader().isVisible():
                self.channelDataWidget.insertRow(row_for_data_pc)
            key_cell = QTableWidgetItem(key)
            self.channelDataWidget.setVerticalHeaderItem(row_for_data_pc, key_cell)
            for sub_key in dpc_dict[key]:
                val_cell = QTableWidgetItem(str(dpc_dict[key][sub_key]))
                self.channelDataWidget.setItem(row_for_data_pc, sub_key - 1, val_cell)
            row_for_data_pc += 1
        tick_error_margin = QTableWidgetItem('Ticks Avg Per Channel at (x)')
        raw_fwd_power = QTableWidgetItem('FWD Power per channel at (x)')
        if not self.channelDataWidget.verticalHeader().isVisible():
            self.channelDataWidget.insertRow(row_for_data_pc)
            self.channelDataWidget.insertRow(row_for_data_pc + 1)
        self.channelDataWidget.setVerticalHeaderItem(row_for_data_pc, raw_fwd_power)
        self.channelDataWidget.setVerticalHeaderItem(row_for_data_pc + 1, tick_error_margin)
        self.channelDataWidget.verticalHeader().setVisible(True)
        self.channelDataWidget.resizeColumnsToContents()

    def fill_data_per_sonication(self, const_dict, error_code=None):
        row = 0
        for key in const_dict.keys():
            if not self.detailWidget.verticalHeader().isVisible():
                self.detailWidget.insertRow(row)
            key_cell = QTableWidgetItem(str(key))
            value = QTableWidgetItem(str(const_dict[key]))
            self.detailWidget.setVerticalHeaderItem(row, key_cell)
            self.detailWidget.setItem(row, 0, value)
            row += 1
            error_key = QTableWidgetItem('Error Code')
            self.detailWidget.setVerticalHeaderItem(row, error_key)
            if error_code:
                error = error_codes[error_code]
                error_val = QTableWidgetItem(error)
                self.detailWidget.setItem(row, 0, error_val)
        self.detailWidget.verticalHeader().setVisible(True)
        self.detailWidget.resizeColumnsToContents()

    """GRAPHS GENERATING AND HANDLING"""

    def connect_interactive_funcs(self):
        self.graph_canvas.figure.canvas.mpl_connect('pick_event', self.on_pick)
        self.graph_canvas.figure.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.graph_canvas.figure.canvas.mpl_connect('button_press_event', self.on_press)

    def gen_fwd_graph(self, item):
        channels_data = {chr(64 + i): item.fwd[i] for i in item.fwd.keys()}
        ax = self.graph_canvas.gen_graph(channels_data, 'fwd')
        ppc = item.power_per_channel()
        self.set_axis_limits(ppc, ax)
        self.set_error_margins(ppc, ax, item.attributes['Electrical Power (W)'])
        ax.set_title('Electrical Power Forward')
        ax.set_ylabel('FWD Power (J)')
        self.graph_canvas.draw()

    def gen_ticks_graph(self, item):
        channels_data = {chr(64 + i): item.ticks_adj[i] for i in item.ticks_adj.keys()}
        ax = self.graph_canvas.gen_graph(channels_data, 'adj')
        ax.set_title('Ticks Adjustments')
        ax.set_ylabel('Ticks')
        self.graph_canvas.draw()

    def gen_acoustic_graph(self, item):
        data = {'Delivered Acoustic Energy (J)': item.delivered_acoustic_energy}
        ax = self.graph_canvas.gen_graph(data, 'Acoustic Energy')
        ax.set_title('Delivered Acoustic Energy')
        ax.set_ylabel('Acoustic Energy (J)')
        x_axis = range(len(item.delivered_acoustic_energy))
        ax.fill_between(x_axis, 0, item.delivered_acoustic_energy, alpha=0.3)
        self.graph_canvas.draw()

    """  INTERACTIVE GRAPH METHODS  """

    def on_pick(self, event):
        leg = event.artist
        ax = leg.axes
        lines = ax.get_lines()
        line = self.find_line(lines, leg)
        global is_line_isolated
        if is_line_isolated[0] and is_line_isolated[1] and is_line_isolated[0] == line:
            for lin in lines:
                lin.set_visible(True)
            is_line_isolated = (line, False)
        else:
            is_line_isolated = (line, True)
            line.set_visible(True)
            for other_lines in lines:
                if other_lines == line or str(other_lines.get_color()) == 'k':
                    pass
                else:
                    other_lines.set_visible(False)
        self.graph_canvas.draw()

    def on_hover(self, event):
        if event.inaxes:
            ax = event.inaxes
            x = event.xdata
            bottom, top = ax.get_ylim()
            global vertical_line
            if vertical_line:
                vertical_line.remove()
            vertical_line = ax.axvline(x, bottom, top, color='k', ls='--')
            vertical_line.set_visible(True)
            self.graph_canvas.draw()

    def on_press(self, event):
        if event.inaxes:
            ax = event.inaxes
            x = event.xdata
            bottom, top = ax.get_ylim()
            row_count = self.channelDataWidget.rowCount()
            self.update_channel_data_table(x, row_count)
            self.set_avg_ticks_in_table(x, row_count)
            self.set_fwd_power_in_table(x, row_count)
            global line_on_press
            if line_on_press:
                line_on_press.remove()
            line_on_press = ax.axvline(x, bottom, top, color='y', ls='--')
        self.channelDataWidget.resizeColumnsToContents()

    """INTERACTIVE GRAPHS AUXILIARY METHODS"""

    def set_avg_ticks_in_table(self, x, row_count):
        current = self.itemsWidget.currentItem()
        index = self.get_item_index(current)
        curr_sonic = self.items[index]
        ticks_dict = curr_sonic.ticks_adj
        x_data = range(len(ticks_dict[1]))
        ticks_avg = {}
        for key in ticks_dict.keys():
            avg = 0
            for other in ticks_dict.keys():
                if other != key:
                    avg += np.interp(x, x_data, ticks_dict[other])
            ticks_avg[key] = format(avg/3, ".2f")
        for key in ticks_avg.keys():
            ticks_avg_at_x = QTableWidgetItem(ticks_avg[key])
            self.channelDataWidget.setItem(row_count - 1, key - 1, ticks_avg_at_x)

    def set_fwd_power_in_table(self, x, row_count):
        current = self.itemsWidget.currentItem()
        index = self.get_item_index(current)
        curr_sonic = self.items[index]
        fwd_dict = curr_sonic.fwd
        power_at_x_dict = {key: format(np.interp(x, range(len(fwd_dict[key])), fwd_dict[key]), '.2f') for key
                           in fwd_dict.keys()}
        for key in power_at_x_dict.keys():
            fwd_power_at_x = QTableWidgetItem(power_at_x_dict[key])
            self.channelDataWidget.setItem(row_count - 2, key - 1, fwd_power_at_x)

    def update_channel_data_table(self, x, row_count):
        x_str = format(x, '.3f')
        ticks_avg_header = QTableWidgetItem('Ticks Avg Per Channel at x = ' + x_str)
        raw_fwd_power_header = QTableWidgetItem('FWD Power per channel at x = ' + x_str)
        self.channelDataWidget.setVerticalHeaderItem(row_count - 2, raw_fwd_power_header)
        self.channelDataWidget.setVerticalHeaderItem(row_count - 1, ticks_avg_header)
        self.channelDataWidget.verticalHeader().setVisible(True)

    """ action open connected function"""
    def get_file(self):
        if self.itemsWidget:
            self.clear_all()
        file_name = QFileDialog.getOpenFileName(self, 'Open file', ' ', "log files (*.csv)")
        if file_name != ('', ''):  # if user pressed open then cancel the file name will be ('','')
            win_format_path = file_name[0].replace('/', '\\')
            self.parse_log.emit(win_format_path)

    """action clear connected function"""
    def clear_all(self):
        self.headerBar.clear()
        self.detailWidget.clearContents()
        self.channelDataWidget.clearContents()
        if self.tableView:
            self.tableView.clearSpans()
        if self.graphWidget:
            self.graph_canvas.clear_graphs()
        if self.itemsWidget:
            self.itemsWidget.clear()

    def save_as_png(self):
        current = self.itemsWidget.currentItem()
        index = self.get_item_index(current)
        curr_sonic = self.items[index]
        date = curr_sonic.attributes['Date'].replace('/', '_')
        sonic_idx = str(curr_sonic.id)
        filename = date + '_sonication_' + sonic_idx + '.png'
        if self.itemsWidget:
            curr_state = self.grab()
            curr_state.save(filename)

    """ AUXILIARY METHODS """

    @staticmethod
    def set_error_margins(ppc, ax, power):
        ax.margins(0)
        ax.axhline(ppc, color='k')
        low_30, up_30 = cp.deviation_margins_30_percent(ppc)
        if float(power) > 30:
            low_10, up_10 = cp.deviation_margins_10_percent(ppc)
        else:
            low_10 = ppc - 0.75
            up_10 = ppc + 0.75
        ax.axhspan(low_10, up_10, facecolor='y', alpha=0.05)
        ax.axhspan(up_10, up_30, facecolor='orange', alpha=0.25)
        ax.axhspan(low_30, low_10, facecolor='orange', alpha=0.25)
        bottom, top = ax.get_ylim()
        if up_30 < top:
            ax.axhspan(up_30, top, facecolor='r', alpha=0.3)
        if low_30 > 0:
            ax.axhspan(0, low_30, facecolor='r', alpha=0.3)

    @staticmethod
    def set_axis_limits(ppc, ax):
        bottom = 0.5*ppc
        top = 1.5*ppc
        ax.set_ylim(bottom, top)

    @staticmethod
    def find_line(lines, legend):
        for line in lines:
            if line.__str__() == legend.__str__():
                return line

    @staticmethod
    def get_channel_name(line_str):
        return line_str[len(line_str) - 2]

    @staticmethod
    def get_item_index(list_item):
        name = list_item.text().split()
        index = int(name[2]) - 1
        return index


is_line_isolated = (None, False)
vertical_line = None
line_on_press = None
