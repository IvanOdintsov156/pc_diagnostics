import psutil
import platform
from datetime import datetime
from PyQt6.QtWidgets import QPushButton, QTextEdit, QVBoxLayout, QWidget, QFileDialog
import os

class SystemInfo(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.info_display = QTextEdit(self)
        self.info_display.setReadOnly(True)
        self.save_button = QPushButton('Сохранить отчёт', self)
        self.save_button.clicked.connect(self.save_report)

        layout = QVBoxLayout()
        layout.addWidget(self.info_display)
        layout.addWidget(self.save_button)
        self.setLayout(layout)

        self.setWindowTitle('Информация об ОС')
        self.display_info()

    def display_info(self):
        info = f"Информация об ОС:\n"
        info += f"Система: {platform.system()}\n"
        info += f"Релиз: {platform.release()}\n"
        info += f"Версия: {platform.version()}\n"
        info += f"Архитектура: {platform.machine()}\n"
        info += f"Процессор: {platform.processor()}\n"
        info += f"Физические ядра: {psutil.cpu_count(logical=False)}\n"
        info += f"Все ядра: {psutil.cpu_count(logical=True)}\n"
        info += f"Использование RAM: {psutil.virtual_memory().percent}%\n"
        self.info_display.setText(info)

    def save_report(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Выберите директорию для сохранения отчета')
        if dir_path:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            report_filename = os.path.join(dir_path, f"OS_Report_{timestamp}.txt")
            with open(report_filename, 'w', encoding='utf-8') as file:
                file.write(f"Отчет об ОС: {timestamp}\n")
                file.write(self.info_display.toPlainText())
            print(f"Отчёт сохранён в файле: {report_filename}")
