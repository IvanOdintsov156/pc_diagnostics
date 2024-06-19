from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QFileDialog, QWidget, QVBoxLayout, QLabel,QPushButton
from datetime import datetime
import win32com.client
import os

class BIOSWorker(QThread):
    bios_info_updated = pyqtSignal(str)

    def run(self):
        while True:
            bios_info = self.get_bios_info()
            self.bios_info_updated.emit(bios_info)
            self.msleep(10000)  # Обновление каждые 10 секунд

    def get_bios_info(self):
        try:
            wmi = win32com.client.GetObject('winmgmts:')
            bios_info = wmi.InstancesOf('Win32_BIOS')
            bios_details = []
            for b in bios_info:
                details = f"Производитель: {b.Manufacturer}\n" \
                        f"Название: {b.Name}\n" \
                        f"Серийный номер: {b.SerialNumber}\n" \
                        f"Версия: {b.Version}"
                bios_details.append(details)
            return '\n\n'.join(bios_details)
        except Exception as e:
            print(f"Ошибка при получении информации о BIOS: {e}")
            return "Ошибка при получении информации. Проверьте консоль для деталей."

class BIOSWidget(QWidget):
    def __init__(self, parent=None):
        super(BIOSWidget, self).__init__(parent)
        self.initUI()
        self.start_worker()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.bios_info_label = QLabel('Информация о BIOS будет отображена здесь.')
        layout.addWidget(self.bios_info_label)

        self.save_button = QPushButton('Сохранить отчёт')
        self.save_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_button)

    def start_worker(self):
        self.worker = BIOSWorker()
        self.worker.bios_info_updated.connect(self.update_bios_info)
        self.worker.start()

    def update_bios_info(self, bios_info):
        self.bios_info_label.setText(bios_info)

    def save_report(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Выберите директорию для сохранения отчета')
        if dir_path:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            report_filename = os.path.join(dir_path, f"BIOS_Report_{timestamp}.txt")
            with open(report_filename, 'w', encoding='utf-8') as file:
                file.write(f"Отчет о BIOS: {timestamp}\n")
                file.write(self.bios_info_label.text())
    