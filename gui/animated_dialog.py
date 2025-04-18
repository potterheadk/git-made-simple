# gui/animated_dialog.py
from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect

class AnimatedDialog(QDialog):
    """Base dialog class with smooth animations"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowModality(Qt.ApplicationModal)
        self.animation = None

    def showEvent(self, event):
        """Animate the dialog when it's shown"""
        if not self.animation:
            self.animation = QPropertyAnimation(self, b"geometry")
            self.animation.setDuration(250)
            self.animation.setEasingCurve(QEasingCurve.OutCubic)

            # Save the target geometry
            target_geometry = self.geometry()

            # Start from a smaller size
            start_geometry = QRect(
                target_geometry.center().x() - target_geometry.width() * 0.4,
                target_geometry.center().y() - target_geometry.height() * 0.4,
                target_geometry.width() * 0.8,
                target_geometry.height() * 0.8
            )

            # Set up the animation
            self.animation.setStartValue(start_geometry)
            self.animation.setEndValue(target_geometry)
            self.animation.start()

        super().showEvent(event)
