#!/usr/bin/env python3

"""
Attempt at implementation of graphing class with PyQt5
Based on elacticnodes.py example from Riverbank Computing Limited
"""
__author__ = "Aryeh Zapinsky"

import math

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Node(QGraphicsItem):
    Type = QGraphicsItem.UserType + 1

    def __init__(self, graphWidget, information):
        super(Node, self).__init__()

        self.graph = graphWidget
        self.information = information
        self.newPos = QPointF()

        self.setZValue(1)

    def type(self):
        return Node.Type

    #TODO: this needs to be fixed
    def boundingRect(self):
        adjust = 2.0
        return QRectF(-20 - adjust, -20 -adjust,
                     40 + adjust, 40 + adjust)
    '''
    #Not sure this is necessay, if no collisions
    def shape(self):
        rect = QRectF(self.boundingRect())
        path = QPainterPath()
        path.addEllipse(rect)
        return path
    '''
    def paint(self, painter, option, widget):
        rect = QRectF(self.boundingRect())
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.cyan)
        painter.drawEllipse(rect)

        font = painter.font()
        font.setPointSize(3)
        painter.setFont(font)

        painter.setPen(Qt.black)
        painter.drawText(rect,
                         Qt.AlignCenter,
                         self.information)

    #TODO: implement this properly
    def mousePressEvent(self, event):
        super(Node, self).mousePressEvent(event)


    #TODO: implement this properly
    def mouseReleaseEvent(self, event):
        super(Node, self).mouseReleaseEvent(event)


class GraphWidget(QGraphicsView):
    def __init__(self, listings):
        super(GraphWidget, self).__init__()

        dim = 500
        scene = QGraphicsScene(self)
        self.setGeometry(QRect(dim/2, dim/2, dim, dim))
        self.setScene(scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorViewCenter)

        scene.setSceneRect(QRectF())

        xpos = 0
        ypos = 0
        squareDim = math.ceil(math.sqrt(len(listings)))

        for listing in listings:
            item = Node(self, *listing)
            scene.addItem(item)
            item.setPos(xpos, ypos)
            item.setPos(xpos * (dim/10), ypos * (dim/10))

            xpos += 1
            if xpos == squareDim:
                xpos %= squareDim
                ypos += 1

        self.scale(0.8, 0.8)
        self.setMinimumSize(400, 400)
        self.setWindowTitle("Mapper: Mapping the Columbia Directory of Courses")

    def keyPressEvent(self, event):
        key = event.key()

        if key == Qt.Key_Plus:
            self.scaleView(1.2)
        elif key == Qt.Key_Minus:
            self.scaleView(1 / 1.2)
        elif key == Qt.Key_Escape:
            self.close()

        else:
            super(GraphWidget, self).keyPressEvent(event)

    def wheelEvent(self, event):
        self.scaleView(math.pow(2.0, -event.angleDelta().y() / 240.0))

    def scaleView(self, scaleFactor):
        factor = self.transform().scale(scaleFactor, scaleFactor).mapRect(
            QRectF(0, 0, 1, 1)).width()

        if factor < 0.07 or factor > 100:
            return

        self.scale(scaleFactor, scaleFactor)

if __name__ == '__main__':

    import sys
    import mapper

    app = QApplication(sys.argv)

    data = mapper.start()
    widget = GraphWidget(data)
    widget.show()

    sys.exit(app.exec_())
