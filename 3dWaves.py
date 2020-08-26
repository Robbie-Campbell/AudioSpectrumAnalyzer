"""
A further development of mark jays audio spectrum analyzer but in 3d!
Link - https://www.youtube.com/watch?v=YUOkOzVQTvY&t=909s -- Audio Reactive Visualizer using PyQtGraph, OpenGL,
and PyAudio!
It's making a little more sense!
"""

import numpy as np
import struct
import pyaudio
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import sys
from opensimplex import OpenSimplex


class Terrain(object):
    def __init__(self):

        # Set up the GUI
        self.app = QtGui.QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.setGeometry(0, 30, 1920, 1050)
        self.window.show()
        self.window.setWindowTitle("Let's Fly!")
        self.window.setCameraPosition(distance=30, elevation=12)

        # Define variables for the wave
        self.nsteps = 1.3
        self.offset = 0
        self.ypoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.xpoints = np.arange(-20, 20 + self.nsteps, self.nsteps)
        self.nfaces = len(self.ypoints)
        self.noise = OpenSimplex()
        self.offset = 0

        # Define audio input variables
        self.RATE = 44100
        self.CHUNK = len(self.xpoints) * len(self.ypoints)

        # Read in audio data
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self.RATE,
            input=True,
            output=True,
            frames_per_buffer=self.CHUNK
        )

        # Define these variables by using the mesh() function
        verts, faces, colors = self.mesh()

        self.mesh1 = gl.GLMeshItem(
            vertexes=verts,
            faces=faces,
            faceColors=colors,
            drawEdges=True,
            smooth=False
        )

        # Put the mesh on the screen
        self.mesh1.setGLOptions('additive')
        self.window.addItem(self.mesh1)

    def mesh(self, offset=0, height=2.5, wf_data=None):

        # Condition to make sure that the wf_data is not null
        if wf_data is not None:
            wf_data = struct.unpack(str(2 * self.CHUNK) + 'B', wf_data)
            wf_data = np.array(wf_data, dtype='b')[::2] + 128
            wf_data = np.array(wf_data, dtype='int32') - 128
            wf_data = wf_data * 0.04
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))

        # So that the app doesn't break
        else:
            wf_data = np.array([1] * 1024)
            wf_data = wf_data.reshape((len(self.xpoints), len(self.ypoints)))

        # Define the position of all of the geometry on the grid, the wf_data array determines the height of each of the
        # peaks and the noise makes it semi random how high the peaks will be
        verts = np.array([
            [
                x, y, wf_data[xid][yid] * self.noise.noise2d(x=xid / 12 + offset, y=yid / 12 + offset),
            ] for xid, x in enumerate(self.xpoints) for yid, y in enumerate(self.ypoints)
        ], dtype=np.float32)

        # Variables to be later appended to
        faces = []
        colors = []

        # Generate all of the positions of the geometry and create color variety
        for m in range(self.nfaces - 1):
            yoff = m * self.nfaces
            for n in range(self.nfaces - 1):
                faces.append([n + yoff, yoff + n + self.nfaces, yoff + n + self.nfaces + 1])
                faces.append([n + yoff, yoff + n + 1, yoff + n + self.nfaces + 1])
                colors.append([n / self.nfaces, 1 - n / self.nfaces, m / self.nfaces, 0.7])
                colors.append([n / self.nfaces, 1 - n / self.nfaces, m / self.nfaces, 0.8])

        # Define the data types
        faces = np.array(faces, dtype=np.uint32)
        colors = np.array(colors, dtype=np.float32)

        return verts, faces, colors

    # Start the application
    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    # Check for changes on each frame
    def update(self):
        wf_data = self.stream.read(self.CHUNK)
        verts, faces, colors = self.mesh(offset=self.offset, wf_data=wf_data)
        self.mesh1.setMeshData(vertexes=verts, faces=faces, faceColors=colors)
        self.offset -= 0.05

    # The 3d animation timer
    def animation(self, frametime=5):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(frametime)
        self.start()
        self.update()


# Run the app
if __name__ == "__main__":
    t = Terrain()
    t.animation()
