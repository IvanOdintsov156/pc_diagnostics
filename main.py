import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QSplitter, QListWidget,
                             QStackedWidget, QWidget, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

from storages import DiskInfoApp
from CPU import CPUDiagnostic
import qt_material
from qt_material import apply_stylesheet
import process
import RAM
import network
import GPU
import BIOS
import system
class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Система мониторинга')
        self._current_theme = 'dark_blue'
        self.create_menu()
        self.initUI()

    def create_menu(self):
        self.theme_menu = self.menuBar().addMenu('Темы')
        for theme in qt_material.list_themes():
            action = self.theme_menu.addAction(theme)
            action.triggered.connect(self.change_theme)

    def change_theme(self):
        action = self.sender()
        self._current_theme = action.text()
        apply_stylesheet(self, theme=self._current_theme)

    def initUI(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.componentsList = QListWidget()
        self.componentsList.addItems(['Диски', 'ОЗУ', 'Процессор', 'Сеть', 'Процессы ОС', 'Система','GPU', 'BIOS'])
        splitter.addWidget(self.componentsList)

        self.infoStack = QStackedWidget()
        splitter.addWidget(self.infoStack)

        for component in ['Диски', 'ОЗУ', 'Процессор', 'Сеть', 'Процессы ОС', 'Система','GPU', 'BIOS']:
            widget = self.create_widget(component)
            self.infoStack.addWidget(widget)

        self.componentsList.currentRowChanged.connect(
            self.infoStack.setCurrentIndex)

        self.setCentralWidget(splitter)
        self.setMinimumSize(800, 600)
        self.setMaximumSize(800, 600)
        self.show()

    def create_widget(self, text):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        if text == 'Диски':
            disk_usage = DiskInfoApp()
            layout.addWidget(disk_usage)
        if text == 'ОЗУ':
            label = RAM.RAMDiagnostic()
            layout.addWidget(label)
        elif text == 'Процессор':
            label = CPUDiagnostic()
            layout.addWidget(label)
        elif text == 'Сеть':
            label = network.NetworkDiagnostics()
            layout.addWidget(label)

        elif text == 'Система':
            label = system.SystemInfo()
            layout.addWidget(label)

        elif text == 'Процессы ОС':
            label = process.ProcessesTable()
            layout.addWidget(label)

        elif text == 'BIOS':
            label = BIOS.BIOSWidget()
            layout.addWidget(label)

        elif text == 'GPU':
            label = GPU.GPUWidget()
            layout.addWidget(label)
            
        return widget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName('Система мониторинга')
    app.setApplicationDisplayName('Система мониторинга')
    app.setApplicationVersion('1.0.0')
    app.setWindowIcon(QIcon('icon.ico'))
    apply_stylesheet(app, theme='dark_blue.xml')
    main_window = MainApp()
    sys.exit(app.exec())