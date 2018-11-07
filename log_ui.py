from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5 import QtGui, QtCore
from log_table_model import LogTableModel
import os, signal
import log_poller
import sys

class Window_title:
    path = None

    @property
    def text(self):
        return '%s - Log Viewer' % self.path

class Line_QMessageBox(QMessageBox):
    bullet = None

    def __init__(self):
        super().__init__()
        bullet = u"\u2022"
        self.bullet = '<br />    <span style="color: #AAAAAA">' + bullet + '</span> '

    def list_to_bullets(self, list_details):
        bullet_list = self.bullet.join(list_details)
        return self.bullet + bullet_list

    def set_line(self, parsed_line, row_no):
        self.setIcon(QMessageBox.Information)
        self.setText("Information about the item")
        self.setInformativeText(self.list_to_bullets(parsed_line[:-1]))
        self.setWindowTitle('Line %d Details' % row_no)
        self.setDetailedText(parsed_line[-1])
        self.setStandardButtons(QMessageBox.Cancel)

class Events:
    table_model = None

    def __init__(self, table_model):
        self.table_model = table_model

    def table_double_click(self, modeIndex):
        msg = Line_QMessageBox()
        msg.set_line(
            self.table_model.parsed_lines[modeIndex.row()],
            modeIndex.row())
        msg.exec_()

    def window_close(self):
        os._exit(0)

class QTableView_Log(QTableView):
    def __init__(self, events):
        super().__init__()
        self.events = events
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)

        self.doubleClicked.connect(self.events.table_double_click)
        self.setSortingEnabled(False)

    def setColumsHeaderWidths(self):
        header = self.horizontalHeader()
        columnCount = header.count()
        for column in range(columnCount):
            if column != columnCount - 1:
                header.setSectionResizeMode(column, QHeaderView.ResizeToContents)
                header.setSectionResizeMode(column, QHeaderView.Interactive)
            else:
                header.setSectionResizeMode(column, QHeaderView.Stretch)

class Window(QWidget):
    events = None

    def __init__(self, log_data_processor, header, *args):
        QWidget.__init__(self, *args)

        self.title = Window_title()
        self.title.path = log_data_processor.log_file.path
        self.setGeometry(70, 150, 1326, 582)
        self.setWindowTitle(self.title.text)

        self.table_model = LogTableModel(self, log_data_processor)
        
        self.events = Events(self.table_model)

        self.table_view = QTableView_Log(self.events)
        self.table_view.setModel(self.table_model)
        self.table_view.setColumsHeaderWidths()

        layout = QVBoxLayout(self)
        layout.addWidget(self.table_view)
        self.setLayout(layout)
        self.table_view.scrollToBottom()

    def update_model(self, datalist, header):
        self.table_model2 = MyTableModel(self, dataList, header)
        self.table_view.setModel(self.table_model2)
        self.table_view.update()

    def closeEvent(self, event):
        event.accept()
        self.events.window_close()