#!/usr/bin/env python2

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from PyQt4 import QtSvg,QtCore,QtGui,Qt
import sys
import signal

class SvgWidget(QtSvg.QSvgWidget):
    location_changed = QtCore.pyqtSignal(QtCore.QPointF)
    
    def updateViewBox(self, size):
        w = self.scale * size.width()
        h = self.scale * size.height()
        r = QtCore.QRectF(self.center_x - w/2, self.center_y - h/2,
                         w, h)
        self.renderer().setViewBox(r)
        
    def center(self):
        self.scale=max(float(self.defViewBox.width())/self.width(),
                       float(self.defViewBox.height())/self.height())
        self.center_x = self.defViewBox.center().x()
        self.center_y = self.defViewBox.center().y()
        self.updateViewBox(self.size())
        self.repaint()

    def load(self, path):
        QtSvg.QSvgWidget.load(self, path)
        self.defViewBox = self.renderer().viewBoxF()
        self.center()
        
    def resizeEvent(self, evt):
        self.updateViewBox( evt.size())
        QtSvg.QSvgWidget.resizeEvent(self, evt)
        
    def __init__(self):
        QtSvg.QSvgWidget.__init__(self)
        self.setMouseTracking(True)
        self.ds = None
        self.scale = 0
        self.center_x = 0
        self.center_y = 0
        self.setPalette( QtGui.QPalette( QtCore.Qt.white ) );
        self.setAutoFillBackground(True)
        
    def updateLocation(self, pos):
        self.location_changed.emit(QtCore.QPointF(
                (pos.x() - self.width()/2)*self.scale + self.center_x, 
                (pos.y() - self.height()/2)*self.scale + self.center_y))

    def wheelEvent(self, evt):
        self.scale = self.scale * 1.0025**(-evt.delta());
        self.updateViewBox(self.size())
        self.updateLocation(evt.pos())
        self.repaint()

    def mousePressEvent(self, evt):
        self.ds = evt.posF()
        self.start_center_x = self.center_x
        self.start_center_y = self.center_y
        
    def mouseMoveEvent(self, evt):
        self.updateLocation(evt.posF())
        if not self.ds: return
        dx = evt.posF().x() - self.ds.x()
        dy = evt.posF().y() - self.ds.y()
        self.center_x = self.start_center_x - dx*self.scale
        self.center_y = self.start_center_y - dy*self.scale
        self.updateViewBox(self.size())
        self.repaint()

    def mouseReleaseEvent(self, evt):
        self.mouseMoveEvent(evt)
        self.ds = None

def tr(s):
    return QtGui.QApplication.translate("SvgViewer", s, None, QtGui.QApplication.UnicodeUTF8)

class MainWindow(QtGui.QMainWindow):
    def showLocation(self, point):
        self.statusbar.showMessage("%f %f"%(point.x(), point.y()))

    def open(self):
        path = QtGui.QFileDialog.getOpenFileName(
            self, "Open File", filter=tr("Svg documents (*.svg);;Any files (*.*)"))
        if path: self.svg.load(path)

    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.svg = SvgWidget()
        self.setCentralWidget(self.svg)
        self.resize(800, 600)
        self.statusbar = QtGui.QStatusBar(self)
        self.setStatusBar(self.statusbar)
        self.svg.location_changed.connect(self.showLocation)
        
        self.menubar = QtGui.QMenuBar(self)
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.setMenuBar(self.menubar)
        
        self.actionOpen = QtGui.QAction(self)
        self.actionOpen.setShortcuts(QtGui.QKeySequence.Open);
        self.actionQuit = QtGui.QAction(self)
        self.actionQuit.setShortcuts(QtGui.QKeySequence.Quit);
        self.actionCenter = QtGui.QAction(self)
        self.actionCenter.setShortcuts(QtGui.QKeySequence(tr("Space")));
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuEdit.addAction(self.actionCenter)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())

        self.actionCenter.triggered.connect(self.svg.center)
        self.actionQuit.triggered.connect(self.close)
        self.actionOpen.triggered.connect(self.open)

        self.setWindowTitle(tr("Svg Viewer"))
        self.menuFile.setTitle(tr("&File"))
        self.menuEdit.setTitle(tr("&Edit"))
        self.actionOpen.setText(tr("&Open"))
        self.actionQuit.setText(tr("&Quit"))
        self.actionCenter.setText(tr("&Center"))
        
def handleIntSignal(signum, frame):
    QtGui.qApp.closeAllWindows()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    
    if len(app.arguments()) > 2 or '-h' in app.arguments()[1:] or '--help' in app.arguments()[1:]:
        print "Usage: svg_view.py <path_to_svg_file>?"
        exit

    window = MainWindow()
    window.show()

    
    if len(app.arguments()) > 1:
        window.svg.load(app.arguments()[1])

    #This is a hack to let the interperter run once every 1/2 second to catch sigint
    timer = QtCore.QTimer()
    timer.start(500)  
    timer.timeout.connect(lambda: None)
    signal.signal(signal.SIGINT, handleIntSignal)
    
    sys.exit(app.exec_())



