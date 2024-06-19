import sys
import psutil
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,QPushButton,QFileDialog
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import os
from datetime import datetime

class CPUDiagnostic(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Диагностика процессора")
        self.setMinimumSize(400, 300)
        self.cpu_count_logical, self.cpu_count_physical = map(
            psutil.cpu_count, (True, False)
        )
        self.init_ui()
        self.init_timer()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.figure = Figure(facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.info_label = QLabel()
        self.layout.addWidget(self.info_label)

        self.save_button = QPushButton('Сохранить отчет', self)
        self.save_button.clicked.connect(self.save_report)
        self.layout.addWidget(self.save_button)

        self.update_labels()

    def init_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_cpu_data)
        self.timer.start(5000)  # Обновление каждую секунду

    def update_cpu_data(self):
        cpu_core_load = psutil.cpu_percent(interval=None, percpu=True)
        self.update_graph(cpu_core_load)
        self.update_labels()

    def update_labels(self):
        self.cpu_freq = psutil.cpu_freq().current
        self.cpu_load = psutil.cpu_percent(interval=1)
        self.cpu_core_load = psutil.cpu_percent(interval=1, percpu=True)

        info_text = f"Логических ядер: {self.cpu_count_logical}\n" \
                    f"Физических ядер: {self.cpu_count_physical}\n" \
                    f"Частота CPU: {self.cpu_freq:.2f} MHz\n" \
                    f"Загрузка CPU: {self.cpu_load}%\n"
        for i, load in enumerate(self.cpu_core_load):
            info_text += f"Ядро {i}: {load}%\n"
        self.info_label.setText(info_text.strip())

    def update_graph(self, cpu_core_load):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.patch.set_facecolor('none')
        ax.bar(range(len(cpu_core_load)), cpu_core_load)
        ax.set_title('Загрузка ядер CPU', color='white')
        ax.set_ylabel('Процент загрузки', color='white')
        ax.set_xlabel('Номер ядра', color='white')
        self.canvas.draw()

    def save_report(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Выберите директорию для сохранения отчета')
        if dir_path:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            report_filename = os.path.join(dir_path, f"CPU_Report_{timestamp}.txt")
            with open(report_filename, 'w') as file:
                file.write(f"Отчет о загрузке CPU: {timestamp}\n")
                file.write(f"Логических ядер: {self.cpu_count_logical}\n")
                file.write(f"Физических ядер: {self.cpu_count_physical}\n")
                file.write(f"Частота CPU: {self.cpu_freq:.2f} MHz\n")
                file.write(f"Загрузка CPU: {self.cpu_load}%\n")
                for i, load in enumerate(self.cpu_core_load):
                    file.write(f"Ядро {i}: {load}%\n")
