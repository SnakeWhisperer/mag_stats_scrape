import functools
import os
import requests
import sys
import time
import traceback

from datetime import datetime
from PyQt5 import QtCore
from PyQt5.QtCore import (QRect, QPoint, QSize, QSettings, QRunnable,
                          QThreadPool, pyqtSlot, pyqtSignal, QObject)
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QLabel, QHBoxLayout, QPushButton, QLineEdit)

from stats import scrape, scrape_team, dump_stats


class WorkerSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object)

class Worker(QRunnable):

    def __init__(self, team):
        super().__init__()
        self.team = team
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        stats = scrape_team(self.team)
        self.signals.result.emit(stats)
        self.signals.finished.emit()


class DumpWorker(QRunnable):
    def __init__(self, stats):
        super().__init__()
        self.stats = stats
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        log = dump_stats(self.stats)
        self.signals.result.emit(log)
        self.signals.finished.emit()

class StatusWorker(QRunnable):
    pass


class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

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
        self.last_scrape_label = QLabel(f'Last scrape: {self.settings.value("last_scrape")} (not available)')
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

        self.update_button.setEnabled(False)

        self.teams_dict = {
            'zul': (0, 'Aguilas'),
            'mar': (1, 'Bravos'),
            'lar': (2, 'Cardenales'),
            'anz': (3, 'Caribes'),
            'car': (4, 'Leones'),
            'mag': (5, 'Navegantes'),
            'lag': (6, 'Tiburones'),
            'ara': (7, 'Tigres'),
        }

        self.stats = {
            0: {'name': 'Aguilas', 'hitting': [], 'pitching': []},
            1: {'name': 'Bravos', 'hitting': [], 'pitching': []},
            2: {'name': 'Cardenales', 'hitting': [], 'pitching': []},
            3: {'name': 'Caribes', 'hitting': [], 'pitching': []},
            4: {'name': 'Leones', 'hitting': [], 'pitching': []},
            5: {'name': 'Navegantes', 'hitting': [], 'pitching': []},
            6: {'name': 'Tiburones', 'hitting': [], 'pitching': []},
            7: {'name': 'Tigres', 'hitting': [], 'pitching': []}
        }

        # --------------------------------------------------------------

        self.scrape_button.clicked.connect(self.scrape_stats)
        self.update_button.clicked.connect(self.update_stats)

        # --------------------------------------------------------------

        self.num_teams = 0

    def save_stats(self, stats):
        self.stats[self.teams_dict[self.current_team][0]]['hitting'] = stats[0]
        self.stats[self.teams_dict[self.current_team][0]]['pitching'] = stats[1]


    def scrape_stats(self):
        teams_list = self.teams_edit.text().split(',')
        teams_list = [team.strip() for team in teams_list]
        self.num_teams = len(teams_list)
        self.team_count = 0
        self.scrape_button.setEnabled(False)

        self.call_worker(teams_list, 0)

    def call_worker(self, teams_list, index):
        if index >= len(teams_list):
            self.scrape_button.setEnabled(True)
            self.status_label.setText(f'Status: Inactive')
            self.update_button.setEnabled(True)
            date_time = get_internet_datetime()
            self.settings.setValue('last_scrape', date_time)
            self.last_scrape_label.setText(f'Last scrape: {date_time} (available)')
        else:
            if teams_list[index] in self.teams_dict.keys():
                self.current_team = teams_list[index]
                self.status_label.setText(f'Status: Working on {self.teams_dict[teams_list[index]][1]} ({(index+1)}/{len(teams_list)})')
                self.worker = Worker(teams_list[index])
                self.worker.signals.finished.connect(functools.partial(self.call_worker, teams_list, index+1))
                self.worker.signals.result.connect(self.save_stats)

                self.threadpool.start(self.worker)

    def update_stats(self):
        self.dump_worker = DumpWorker(self.stats)
        self.status_label.setText('Status: Updating stats')
        self.threadpool.start(self.dump_worker)
        self.dump_worker.signals.finished.connect()
        self.dump_worker.signals.result.connect(self.save_log)

    def save_log(self, log):
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
        # logger.exception("ERROR getting datetime from internet...")
        return None

    return dt


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())