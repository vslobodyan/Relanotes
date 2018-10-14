import logging
import os
import sqlite3

from PyQt5 import QtCore

from relanotes.routines import give_correct_path_under_win_and_other, get_path_to_app


class Settings():
    """ Класс настроек приложения. И основных переменных, относящихся к концигурации и местоположению. """

    NameOrganization = 'DigiTect'
    NameGlobal = 'Relanotes'
    Name = 'RelaNotes'
    config_path = ''   # Путь к файлам локальных настроек программы
    path_to_notes = '' # Путь к каталогу с заметками
    path_to_app = ''   # Путь к исходникам (или выполняемым файлам) приложения
    logfile = ''        # Путь к лог-файлу
    log_level = ''
    settings = None    # ini-хранилище переменных
    state_db = None    # База данных со списками истории открытия заметок и прочими данными
    state_db_connection = None
    snippets_relative_filename = os.path.join('Relanotes', 'Snippets-saved.txt')
    snippets_separator = '###'
    snippets_filename = ''
    snippet_actions = []


    def initial_setup(self):
        print('Инициализация настроек приложения')
        QtCore.QCoreApplication.setOrganizationName(self.NameOrganization)
        QtCore.QCoreApplication.setApplicationName(self.NameGlobal)

        # Получаем путь к каталогу с настройками программы по данным QStandardPaths
        self.config_path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation);
        self.config_path = give_correct_path_under_win_and_other(self.config_path)
        print("Каталог с настройками и логом программы: %s" % self.config_path)

        # Если не существует - создаем.
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)

        # Инициируем хранение настроек в ini-файле
        full_ini_filename = os.path.join(self.config_path, 'settings.ini')
        # print("Полный путь к ini-файлу настроек: %s" % full_ini_filename)

        self.log_level = logging.DEBUG  # or whatever
        self.logfile = os.path.join(self.config_path, 'working.log')

        self.settings = QtCore.QSettings(full_ini_filename, QtCore.QSettings.IniFormat)

        self.path_to_notes = self.settings.value('path_to_notes')
        # print('DEBUG: path_to_notes from settings: %s' % self.path_to_notes)
        # Проверяем БАГ, когда в переменную библиотека QT занесла неправильные слеши
        self.path_to_notes = give_correct_path_under_win_and_other(self.path_to_notes)

        print('self.path_to_notes: "%s", self.snippets_relative_filename: "%s"' % (
        self.path_to_notes, self.snippets_relative_filename))
        if self.path_to_notes:
            self.snippets_filename = os.path.join(self.path_to_notes, self.snippets_relative_filename)

        self.snippets_filename = give_correct_path_under_win_and_other(self.snippets_filename)

        # Получаем путь к каталогу, в котором лежат исходники программы
        self.path_to_app = get_path_to_app()
        print("path_to_app:", self.path_to_app)
        # '/home/vchsnr/Dropbox/Projects/Relanotes/Relanotes-next/'
        # Переходим в свой каталог, чтобы относительные пути до настроек и прочих файлов оказались
        # корректными при запуске из любого каталога.
        os.chdir(self.path_to_app)

        # path_to_home = os.path.expanduser("~")
        # print("path_to_home:", path_to_home)

        # Инициируем доступ к базе данных, в которой хранится состояние программы:
        # история открытия заметок, позиции в них и другая информация
        full_state_db_filename = os.path.join(self.config_path, 'state.db')
        self.state_db = sqlite3.connect(full_state_db_filename)
        self.state_db_connection = self.state_db.cursor()

        # return super().__init__(**kwargs)

    # was: , **kwargs
    def __init__(self):
        pass