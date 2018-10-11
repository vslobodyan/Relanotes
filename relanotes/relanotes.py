# -*- coding: utf-8 -*-

# __author__ = 'vyacheslav'
# __version__ = '0.06'


import logging

# from src.ui import calculator_window, preferences_window, note_multiaction
from relanotes.clear_history_dialog import ClearHistoryDialog
from relanotes.event_filter import MyEventFilter
from relanotes.main_window import Window
from relanotes.mytextbrowser import MyTextBrowser
from relanotes.note import Note
from relanotes.note_multiaction_window import NoteMultiactionWindow
from relanotes.notelist import Notelist
from relanotes.preferences_window import PreferencesWindow
from relanotes.profiler import Profiler
from relacalc import relacalc

# from PyQt4.QtCore import *
# from PyQt4.QtGui import *

from PyQt5 import QtWidgets

from relanotes.routines import *

# from PyQt5.QtCore import *
# from PyQt5.QtGui import *



#settingsNameOrganization = 'DigiTect'
#settingsNameGlobal = 'Relanotes'
#QtCore.QCoreApplication.setOrganizationName(settingsNameOrganization)
#QtCore.QCoreApplication.setApplicationName(settingsNameGlobal)

## Получаем путь к каталогу с настройками программы по данным QStandardPaths
#app_config_path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation);
## Подробнее о выборе пути: http://doc.qt.io/qt-5/qstandardpaths.html
## config_homePath = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppConfigLocation);
## config_homePath = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppLocalDataLocation);

#app_config_path = give_correct_path_under_win_and_other(app_config_path)

#print("Каталог с настройками программы: %s" % app_config_path)
## Если не существует - создаем.
#if not os.path.exists(app_config_path):
#    os.makedirs(app_config_path)

#full_ini_filename = os.path.join(app_config_path, 'settings.ini')
## print("Полный путь к ini-файлу настроек: %s" % full_ini_filename)

#settings = QtCore.QSettings(full_ini_filename, QtCore.QSettings.IniFormat)
## settings.setFallbacksEnabled(False)    # File only, no fallback to registry or or.

## settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
##     settingsNameOrganization, settingsNameGlobal)
    

#path_to_notes = settings.value('path_to_notes')
#print('DEBUG: path_to_notes from settings: %s' % path_to_notes)
## Проверяем БАГ, когда в переменную библиотека QT занесла неправильные слеши
#path_to_notes = give_correct_path_under_win_and_other(path_to_notes)

##path_to_test_converting_notes = settings.value('path_to_test_converting_notes')
##path_to_test_converting_notes = give_correct_path_under_win_and_other(path_to_test_converting_notes)

## Основные переменные

## Получаем путь к каталогу, в котором лежат файлы и подкаталоги программы
#path_to_me = os.path.split(os.path.abspath(sys.argv[0]))[0]
#print("path_to_me:", path_to_me)
## '/home/vchsnr/Dropbox/Projects/Relanotes/Relanotes-next/'
## Переходим в свой каталог, чтобы относительные пути до настроек и прочих файлов оказались
## корректными при запуске из любого каталога.
#os.chdir(path_to_me)

#path_to_home = os.path.expanduser("~")
#print("path_to_home:", path_to_home)

#prog_name = 'Relanotes'

## path_to_notes = '/home/rat/Dropbox/Data/s_zim/Notes/'
## path_to_notes = path_to_me+'Notes/'
## print("path_to_notes:", path_to_notes)

## FIXME: . При зачеркивании (или другом выделении) текста дальнейшая печать идет в таком-же новом стиле. Надо сделать
## чтобы шла как обычный текст. Пример - зачеркивание старого пароля и запись после него нового.

## Список истории
## rec = [ 'note' / 'list', 'filename' / 'filter', datetime ]
## history_recs = [ rec1, rec2, .. ]

## history_recs = []
#history_position = 0

#full_state_db_name = os.path.join(app_config_path, 'state.db')
#app_settings.state_db = sqlite3.connect(full_state_db_filename)
#app_settings.state_db_connection = state_db.cursor()

## full_notelist_db_filename = os.path.join(app_config_path, 'notelist.db')
## notelist_db = sqlite3.connect(full_notelist_db_filename)
## notelist_db_connection = notelist_db.cursor()
from relanotes.settings import App_Settings
from relanotes.table_of_note_contents import Table_of_note_contents
from relanotes.tests import App_Tests
from relanotes.text_format import Text_Format

"""
Список заметок и статус работы с ними - реализовано в классе Notelist, переменная file_recs
rec = [ id, filename, cute_name, parent_id, subnotes_count, size, favorite, hidden, 
        last_change, last_open, count_opens, opened ]

file_recs = [ rec1, rec2, rec3, .. ]
file_recs = []
"""

profiler = Profiler()



# if __name__ == "__main__":
app = QtWidgets.QApplication(sys.argv)
# myapp = MyForm()

# Инициируем класс настроек приложения
app_settings = App_Settings()

# Включаем логирование
root_logger = logging.getLogger()
root_logger.setLevel(app_settings.log_level)
handler = logging.FileHandler(app_settings.logfile, 'w', 'utf-8') # or whatever
# formatter = logging.Formatter('%(name)s %(message)s') # or whatever
# handler.setFormatter(formatter) # Pass handler as a parameter, not assign
root_logger.addHandler(handler)


# theme = Theme()


myFilter = MyEventFilter()
text_format = Text_Format()
main_window = Window()

# Переопределяем класс редактора заметок
new_textBrowser = MyTextBrowser(main_window.textBrowser_Note)
main_window.textBrowser_Note.setVisible(False)  # Скрываем старый класс редактора заметки
main_window.textBrowser_Note = new_textBrowser 
main_window.horizontalLayout_Note.layout().addWidget(main_window.textBrowser_Note)
main_window.horizontalLayout_Note.layout().addWidget(main_window.frame_NoteMinimap)

note = Note()

notelist = Notelist()
#history = History()

table_of_note_contents = Table_of_note_contents()
calculator_win = relacalc.CalculatorWindow()

preferences_win = PreferencesWindow()
notemultiaction_win = NoteMultiactionWindow()
clear_history_win = ClearHistoryDialog()

app.installEventFilter(myFilter)

# Инициируем класс тестов приложения
app_tests = App_Tests()


# Запускаем инициализирующую проверку пути к заметкам
main_window.check_path_to_notes_or_select_new()        

# history.setVisible()
notelist.set_visible()  # По-умолчанию встречаем пользователя списком заметок

main_window.show()

main_window.statusbar.showMessage('Application initializing..')
# self.open_file_in_editor(path_to_notes + 'компьютерное.txt')
main_window.initial_db()
notelist.update()
main_window.renew_history_lists('')
# Делаем инициализацию текста в поле фильтра списка заметок
main_window.notelist_filter_changed('')


sys.exit(app.exec_())


