import pandas as pd
from matplotlib.figure import Figure
import matplotlib.ticker as ticker
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas


class PlotCanvas(Canvas):
    def __init__(self):
        self.fig = Figure(figsize=(9, 4.4), dpi=100)
        self.axes_fwd = self.fig.add_subplot(131)
        self.axes_adj = self.fig.add_subplot(132)
        self.axes_acoustic = self.fig.add_subplot(133)
        self.axes = {'fwd': self.axes_fwd, 'adj': self.axes_adj, 'Acoustic Energy': self.axes_acoustic}
        self.graph_limits = {}
        super(PlotCanvas, self).__init__(self.fig)

    def gen_graph(self, data_dict, data_type):
        frame = pd.DataFrame(data=data_dict)
        ax = frame.plot(ax=self.axes[data_type])
        ax.grid(True)
        self.scale_axis(ax)
        if len(data_dict.keys()) > 1:
            legends = ax.legend(loc='upper right')
            for leg in legends.get_lines():
                leg.set_picker(True)
                leg.set_pickradius(6)
        return ax

    @staticmethod
    def scale_axis(ax):
        scale_x = 1e1
        ticks_x = ticker.FuncFormatter(lambda x, pos: '{0:g}'.format(x / scale_x))
        ax.xaxis.set_major_formatter(ticks_x)
        ax.set_xlabel("seconds")

    def clear_graphs(self):
        self.axes_fwd.cla()
        self.axes_adj.cla()
        self.axes_acoustic.cla()


    '''def on_hover(self, event):
        if event.inaxes:
            ax = event.inaxes
            x = event.xdata
            bottom, top = ax.get_ylim()
            global vertical_line
            if vertical_line:
                vertical_line.remove()
            vertical_line = ax.axvline(x, bottom, top, color='k', ls='--')
            vertical_line.set_visible(True)
            self.graph_canvas.draw()'''



