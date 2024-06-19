import psutil
from PyQt6.QtWidgets import (QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QFileDialog)
from PyQt6.QtCore import QTimer
from datetime import datetime
import os

class ProcessesTable(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_table)
        self.timer.start(5000)  # Обновление каждую секунду

    def initUI(self):
        # Настройка таблицы
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['PID', 'Имя', 'Пользователь', 'CPU%'])
        font = self.table.font()
        font.setPointSize(8)
        self.table.setFont(font)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        # Кнопка для сохранения отчета
        self.save_report_button = QPushButton('Сохранить отчет', self)
        self.save_report_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_report_button)
        self.setLayout(layout)

    def update_table(self):
        processes = list(psutil.process_iter(['pid', 'name', 'username', 'cpu_percent']))
        self.table.setRowCount(len(processes))
        for i, proc in enumerate(processes):
            self.table.setItem(i, 0, QTableWidgetItem(str(proc.info['pid'])))
            self.table.setItem(i, 1, QTableWidgetItem(proc.info['name']))
            self.table.setItem(i, 2, QTableWidgetItem(proc.info['username']))
            self.table.setItem(i, 3, QTableWidgetItem(str(proc.info['cpu_percent'])))

    def save_report(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Выберите директорию для сохранения отчета')
        if dir_path:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            report_filename = os.path.join(dir_path, f"Processes_Report_{timestamp}.txt")
            try:
                with open(report_filename, 'w', encoding='utf-8') as file:
                    file.write(f"Отчет о процессах: {timestamp}\n")
                    for i in range(self.table.rowCount()):
                        pid = self.table.item(i, 0).text()
                        name = self.table.item(i, 1).text()
                        user = self.table.item(i, 2).text()
                        cpu_usage = self.table.item(i, 3).text()
                        file.write(f"{pid}\t{name}\t{user}\t{cpu_usage}%\n")
            except OSError as e:
                print(f"Ошибка при сохранении файла: {e}")
