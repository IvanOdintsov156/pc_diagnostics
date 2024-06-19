from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import GPUtil
import os
from datetime import datetime
from PyQt6.QtCore import QTimer

class GPUWidget(QWidget):
    def __init__(self, parent=None):
        super(GPUWidget, self).__init__(parent)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Создание фигуры с прозрачным фоном
        self.figure = Figure(facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        layout.addWidget(self.canvas)

        # QLabel для отображения информации о GPU
        self.gpu_info_label = QLabel('Информация о GPU будет отображена здесь.')
        layout.addWidget(self.gpu_info_label)

        # Кнопка для сохранения отчёта о GPU
        self.save_button = QPushButton('Сохранить отчёт')
        self.save_button.clicked.connect(self.save_report)
        layout.addWidget(self.save_button)

        # Таймер для обновления информации о GPU
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_gpu_info)
        self.update_timer.start(1000) 
        self.usage_data = []
        self.memory_used_data = []
        self.temperature_data = []

    def update_graph(self):
        # Получение и обновление данных о GPU
        gpus = GPUtil.getGPUs()
        gpu = gpus[0]
        self.usage_data.append(gpu.load * 100)
        self.memory_used_data.append(gpu.memoryUsed)
        self.temperature_data.append(gpu.temperature)

        # Очистка и обновление графика
        self.ax.clear()
        self.ax.set_facecolor('none')
        self.ax.plot(self.usage_data, label='Использование GPU (%)', alpha=0.5, color='white')
        self.ax.plot(self.memory_used_data, label='Использование памяти GPU (МБ)', alpha=0.5)
        self.ax.plot(self.temperature_data, label='Температура GPU (°C)', alpha=0.5)
        self.ax.set_xlabel('Время (с)', color='white')
        self.ax.set_ylabel('Значение', color='white')
        self.ax.set_title('Данные по мониторингу GPU', color='white')
        self.ax.legend(loc='upper right')
        self.canvas.draw_idle()

    def update_gpu_info(self):
        # Обновление графика и информации о GPU
        self.update_graph()
        gpus = GPUtil.getGPUs()
        gpu = gpus[0]
        gpu_info_text = f"Модель: {gpu.name}, Температура: {gpu.temperature}°C, 
        Использование: {gpu.load * 100}%, 
        Память: {gpu.memoryUsed}/{gpu.memoryTotal} MB"
        self.gpu_info_label.setText(gpu_info_text)

    def save_report(self):
        # Сохранение отчёта о GPU
        dir_path = QFileDialog.getExistingDirectory(self, 'Выберите директорию для сохранения отчета')
        if dir_path:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            report_filename = os.path.join(dir_path, f"GPU_Report_{timestamp}.txt")
            with open(report_filename, 'w', encoding='utf-8') as file:
                file.write(f"Дата: {timestamp}\n")
                file.write(f"{self.gpu_info_label.text()}\n")
