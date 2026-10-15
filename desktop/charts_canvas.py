""" Import necessary modules """
from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


""" Class to create a scrollable figure canvas for matplotlib """
class ScrollableFigureCanvas(FigureCanvasQTAgg):
    """ Function to initialize the scrollable figure canvas """
    def __init__(
            self,
            figure,
            scroll_area=None,
            parent=None
    ):
        super().__init__(figure)

        self.setParent(parent)
        self.scroll_area = scroll_area

        self._is_dragging = False
        self._last_mouse_pos = QPoint()

        self.setCursor(Qt.CursorShape.ArrowCursor)

    """ Function to handle wheel events for scrolling """
    def wheelEvent(self, event: QWheelEvent):
        if self.scroll_area is None:
            event.ignore()
            return

        delta = event.angleDelta().y()

        vertical_scrollbar = (self.scroll_area.verticalScrollBar())

        vertical_scrollbar.setValue(vertical_scrollbar.value() - delta)

        event.accept()

    """ Function to handle mouse press events for dragging """
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._last_mouse_pos = (event.position().toPoint())

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

            event.accept()
            return

        super().mousePressEvent(event)

    """ Function to handle mouse move events for dragging """
    def mouseMoveEvent(self, event: QMouseEvent):
        if not self._is_dragging:
            super().mouseMoveEvent(event)
            return

        current_pos = (event.position().toPoint())
        delta = (current_pos - self._last_mouse_pos)

        self._last_mouse_pos = current_pos

        vertical_scrollbar = (self.scroll_area.verticalScrollBar())
        horizontal_scrollbar = (self.scroll_area.horizontalScrollBar())

        vertical_scrollbar.setValue(vertical_scrollbar.value() - delta.y())
        horizontal_scrollbar.setValue(horizontal_scrollbar.value() - delta.x())

        event.accept()

    """ Function to handle mouse release events for dragging """
    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False

            self.setCursor(Qt.CursorShape.ArrowCursor)

            event.accept()
            return

        super().mouseReleaseEvent(event)