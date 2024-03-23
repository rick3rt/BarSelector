import ctypes
import os
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QWidget,
    QMenu,
    QMenuBar,
    QDesktopWidget,
    QTableView,
    QLineEdit,
    QCheckBox,
    QPushButton,
    QMessageBox,
    QLabel,
)
import pandas as pd
from barselector import BarSelector
from widgets import MySlider, PandasModel
import numpy as np


class BarSelectorGui(QMainWindow):
    def __init__(self):

        super().__init__()
        self.name = "BarSelectorGui"
        self.app = QApplication.instance()
        self.bs = BarSelector()

        # set application font and style
        app_font = self.font()
        app_font.setPointSize(10)
        self.setFont(app_font)
        QApplication.setFont(app_font)  # for any new popup window

        QApplication.setStyle("Fusion")
        self.setWindowTitle(self.name)
        self.default_size = (1400, 600)
        self.resize(self.default_size[0], self.default_size[1])
        self.centerWindow()

        # set icon on taskbar: https://stackoverflow.com/q/14900510/7054628
        self.setWindowIcon(QIcon("resource/icon.png"))
        appid = "bs.BarSelector"  # arbitrary string
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(appid)

        # init menus
        self.menu = QMenuBar()
        self.file_menu = QMenu("&File", self)
        self.menu.addMenu(self.file_menu)
        self.setMenuBar(self.menu)

        # bar selection
        # input your address
        self.input_address = QLineEdit()
        self.input_address.setText("Klein Delfgauw 53, Delft")
        self.input_address.returnPressed.connect(self.on_address_entered)

        # type selection
        bar_types = self.bs.getTypes()
        self.check_buttons = {}
        layout_selection = QGridLayout()
        num_cols = 5
        for i, t in enumerate(bar_types):
            row = i // num_cols
            col = i % num_cols
            self.check_buttons[t] = QCheckBox(t)
            self.check_buttons[t].stateChanged.connect(self.on_type_selected)
            layout_selection.addWidget(self.check_buttons[t], row, col)

        self.type_selector = QWidget()
        self.type_selector.setLayout(layout_selection)

        self.distance_selector = MySlider("Disance", 0, 20, 0.1)
        self.distance_selector.slider.valueChanged.connect(self.on_distance_changed)

        self.tableView = QTableView()
        self.tableView.setObjectName("Cafe Database")
        self.tableView.setSortingEnabled(True)
        self.tableView.setVisible(False)
        self.current_df = None

        check_show_options = QCheckBox("Show options")
        check_show_options.clicked.connect(self.on_show_options)

        but_randomize = QPushButton("Randomize Bar!")
        but_randomize.clicked.connect(self.on_randomize)

        self.bar_label = QLabel("Selected bar")
        self.bar_label.setMinimumSize(400, 100)
        self.bar_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        # set a border around the label and set the background color
        self.bar_label.setStyleSheet(
            "border: 1px solid black; background-color: white;"
        )

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # layout.addWidget(widget_but, 0, 0)
        layout.addWidget(self.input_address, 0, 0, 1, 3)
        layout.addWidget(self.type_selector, 1, 0, 1, 3)
        layout.addWidget(self.bar_label, 2, 2, 2, 1)
        layout.addWidget(self.distance_selector, 2, 0, 1, 2)
        layout.addWidget(but_randomize, 3, 0, 1, 1)
        layout.addWidget(check_show_options, 3, 1, 1, 1)
        layout.addWidget(self.tableView, 4, 0, 1, 3)

        # add layout to main window
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.centerWindow()

        # compute distance to bars
        self.on_address_entered()

    def on_randomize(self):
        # select a random bar from the current list
        if self.current_df is None:
            self.update_table()
        df = self.current_df
        if not df.empty:
            idx = np.random.randint(len(df))
            bar = df.iloc[idx]
            bar = self.bs.getEntry(bar["title"])

            # check if url is nan
            # if bar["website"] == "nan":
            # QMessageBox.about(self, "Bar Name", bar["title"])
            # else:
            #     url = bar["website"]
            #     os.system(f"start chrome {url}")
            self.bar_label.setText(bar["title"])

    def on_show_options(self):
        self.tableView.setVisible(not self.tableView.isVisible())
        if self.tableView.isVisible():
            self.resize(self.default_size[0], self.default_size[1] + 400)
        else:
            self.resize(self.default_size[0], self.default_size[1])

    def on_address_entered(self):
        address = self.input_address.text()
        self.bs.computeDistance(address)
        self.update_table()

    def on_distance_changed(self):
        distance = self.distance_selector.getValue()
        self.bs.setDistanceFilter(distance)
        self.update_table()

    def on_type_selected(self):
        filter = []
        for t, cb in self.check_buttons.items():
            if cb.isChecked():
                filter.append(t)
        self.bs.setTypeFilter(filter)
        self.update_table()

    def update_table(self):
        self.current_df = self.bs.filterBars()
        self.setTableContent(self.current_df)

    def centerWindow(self):
        ag = QDesktopWidget().availableGeometry()
        sg = QDesktopWidget().screenGeometry()
        widget = self.geometry()
        x = int((ag.width() - widget.width()) / 3)
        y = int((ag.height() - widget.height()) / 4)
        self.move(x, y)

    def setTableContent(self, df):
        self.model = PandasModel(df)
        self.tableView.setModel(self.model)
        self.tableView.resizeColumnsToContents()
        self.tableView.horizontalHeader().setStretchLastSection(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    bs = BarSelectorGui()
    bs.show()

    ret = app.exec_()
    sys.exit(ret)
