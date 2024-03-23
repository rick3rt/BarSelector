from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QSlider, QLabel, QHBoxLayout
import pandas as pd


class MySlider(QWidget):
    def __init__(self, name, min, max, step):
        super(MySlider, self).__init__()
        self.slider = QSlider(QtCore.Qt.Horizontal)
        self.slider.setMinimum(min)
        self.slider.setMaximum(max)
        # self.slider.setSingleStep(step)
        self.slider.setTickPosition(QSlider.TicksBelow)
        range = max - min
        # self.slider.setTickInterval(range / 20)
        self.slider.valueChanged.connect(self.on_change)

        self.label = QLabel(name)
        self.value = QLabel(str(min))

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value)
        self.setLayout(layout)

    def on_change(self):
        self.value.setText(str(self.slider.value()))

    def getValue(self):
        return self.slider.value()


class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.DisplayRole,
    ):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (
            0 <= index.row() < self.rowCount()
            and 0 <= index.column() < self.columnCount()
        ):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b"display",
            DataFrameModel.DtypeRole: b"dtype",
            DataFrameModel.ValueRole: b"value",
        }
        return roles


class PandasModel(QtCore.QAbstractTableModel):

    def __init__(self, data, parent=None):
        """
        :param data: a pandas dataframe
        :param parent:
        """
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
        # self.headerdata = data.columns

    def rowCount(self, parent=None):
        return len(self._data.values)

    def columnCount(self, parent=None):
        return self._data.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.values[index.row()][index.column()])
        return None

    def headerData(self, rowcol, orientation, role):
        # print(self._data.columns[rowcol])
        # print(self._data.index[rowcol])
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[rowcol]
        if orientation == QtCore.Qt.Vertical and role == QtCore.Qt.DisplayRole:
            return self._data.index[rowcol]
        return None

    def flags(self, index):
        flags = super(self.__class__, self).flags(index)
        flags |= QtCore.Qt.ItemIsEditable
        flags |= QtCore.Qt.ItemIsSelectable
        flags |= QtCore.Qt.ItemIsEnabled
        flags |= QtCore.Qt.ItemIsDragEnabled
        flags |= QtCore.Qt.ItemIsDropEnabled
        return flags

    def sort(self, Ncol, order):
        """Sort table by given column number."""
        try:
            self.layoutAboutToBeChanged.emit()
            self._data = self._data.sort_values(
                self._data.columns[Ncol], ascending=not order
            )
            self.layoutChanged.emit()
        except Exception as e:
            print(e)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication, QMainWindow

    app = QApplication(sys.argv)

    class TestWidget(QMainWindow):
        def __init__(self, widget):
            super(TestWidget, self).__init__()
            self.setCentralWidget(widget)

    slider = MySlider("Distance", 0, 100, 1)
    test_widget = TestWidget(slider)
    test_widget.show()

    ret = app.exec_()
    sys.exit(ret)
