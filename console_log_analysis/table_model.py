from PyQt5 import QtCore


class RawDataModel(QtCore.QAbstractTableModel):

    def __init__(self, data):
        super(RawDataModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            val = self._data.iloc[index.row(), index.column()]
            return str(val)

    def rowCount(self, index):
        return self._data.shape[0]

    def columnCount(self, index):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return str(self._data.columns[section])
