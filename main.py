"""
A tutorial courtesy of Mark Jay on youtube
An Audio spectrum analyzer
https://www.youtube.com/watch?v=RHmTgapLu4s&t=77s -- Let's Build an Audio Spectrum Analyzer in Python! (pt. 3)
Switching to PyQtGraph
"""

from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import sys
import struct
import pyaudio
from scipy.fftpack import fft


class AudioStream(object):
    def __init__(self):

        # Set up the pyqtgraph items
        self.traces = dict()
        self.phase = 0
        self.t = np.arange(0, 3.0, 0.01)
        self.app = QtGui.QApplication(sys.argv)
        self.win = pg.GraphicsWindow(title="Audio Analyzer")
        self.win.setGeometry(5,115, 1910, 900)
        self.win.setWindowTitle('Audio Analyzer')
        pg.setConfigOptions(antialias=True)

        # Give more meaningful x axis wf labels
        wf_xlabels = [(0, '0'), (2048, '2048'), (4096, '4096')]
        wf_xaxis = pg.AxisItem(orientation='bottom')
        wf_xaxis.setTicks([wf_xlabels])

        # Give more meaningful y axis wf labels
        wf_ylabels = [(0, '0'), (127, '128'), (255, '255')]
        wf_yaxis = pg.AxisItem(orientation='left')
        wf_yaxis.setTicks([wf_ylabels])

        # Using powers, give meaningful x axis labels for the spectrum
        sp_xlabels = [
            (np.log10(10), '10'), (np.log10(100), '100'),
            (np.log10(1000), '1000'), (np.log10(22050), '22050')
        ]
        sp_xaxis = pg.AxisItem(orientation='bottom')
        sp_xaxis.setTicks([sp_xlabels])

        # Put the graphs onto the frame
        self.waveform = self.win.addPlot(title="WAVEFORM", row=1, col=1, axisItems={'bottom': wf_xaxis, 'left':wf_yaxis},)
        self.spectrum = self.win.addPlot(title="SPECTRUM", row=2, col=1, axisItems={'bottom': sp_xaxis})

        # Initialise variables for the audio pickup
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2

        # Create a variable to read in the audio input
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK,
        )

        # Define the x points for the wf and spectrum
        self.x = np.arange(0, 2 * self.CHUNK, 2)
        self.f = np.linspace(0, self.RATE / 2, int(self.CHUNK / 2))

    # Start the application
    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    # A function to define the boundaries and assets of the 2 graphs
    def set_plotdata(self, name, data_x, data_y):
        if name in self.traces:
            self.traces[name].setData(data_x,data_y)
        else:
            if name == "waveform":
                self.traces[name] = self.waveform.plot(pen='c', width=3)
                self.waveform.setYRange(0, 255, padding=0)
                self.waveform.setXRange(0, 2 * self.CHUNK, padding=0.005)
            if name == "spectrum":
                self.traces[name] = self.spectrum.plot(pen='m', width=3)
                self.spectrum.setLogMode(x=True, y=True)
                self.spectrum.setYRange(-4, 0, padding=0)
                self.waveform.setXRange(np.log10(20), np.log10(self.RATE / 2), padding=0.005)

    # apply the audio input data to the graph for display
    def update(self):
        wf_data = self.stream.read(self.CHUNK)
        wf_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data)
        wf_data = np.array(wf_data, dtype='b')[::2] + 128  # double-precision floating-point number
        self.set_plotdata(name="waveform", data_x=self.x, data_y=wf_data)

        sp_data = fft(np.array(wf_data, dtype='int8') - 128)  # 8 bit integer number
        sp_data = np.abs(sp_data[0:int(self.CHUNK / 2)]) * 2 / (128 * self.CHUNK)
        self.set_plotdata(name="spectrum", data_x=self.f, data_y=sp_data)

    # Constantly update the graphs
    def animate(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()


if __name__ == "__main__":
    p = AudioStream()
    p.animate()
