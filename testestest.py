import numpy as np
import pyqtgraph as pg 
from tdms_viewer import *
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider
from PyQt5.QtCore import Qt, QTimer

class GUI(QMainWindow):
    def __init__(self, plot_dpi=100):
        super().__init__()
        self.tdms_data, self.tdms_path = tdms_viewer()
        self.dpi = plot_dpi
        self.initUI()
        self.Animation()
        self.Timebar()
        self.Quit()
        # self.Plot(0)

    def initUI(self):
        self.setGeometry(100, 100, 1000, 800)
        self.setWindowTitle("Data Visualizer 0.1")
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        tdms_file = self.tdms_path
        channel_data = tdms_file._channel_data
        self.channels = list(channel_data.keys())
        self.create_plot_widgets()

    def create_plot_widgets(self):
        self.plot_widgets = []
        for channel_name in self.channels[:-4]:
            plot_widget = pg.PlotWidget()
            plot_widget.setLabel('bottom', 'Zeitstempel')
            plot_widget.setLabel('left', channel_name)
            self.plot_widgets.append(plot_widget)
            self.layout.addWidget(plot_widget)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

    def Animation(self):
        # Animation
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.start_stop_button)
        self.layout.addWidget(self.play_button)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_line)
        
        self.slider_value = 0
        self.animation_speed = 1 # milliseconds
        self.playing = False

    def Timebar(self):
        # Timebar
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setMinimum(0)
        self.time_slider.setMaximum(len(self.tdms_data["Zeitstempel"])-1)
        self.time_slider.setTickInterval(int(len(self.tdms_data["Zeitstempel"])/10))
        self.time_slider.setSingleStep(1)
        self.time_slider.sliderMoved.connect(self.on_time_slider_change)
        self.layout.addWidget(self.time_slider)

    def Quit(self):
        # Quit
        quit_button = QPushButton("Quit")
        quit_button.clicked.connect(self.close)
        self.layout.addWidget(quit_button)

    def Plot(self, slider_value):
        for idx, ch in enumerate(self.channels[0:-4]):
            channel_name = ch.split("/'")[2].replace("'", "")
            if channel_name == "Zeitstempel":
                continue
            
            # Common plot properties
            plot_widget = self.plot_widgets[idx]
            plot_widget.setTitle(channel_name)
            plot_widget.setXRange(0, self.tdms_data["Zeitstempel"][-1])
            max_value = self.tdms_data[channel_name].max()
            plot_widget.setYRange(-0.05 * max_value, 1.05 * max_value)
            
            if idx == 0:
                # Scatter plot for the first channel
                plot_widget.plot(self.tdms_data["Zeitstempel"], self.tdms_data[channel_name], pen=None, symbol='+', symbolSize=0.05)
            else:
                # Line plot for subsequent channels
                plot_widget.plot(self.tdms_data["Zeitstempel"], self.tdms_data[channel_name], pen=None, symbol='+', symbolSize=0.05)
            
            # Vertical line
            vline = pg.InfiniteLine(pos=self.tdms_data["Zeitstempel"][slider_value], angle=90, movable=True, pen='r')
            plot_widget.addItem(vline)

    # Function for the slider
    def on_time_slider_change(self, slider_value):
        for k, ch in enumerate(self.channels[0:-4]):
            plot_widget = self.plot_widgets[k]
            for item in plot_widget.items():
                if isinstance(item, pg.InfiniteLine):
                    plot_widget.removeItem(item)

            channel_name = ch.split("/'")[2].replace("'", "")
            if channel_name == "Zeitstempel":
                continue
            vline = pg.InfiniteLine(pos=self.tdms_data["Zeitstempel"][slider_value], angle=90, movable=True, pen='r')
            plot_widget.addItem(vline)

    def start_stop_button(self):
        if not self.playing:
            self.playing = True
            self.timer.start(self.animation_speed)
        else:
            self.playing = False
            self.timer.stop()

    def update_line(self):
        current_value = self.time_slider.value()
        new_value = current_value + 100
        self.time_slider.setValue(new_value)
        self.on_time_slider_change(new_value)
        if self.slider_value == len(self.tdms_data["Zeitstempel"]):
            self.timer.stop()
            self.playing = False


app = QApplication([])
window = GUI()
window.show()
app.exec_()
