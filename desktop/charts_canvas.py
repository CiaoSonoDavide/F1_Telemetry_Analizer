from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QMouseEvent, QWheelEvent
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg


class ScrollableFigureCanvas(FigureCanvasQTAgg):
    def __init__(self, figure, scroll_area=None, parent=None):
        super().__init__(figure)

        self.setParent(parent)
        self.scroll_area = scroll_area

        self._is_dragging = False
        self._last_mouse_pos = QPoint()

        self.setCursor(Qt.CursorShape.ArrowCursor)

    def wheelEvent(self, event: QWheelEvent):
        if self.scroll_area is None:
            event.ignore()
            return

        delta = event.angleDelta().y()

        vertical_scrollbar = (self.scroll_area.verticalScrollBar())

        vertical_scrollbar.setValue(vertical_scrollbar.value() - delta)

        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._last_mouse_pos = (event.position().toPoint())

            self.setCursor(Qt.CursorShape.ClosedHandCursor)

            event.accept()
            return

        super().mousePressEvent(event)

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

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_dragging = False

            self.setCursor(Qt.CursorShape.ArrowCursor)

            event.accept()
            return

        super().mouseReleaseEvent(event)