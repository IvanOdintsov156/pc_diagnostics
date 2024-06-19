import psutil
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QComboBox)
from PyQt6.QtCore import QThread, pyqtSignal
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from datetime import datetime
import os

class DiskInfoThread(QThread):
    data_ready = pyqtSignal(dict)

    def __init__(self, disk_name):
        super().__init__()
        self.disk_name = disk_name

    def run(self):
        disk_usage = psutil.disk_usage(self.disk_name)
        self.data_ready.emit({'total': disk_usage.total, 'used': disk_usage.used, 'free': disk_usage.free})
        self.msleep(5000)  # Используйте msleep для ожидания в миллисекундах

class DiskInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Информация о дисках')
        self.setGeometry(100, 100, 600, 400)
        layout = QVBoxLayout()

        self.disk_selector = QComboBox(self)
        self.disk_selector.addItems([disk.device for disk in psutil.disk_partitions()])
        self.disk_selector.setCurrentIndex(0)  # Выбрать диск C по умолчанию
        self.disk_selector.currentTextChanged.connect(self.update_disk_info)
        layout.addWidget(self.disk_selector)

        self.figure = Figure(facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        self.plot_disk_usage
        layout.addWidget(self.canvas)

        self.save_button = QPushButton('Сохранить отчёт', self)
        self.save_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.show()

    def update_disk_info(self, disk_name):
        self.thread = DiskInfoThread(disk_name)
        self.thread.data_ready.connect(self.plot_disk_usage)
        self.thread.start()

    def plot_disk_usage(self, data):
        self.figure.clear()
        self.figure.patch.set_facecolor('none')  # Установка прозрачного фона для фигуры
        ax = self.figure.add_subplot(111)
        used_percent = data['used'] / (data['total'])
        free_percent = data['free'] / (data['total'])
        ax.pie([used_percent, free_percent], labels=['%d%% Использовано' % (used_percent * 100), 
                                                     '%d%% Свободно' % (free_percent * 100)], 
                                                     colors=['#ff9999', '#66b3ff'], startangle=90,
                                                       textprops={'color':'white'})
        ax.axis('equal')  # Для круглого пирога
        self.canvas.draw()

    def save_report(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Выберите директорию для сохранения отчета')
        if not dir_path:
            return
        disk_name = self.disk_selector.currentText().replace(':', '-').replace('\\', '').replace('/', '')
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        report_filename = os.path.join(dir_path, f"Disk_Usage_Report_{disk_name}_{timestamp}.txt")
        try:
            with open(report_filename, 'w', encoding='utf-8') as file:
                file.write(f"Отчет об использовании диска: {disk_name}\nДата: {timestamp}\n")
                disk_usage = psutil.disk_usage(self.disk_selector.currentText())
                file.write(f"Итого: {disk_usage.total:.2f} МБ\nИспользовано: {disk_usage.used:.2f} МБ\nСвободно: {disk_usage.free:.2f} МБ\n")
        except OSError as e:
            print(f"Ошибка при сохранении файла: {e}")

