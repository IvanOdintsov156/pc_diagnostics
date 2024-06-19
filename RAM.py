import sys
import psutil
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,QFileDialog,QPushButton
from PyQt6.QtCore import QThread, pyqtSignal
import os
from datetime import datetime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class UpdateThread(QThread):
    # Сигнал для отправки данных
    data_updated = pyqtSignal(float)

    def run(self):
        while True:
            ram_usage = psutil.virtual_memory().percent
            self.data_updated.emit(ram_usage)
            self.msleep(5000)  # Пауза на 1 секунду

class RAMDiagnostic(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Диагностика ОЗУ")
        self.setMinimumSize(400, 300)
        self.init_ui()
        self.update_thread = UpdateThread()
        self.update_thread.data_updated.connect(self.update_graph)
        self.update_thread.start()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)

        self.figure = Figure(facecolor='none')
        self.canvas = FigureCanvas(self.figure)
        self.layout.addWidget(self.canvas)

        self.info_label = QLabel('Информация об ОЗУ будет отображаться здесь')
        self.layout.addWidget(self.info_label)

        self.button_save = QPushButton('Сохранить отчёт', self)
        self.button_save.clicked.connect(self.save_report)
        self.layout.addWidget(self.button_save)

    def update_graph(self, ram_usage):
        # Проверяем, существует ли уже история использования ОЗУ
        if not hasattr(self, 'ram_usage_history'):
            self.ram_usage_history = []
            self.ax = self.figure.add_subplot(111)  # Создаем оси графика один раз
            self.ax.patch.set_facecolor('none')
            self.ax.yaxis.label.set_color('white')
            self.ax.xaxis.label.set_color('white')
            self.ax.tick_params(axis='x', colors='white')
            self.ax.tick_params(axis='y', colors='white')
            self.ax.title.set_color('white')
            self.line, = self.ax.plot([], [], '-o', label='Использование ОЗУ')  # Инициализируем линию графика

        self.ram_usage_history.append(ram_usage)
        self.ram_usage_history = self.ram_usage_history[-50:]  # Ограничиваем историю

        # Обновляем данные линии графика
        self.line.set_data(range(len(self.ram_usage_history)), self.ram_usage_history)
        self.ax.relim()  # Пересчитываем пределы осей
        self.ax.autoscale_view()  # Автоматически масштабируем оси

        self.ax.set_title('Использование ОЗУ во времени', color='white')
        self.ax.set_ylabel('Процент использования', color='white')
        self.ax.set_xlabel('Время (сек)', color='white')
        self.ax.legend(loc='upper right')

        self.canvas.draw()
        self.info_label.setText(f'Текущее использование ОЗУ: {ram_usage}%')

    
    def save_report(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Выберите директорию для сохранения отчета')
        if dir_path:
            timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            report_filename = os.path.join(dir_path, f"RAM_Report_{timestamp}.txt")
            with open(report_filename, 'w') as file:
                file.write(f"Отчет об использовании ОЗУ: {timestamp}\n")
                file.write(f"Использование ОЗУ {self.ram_usage_history[-1]}%\n")