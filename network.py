import psutil
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QPushButton,QScrollArea,QFileDialog
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import socket
import datetime
import os
class NetworkDiagnostics(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.data_history = {'bytes_sent': [], 'bytes_recv': []} 

    def initUI(self):
        # Настройка вкладок
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, "График")
        self.tabs.addTab(self.tab2, "Данные")

        # Настройка графика
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.graphLayout = QVBoxLayout(self.tab1)
        self.graphLayout.addWidget(self.canvas)

        # Настройка данных с прокруткой
        self.scrollArea = QScrollArea(self.tab2)  # Создание области прокрутки
        self.scrollArea.setWidgetResizable(True)  # Разрешение изменения размера виджета
        self.infoLabel = QLabel('Сетевая информация будет отображаться здесь')
        self.infoLabel.setWordWrap(True)  # Перенос слов в метке
        self.scrollArea.setWidget(self.infoLabel)  # Установка метки в качестве виджета для прокрутки

        self.dataLayout = QVBoxLayout(self.tab2)
        self.dataLayout.addWidget(self.scrollArea)  # Добавление области прокрутки в layout
        self.updateButton = QPushButton('Обновить данные')
        self.updateButton.clicked.connect(self.update_info)
        self.dataLayout.addWidget(self.updateButton)

        # Главный layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.button_save = QPushButton('Сохранить отчёт')
        self.button_save.clicked.connect(self.save_report)
        self.layout.addWidget(self.button_save)

        # Таймер для обновления графика
        self.timer = QTimer()
        self.timer.setInterval(1000)  # Обновление каждую секунду
        self.timer.timeout.connect(self.update_graph)
        self.timer.start()

    def update_graph(self):
        # Получение данных о сетевой активности
        net_io = psutil.net_io_counters()
        self.data_history['bytes_sent'].append(net_io.bytes_sent)
        self.data_history['bytes_recv'].append(net_io.bytes_recv)

        # Ограничение размера истории данных
        if len(self.data_history['bytes_sent']) > 60:  # Например, хранить данные за последнюю минуту
            self.data_history['bytes_sent'].pop(0)
            self.data_history['bytes_recv'].pop(0)

        # Обновление графика
        self.figure.clear()
        self.figure.patch.set_facecolor('none')  # Установка прозрачного фона для фигуры
        ax = self.figure.add_subplot(111)
        ax.patch.set_facecolor('none')
        ax.plot(self.data_history['bytes_sent'], label='Отправлено байт')
        ax.plot(self.data_history['bytes_recv'], label='Получено байт')
        ax.set_title('Сетевая активность')
        ax.set_xlabel('Время')
        ax.set_ylabel('Байты')
        ax.legend(loc='upper right')
        ax.tick_params(colors='white', labelcolor='white')
        ax.yaxis.label.set_color('white')
        ax.xaxis.label.set_color('white')
        ax.title.set_color('white')
        self.canvas.draw()

    def update_info(self):
        # Сбор информации о всех сетевых интерфейсах
        net_io = psutil.net_io_counters(pernic=True)
        net_addrs = psutil.net_if_addrs()
        info_text = ''
        for interface, stats in net_io.items():
            info_text += f'Интерфейс: {interface}\n' \
                        f'Отправлено байт: {stats.bytes_sent}\n' \
                        f'Получено байт: {stats.bytes_recv}\n'
            # Добавление адресной информации
            if interface in net_addrs:
                for addr in net_addrs[interface]:
                    if addr.family == socket.AF_INET:
                        info_text += f'IP адрес: {addr.address}\n' \
                                    f'Маска подсети: {addr.netmask}\n' \
                                    f'Широковещательный адрес: {addr.broadcast}\n'
            info_text += '\n'
        self.infoLabel.setText(info_text)


    def save_report(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Выберите директорию для сохранения отчета')
        if dir_path:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            report_filename = os.path.join(dir_path, f"Net_Report_{timestamp}.txt")
            with open(report_filename, 'w', encoding='utf-8') as file:
                file.write(f"Отчет по сетевой активности: {timestamp}\n")
                file.write(self.infoLabel.text())

