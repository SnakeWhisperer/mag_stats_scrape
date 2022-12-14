import os
import requests

from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtCore import QRect, QPoint, QSize, QSettings
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QLabel, QHBoxLayout, QPushButton, QLineEdit)

from stats import scrape, dump_stats


class Worker(QRunnable):
    pass

class Window(QWidget):
    def __init__(self):
        super().__init__()

        # ------------------- Setting window size ----------------------
        self.screen = QApplication.primaryScreen()
        # rect = QRect(QPoint(), self.screen.size() * 0.3)
        rect = QRect(QPoint(), QSize(500, 200))
        rect.moveCenter(self.screen.geometry().center())
        self.setGeometry(rect)
        self.setMinimumWidth(rect.width())
        self.setMinimumHeight(rect.height())
        # --------------------------------------------------------------

        self.setWindowTitle('Stats')


        # --------------------------------------------------------------

        self.settings = QSettings('Magallanes Stats', 'Stats Scrape')
        if self.settings.value('last_scrape') is None:
            self.settings.setValue('last_scrape', '-')

        self.main_layout = QVBoxLayout(self)
        self.last_scrape_label = QLabel('Last scrape: ---')
        self.main_layout.addWidget(self.last_scrape_label, 0, QtCore.Qt.AlignLeft)

        self.status_label = QLabel('Status: Inactive')
        self.main_layout.addWidget(self.status_label, 0, QtCore.Qt.AlignLeft)

        self.top_layout = QHBoxLayout()
        self.mid_layout = QHBoxLayout()
        self.bottom_layout = QHBoxLayout()
        # self.main_layout.addLayout(self.top_layout)
        self.main_layout.addLayout(self.mid_layout)
        # self.main_layout.addLayout(self.bottom_layout)




        self.teams_label = QLabel('Teams: ')
        self.teams_edit = QLineEdit()
        self.scrape_button = QPushButton('Scrape')

        self.mid_layout.addWidget(self.teams_label)
        self.mid_layout.addWidget(self.teams_edit)
        self.mid_layout.addWidget(self.scrape_button)

        self.update_button = QPushButton('Update')
        self.main_layout.addWidget(self.update_button, 0, QtCore.Qt.AlignRight)








        # --------------------------------------------------------------

        self.scrape_button.clicked.connect(self.scrape_stats)
        self.scrape_button.clicked.connect(self.update_stats)

        # --------------------------------------------------------------

    def scrape_stats(self):
        pass

    def update_stats(self):
        pass


def get_internet_datetime(time_zone: str = "America/Caracas") -> datetime:
    """
    Get the current internet time from:
    'https://www.timeapi.io/api/Time/current/zone?timeZone=etc/utc'
    """
    timeapi_url = "https://www.timeapi.io/api/Time/current/zone"
    headers = {
        "Accept": "application/json",
    }
    params = {"timeZone": time_zone}

    dt = None
    try:
        request = requests.get(timeapi_url, headers=headers, params=params)
        r_dict = request.json()
        dt = datetime(
            year=r_dict["year"],
            month=r_dict["month"],
            day=r_dict["day"],
            hour=r_dict["hour"],
            minute=r_dict["minute"],
            second=r_dict["seconds"],
            microsecond=r_dict["milliSeconds"] * 1000,
        )
    except Exception:
        logger.exception("ERROR getting datetime from internet...")
        return None

    return dt


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())