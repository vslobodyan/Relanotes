# -*- coding: utf-8 -*-

# __author__ = 'vyacheslav'
# __version__ = '0.06'


import sys
import os
import re
import time
import sqlite3
from datetime import datetime, timedelta, date  #, time
import codecs
import html
import logging

# from src.ui import calculator_window, preferences_window, note_multiaction
from src.ui import preferences_window, note_multiaction, clear_history_dialog
from src.ui.main_window import *
from src import calculator

# from PyQt4.QtCore import *
# from PyQt4.QtGui import *

from PyQt5 import QtCore, QtGui, QtWidgets

from src.routines import *

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


"""
Список заметок и статус работы с ними - реализовано в классе Notelist, переменная file_recs
rec = [ id, filename, cute_name, parent_id, subnotes_count, size, favorite, hidden, 
        last_change, last_open, count_opens, opened ]

file_recs = [ rec1, rec2, rec3, .. ]
file_recs = []
"""


class App_Settings():
    # Основные настройки программы

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

    def __init__(self, **kwargs):
        print('Инициализация настроек приложения')
        QtCore.QCoreApplication.setOrganizationName(self.NameOrganization)
        QtCore.QCoreApplication.setApplicationName(self.NameGlobal)
        
        # Получаем путь к каталогу с настройками программы по данным QStandardPaths
        self.config_path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation);
        self.config_path = give_correct_path_under_win_and_other(self.config_path)
        print("Каталог с настройками программы: %s" % self.config_path)
        # Если не существует - создаем.
        if not os.path.exists(self.config_path):
            os.makedirs(self.config_path)
        # Инициируем хранение настроек в ini-файле
        full_ini_filename = os.path.join(self.config_path, 'settings.ini')
        # print("Полный путь к ini-файлу настроек: %s" % full_ini_filename)
        print("Каталог настроек и лога: %s" % self.config_path)

        self.log_level = logging.DEBUG # or whatever
        self.logfile = os.path.join(self.config_path, 'working.log')

        self.settings = QtCore.QSettings(full_ini_filename, QtCore.QSettings.IniFormat)

        self.path_to_notes = self.settings.value('path_to_notes')
        # print('DEBUG: path_to_notes from settings: %s' % self.path_to_notes)
        # Проверяем БАГ, когда в переменную библиотека QT занесла неправильные слеши
        self.path_to_notes = give_correct_path_under_win_and_other(self.path_to_notes)

        self.snippets_filename = os.path.join(self.path_to_notes, self.snippets_relative_filename)

        self.snippets_filename = give_correct_path_under_win_and_other(self.snippets_filename)


        # Получаем путь к каталогу, в котором лежат исходники программы
        self.path_to_app = get_path_to_app()
        print("path_to_app:", self.path_to_app)
        # '/home/vchsnr/Dropbox/Projects/Relanotes/Relanotes-next/'
        # Переходим в свой каталог, чтобы относительные пути до настроек и прочих файлов оказались
        # корректными при запуске из любого каталога.
        os.chdir(self.path_to_app)
        
        #path_to_home = os.path.expanduser("~")
        #print("path_to_home:", path_to_home)

        
        # Инициируем доступ к базе данных, в которой хранится состояние программы:
        # история открытия заметок, позиции в них и другая информация
        full_state_db_filename = os.path.join(self.config_path, 'state.db')
        self.state_db = sqlite3.connect(full_state_db_filename)
        self.state_db_connection = self.state_db.cursor()



        return super().__init__(**kwargs)


class Log():

    pass



class Profiler():
    start_time = 0
    start_time_overall = 0
    
    def start(self, text):
        self.start_time = time.time()
        self.start_time_overall = time.time()
        print(text)
    
    def checkpoint(self, text):
        print("Время выполнения: %.03f s" % (time.time() - self.start_time), '\n')
        print(text)
        self.start_time = time.time()
    
    def stop(self, text=''):
        print("Время выполнения: %.03f s" % (time.time() - self.start_time), '\n')
        print("Общее время работы профилируемого кода : %.03f s" % (time.time() - self.start_time_overall))
        print(text, '\n')

profiler = Profiler()


class MyEventFilter(QtCore.QObject):
    def eventFilter(self, receiver, event):

        # if not main_window: exit()

        # После блокировки и сворачивания окна перехыватываем восстановление окна и
        # запускаем таймер сворачивания снова, если он неактивный.
        if main_window.locked and main_window.isVisible() and (event.type() in [QtCore.QEvent.WindowStateChange]) and \
                not main_window.timer_window_minimize.isActive():
            # FIXME: .. фильтр событий повторно запускает таймер на сворачивание окна при первом сворачивании
            # Вариант решения: делать таймаут полсекунды в обработке событий,
            # if self.must_minimized and isVisible - запускаем таймер

            # print ('new minimize timer on restore win')
            main_window.timer_window_minimize.start(main_window.window_minimize_timeout)
            return True
           
        # Получили событие клавиатуры (или мыши) когда окно заблокировано
        if (event.type() == QtCore.QEvent.KeyPress) and main_window.locked:
                # print('keyboard event, by main_window is locked')
                # Проверяем на ключ разблокировки Ctrl+Win
                if (event.modifiers() & QtCore.Qt.ControlModifier) and \
                        ((event.modifiers() & QtCore.Qt.MetaModifier) or (event.modifiers() & QtCore.Qt.Key_Meta)):
                    # event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
                    # Если есть - разблокируем интерфейс
                    # print('We have unlock key combination')
                    main_window.unlock_ui()
                else:
                    # Если его нет - блокируем событие и выходим
                    return True                

        # Блокируем все клавиатурно-мышиные события при заблокированном интерфейсе
        if main_window.locked and \
                (event.type() in [QtCore.QEvent.KeyPress, QtCore.QEvent.KeyRelease, QtCore.QEvent.MouseButtonRelease,
                                  QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseMove, QtCore.QEvent.MouseButtonDblClick]):
            return True
        
        if not main_window.locked and main_window.actionLock_UI.isChecked() and \
                (event.type() in [QtCore.QEvent.KeyPress, QtCore.QEvent.KeyRelease, QtCore.QEvent.MouseButtonRelease,
                                  QtCore.QEvent.MouseButtonPress, QtCore.QEvent.MouseMove]):
            # Запускаем таймер отсчета блокировки
            # print('event restart lock_ui_timer')
            main_window.timer_lock_ui.start(main_window.lock_ui_timeout)

        # FIXME: Esc при фокусе в поле заметки не скрывает панель поиска по тексту заметки
        
        # Обрабатываем клавиатурные события в разных виджетах
        if event.type() == QtCore.QEvent.KeyPress:
            # print('keypress to '+receiver.objectName())
            # Отслеживаем нажатия клавиатуры при редактировании заметки 
            if receiver.objectName() == 'MyTextBrowser':

                # Нажатие Enter на основном или цифровом блоке
                if event.key() in [QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter]:
                    cursor = main_window.textBrowser_Note.textCursor()
                    # Если нажат перенос в начале строки - делаем пустую строку очищенной от формата,
                    # чтобы не плодились пустые строки с жирным текстом и прочим декором
                    if cursor.columnNumber() == 0:
                        # print('При редактировании заметки нажат Enter в начале строки. Сбрасываем формат шрифта у
                        # будущей пустой строчки. Исходник выделения курсора:')
                        # tmp_string = cursor.selection().toHtml()
                        # print(tmp_string.rpartition('StartFragment-->')[2])
                        
                        # cursor.setCharFormat(text_format.editor_default_format)
                        cursor.insertHtml(text_format.editor_default_font_span + '<br>')
                        # text_format.clear_format()
                        # return super(MyEventFilter,self).eventFilter(receiver, event)
                        return True
                    
            # Клавиатурные события приходящие на окно общего списка заметок
            # передаем на поле фильтра имени заметок
            if receiver.objectName() == 'textBrowser_Listnotes':
                main_window.lineNotelist_Filter.keyPressEvent(event)

                # На клавишу вниз - увеличиваем индекс выбранного
                if event.key() == QtCore.Qt.Key_Down:
                    # QMessageBox.information(None,"Filtered Key Press Event!!", "Key Down")
                    # notelist.items_cursor_position += 1
                    # notelist.update()
                    notelist.move_cursor(delta=1)
                    return True
                    
                # На клавишу вверх - уменьшаем индекс выбранного
                if event.key() == QtCore.Qt.Key_Up:
                    # QMessageBox.information(None,"Filtered Key Press Event!!", "Key Down")
                    # notelist.items_cursor_position -= 1
                    # notelist.update()
                    notelist.move_cursor(delta=-1)
                    return True

                # На Esc- возвращаемся в предыдущее открытую панель (текст заметки или содержание)
                if event.key() == QtCore.Qt.Key_Escape:
                    if notelist.items_cursor_url != '':
                        Note.set_visible(self, True)
                    return True
                # FIXME: на Esc в поле ввода фильтра списка заметок должны возвращаться в предыдущую панель, а не просто
                #  показывать окно заметки
            
            # Обрабатываем функциональные клавиши на поле фильтра имени 
            # списка заметок 
            if receiver.objectName() == 'lineNotelist_Filter':
                
                # На клавишу вниз - увеличиваем индекс выбранного
                if event.key() == QtCore.Qt.Key_Down:
                    # QMessageBox.information(None,"Filtered Key Press Event!!", "Key Down")
                    # notelist.items_cursor_position += 1
                    # notelist.update
                    notelist.move_cursor(delta=1)
                    return True

                # На клавишу вверх - уменьшаем индекс выбранного
                if event.key() == QtCore.Qt.Key_Up:
                    # QMessageBox.information(None,"Filtered Key Press Event!!", "Key Down")
                    # notelist.items_cursor_position -= 1
                    # notelist.update()
                    notelist.move_cursor(delta=-1)
                    return True

                # На Esc- возвращаемся в предыдущее открытую панель (текст заметки или содержание)
                if event.key() == QtCore.Qt.Key_Escape:
                    if notelist.items_cursor_url != '':
                        Note.set_visible(self, True)
                    return True
                # FIXME: на Esc в поле ввода фильтра списка заметок должны возвращаться в предыдущую панель, а не просто
                #  показывать окно заметки

            # Обрабатываем Esc на поле поиска внутри заметки или окне редактора
            if receiver.objectName() == 'lineTextToFind' or receiver.objectName() == 'textBrowser_Note' and \
                    main_window.frameSearchInNote.isVisible():
                if event.key() == QtCore.Qt.Key_Escape:
                    main_window.frameSearchInNote.setVisible(False)
                    main_window.textBrowser_Note.setFocus()
                    return True

            # QMessageBox.information(None,"Filtered Key Press Event!!",
            #         "In "+receiver.objectName()+" You Pressed: "+ event.text())
            # return True
            return super(MyEventFilter, self).eventFilter(receiver, event)
        else:      
            # Call Base Class Method to Continue Normal Event Processing
            return super(MyEventFilter, self).eventFilter(receiver, event)


def hbytes(num):
    # Возвращает размер в удобночитаемом виде
    for x in ['bytes', 'KB', 'MB', 'GB']:
        if num < 1024.0:
            if x == 'bytes':
                return "%3.0f %s" % (num, x)
            else:
                return "%3.1f %s" % (num, x)
        num /= 1024.0
    return "%3.1f%s" % (num, 'TB')


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    # Главное окно приложения.
    doc_source = QtGui.QTextDocument()
    sidebar_source = QtGui.QTextDocument()
    notelist_source = QtGui.QTextDocument()
    current_open_note_link = ''    # Ссылка на текущую открытую заметку
    timer_lock_ui = QtCore.QTimer()
    lock_ui_timeout = 10000
    locked = False
    timer_window_minimize = QtCore.QTimer()
    window_minimize_timeout = 10000

    # Действия, относящиеся только к редактору заметки
    note_editor_actions = None
    # Какие действия выводить в панели справа от редактора заметки
    note_editor_toolbar_actions = None


    def check_path_to_notes_or_select_new(self, select_new=False):
        # Функция проверки пути к заметкам из настроек или путем выбора каталога в диалоге
        #new_message_title = "Выбор каталога с заметками"
        #new_message_text = "Выберите каталог, в котором хранятся файлы с заметками. Включенные расширения файлов: %s" % notelist.allowed_note_files_extensions

        #message_title = message_text = None
        #print("path_to_notes: %s" % app_settings.path_to_notes)

        if not app_settings.path_to_notes:
            # Первый запуск программы. Приветствуем пользователя и предлагаем ему выбрать каталог с заметками

            message_title = "RelaNotes приветствует Вас!"
            message_text = '''Вы запустили отличную программу работы с заметками и знаниями.
Теперь Вам надо выбрать каталог с файлами заметок.
Включенные расширения файлов: %s''' % notelist.allowed_note_files_extensions
            reply = QtWidgets.QMessageBox.question(self, 
                                                   message_title,
                                                   message_text,
                                         QtWidgets.QMessageBox.Ok)
            select_new = True

        elif not os.path.exists(app_settings.path_to_notes):
            # Каталога с заметками не существует. Сообщаем о том, что может быть надо выбрать другой.
            message_title = "Ваши заметки были перемещены?"
            message_text = '''RelaNotes не может открыть каталог %s с Вашими заметками.
Возможно, он не существует или недоступен программе.
Проверьте доступность этого каталога или укажите новый.
Открыть другой каталог с заметками?''' % app_settings.path_to_notes
            reply = QtWidgets.QMessageBox.question(self, 
                                                   message_title,
                                                   message_text,
                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Cancel:
                # print("Заметки по указанному пути отсутствуют. Пользователь не хочет продолжать работу.")
                exit()
            elif reply == QtWidgets.QMessageBox.Yes:
                select_new = True
                # print("Выбираем новый путь к заметкам")
                # app_settings.path_to_notes = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes") )
                # raw_path_to_notes = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes", '' , QtWidgets.QFileDialog.ShowDirsOnly)

        if select_new:
            # Надо выбрать новый каталог заметок
                app_settings.path_to_notes = give_correct_path_under_win_and_other(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes", '' , QtWidgets.QFileDialog.ShowDirsOnly))
                app_settings.settings.setValue('path_to_notes', app_settings.path_to_notes)
                app_settings.settings.sync()
                print("Выбран новый путь к заметкам:", app_settings.path_to_notes)

    def open_notes(self):
        # Открываем другой каталог с заметками
        self.check_path_to_notes_or_select_new(select_new=True)
        notelist.update()

    def reopen_note(self):
        # Перезагружаем заметку из её файла
        if self.current_open_note_link:
            self.open_file_in_editor(self.current_open_note_link, reload=True)


    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # settings.setValue('int_value', 42)
        try:
            # self.layoutSettings = QtCore.QSettings(os.path.join(path_to_me, "./layout.ini"), QtCore.QSettings.IniFormat)
            # self.restoreGeometry(self.layoutSettings.value("mainWindow/geometry"))
            # self.restoreState(self.layoutSettings.value("mainWindow/windowState"))

            self.restoreGeometry(app_settings.settings.value("mainWindow/geometry"))
            self.restoreState(app_settings.settings.value("mainWindow/windowState"))
        except:
            pass

        # На инициализацию заполняем действия, которые идут к текущей заметке
        self.note_editor_actions = [
            self.actionAdd_Link, self.actionAdd_Image,
            self.actionBold, self.actionItalic,
            self.actionStrikethrough, self.actionMark,
            self.actionBullet_List, self.actionNumber_List,
            self.actionHeading_1, self.actionHeading_2,
            self.actionHeading_3, self.actionHeading_4,
            self.actionHeading_5, self.actionHeading_6,
            self.actionUndo, self.actionRedo,
            self.actionFind_in_current_note,
            self.actionFind_next_in_cur_note,
            self.actionShow_content_collapse_all_H,
            self.actionCollapse_all_H_exclude_cur,
            self.actionCollapse_cur_H, self.actionExpand_all_H,
            self.actionSave_note, self.action_ClearFormat,
            self.actionCode,
            self.actionCopy, self.actionPaste, self.actionCut,
            self.actionPaste_as_text
        ]

        # Корневые пункты меню, которые скрываем и показываем вместе с
        # текущей заметкой
        self.note_editor_root_menus = [
            self.menuFormat,
            self.menuContent_cur_note
        ]


        self.note_editor_toolbar_actions = [
            self.actionUndo,
            self.actionRedo,
            self.actionBold,
            self.actionItalic,
            self.actionStrikethrough,
            self.actionMark,
            self.actionCode,
            self.actionBullet_List,
            self.actionNumber_List,
            self.actionHeading_1,
            self.actionHeading_2,
            self.actionHeading_3,
            self.actionHeading_4,
            self.actionHeading_5,
            self.actionHeading_6,
            self.action_ClearFormat,
            self.actionAdd_Link,
            self.actionAdd_Image,
            
            # self.actionSave_note, 
            # self.actionFind_in_current_note,
            # self.actionFind_next_in_cur_note,
            # self.actionClear, 
        ]


    
        # Новая работа с сигналами в PyQT5
        # Пример объяснения: http://stackoverflow.com/questions/17578428/pyqt5-signals-and-slots-qobject-has-no-attribute-error
    
        self.timer_lock_ui.setSingleShot(True)
        # Старая строка под PyQT4
        # QtCore.QObject.connect(self.timer_lock_ui, QtCore.SIGNAL("timeout ()"), self.lock_ui)
        # Новая реализация связи сигнала по таймауту таймера
        self.timer_lock_ui.timeout.connect(self.lock_ui)
        
        self.actionLock_UI.triggered.connect(self.lock_ui_timer_start)
    
        self.timer_window_minimize.setSingleShot(True)
        # QtCore.QObject.connect(self.timer_window_minimize, QtCore.SIGNAL("timeout ()"), self.minimize)
        self.timer_window_minimize.timeout.connect(self.minimize)
    
        # self.webView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        # self.textBrowser_History.setOpenExternalLinks(true)
        # self.connect(self.ui.webView, QtCore.SIGNAL("linkClicked (const QUrl&)"), self.loadfile2)
        # QtCore.QObject.connect(self.webView, QtCore.SIGNAL("linkClicked (const QUrl&)"), self.loadfile2)
        
        # QtCore.QObject.connect(self.textBrowser_History, QtCore.SIGNAL("anchorClicked (const QUrl&)"), self.loadfile_from_history)
        
        #self.textBrowser_History.anchorClicked.connect(self.loadfile_from_history)


        self.textBrowser_Note.anchorClicked.connect(self.open_url_from_current_note)

        # Debug
        # QtCore.QObject.connect(self.textBrowser_Note, QtCore.SIGNAL("textChanged()"), self.note_text_changed)
        self.textBrowser_Note.textChanged.connect(self.note_text_changed)
        
        # self.plainTextEdit_Note_Ntml_Source.setVisible(False)
        
        # web_view.connect(web_view, SIGNAL("urlChanged(const QUrl&)"), url_changed)
        # self.webView.linkClicked.connect(self.loadfile2)

        # self.connect(self.ui.listWidget, QtCore.SIGNAL('itemClicked()'), self.loadfile)
        # QtCore.QObject.connect(self.listWidget, QtCore.SIGNAL("itemClicked(QListWidgetItem *)"), self.loadfile)

        # QtCore.QObject.connect(self.tabWidget_2, QtCore.SIGNAL("currentChanged()"), self.refresh_html_source_or_view())
        # self.tabWidget_2.currentChanged.connect(self.refresh_html_source_or_view)

        # QtCore.QObject.connect(self.lineNotelist_Filter, QtCore.SIGNAL("textChanged( const QString& )"),
                               # self.notelist_filter_changed)

        # Отслеживаем изменение текста в поле
        self.lineNotelist_Filter.textChanged.connect(self.notelist_filter_changed)
        
        # Отслеживаем изменение положения курсора в поле
        self.lineNotelist_Filter.cursorPositionChanged.connect(self.notelist_filter_cursorPositionChanged)

        # Отслеживаем изменение выделения в поле
        self.lineNotelist_Filter.selectionChanged.connect(self.notelist_filter_selectionChanged)

        # QtCore.QObject.connect(self.lineTextToFind, QtCore.SIGNAL("textChanged( const QString& )"),
                               # self.find_text_in_cur_note)
        self.lineTextToFind.textChanged.connect(self.find_text_in_cur_note)

        # self.textEdit.setPlainText('123')

        # self.dockHistory.restoreGeometry()

        
        # Скрываем окна истории и таблицы содержания заметки        
        self.dockHistory.close()
        self.dockNoteContentTable.close()
        
        # Скрываем поле поиска по тексту внутри заметок и текст рядом с ним
        self.label_6.hide()
        self.lineEdit_Filter_Note_Text.hide()
        # Скрываем текст о текущем фильтре заметок
        self.label_DisplayFilters.hide()

        # Скрываем панель прогресса поиска заметок
        self.Search_Progressbar_Panel.hide()

        # if self.dockHistory.isVisible():
            # self.actionShowHistoryWindow.setChecked(True)
        # else:
            # self.actionShowHistoryWindow.setChecked(False)
        
        # if self.dockNoteContentTable.isVisible():
            # self.actionShow_List_of_contents.setChecked(True)
        # else:
            # self.actionShow_List_of_contents.setChecked(False)

        # Связываем действия открытия и закрытия мини-окна истории и мини-окна таблицы содержимого заметки
        self.actionShowHistoryWindow.triggered.connect(self.ShowHistoryWindow)
        self.actionShow_List_of_contents.triggered.connect(self.Show_List_of_contents_Window)

        
        # Добавляем тулбар на панель справа от редактора заметки
        hBoxLayout = QtWidgets.QHBoxLayout()
        # note_editor_toolbar = QtWidgets.QToolBar(self.frame_NoteMinimap)
        note_editor_toolbar = QtWidgets.QToolBar(self.widget_toolbar)
        
        note_editor_toolbar.setOrientation(QtCore.Qt.Vertical)

        for action in self.note_editor_toolbar_actions:
            if not action:
                note_editor_toolbar.addSeparator()
            else:
                note_editor_toolbar.addAction(action)

        # self.frame_NoteMinimap.setMinimumWidth(0)
        hBoxLayout.setContentsMargins(0, 0, 0, 0)
        hBoxLayout.setSpacing(0)
        hBoxLayout.addWidget(note_editor_toolbar)
        # self.frame_NoteMinimap.setLayout(hBoxLayout)
        self.widget_toolbar.setLayout(hBoxLayout)
        
        self.actionCalculator.triggered.connect(self.show_calculator)
        self.actionPreferences.triggered.connect(self.show_preferences)
        
        self.actionHistoryClear.triggered.connect(self.history_clear)

        self.actionOpenNotes.triggered.connect(self.previous_note)

        self.actionPrevious_note.triggered.connect(self.previous_note)
        self.actionNext_note.triggered.connect(self.next_note)
        self.actionNext_note.setDisabled(True)
        self.actionForward_on_history.triggered.connect(self.forward_on_history)
        self.actionForward_on_history.setDisabled(True)
        self.actionBackward_on_history.triggered.connect(self.backward_on_history)
        self.actionFind_in_current_note.triggered.connect(self.find_in_current_note)
        self.actionFind_next_in_cur_note.triggered.connect(self.find_next_in_cur_note)
        # QtCore.QObject.connect(self.lineTextToFind, QtCore.SIGNAL("returnPressed()"), self.find_next_in_cur_note)
        self.lineTextToFind.returnPressed.connect(self.find_next_in_cur_note)

        
        self.actionShow_note_HTML_source.triggered.connect(self.show_html_source)
        self.plainTextEdit_Note_Ntml_Source.setVisible(False)

        self.actionOpenNotes.triggered.connect(self.open_notes)

        self.actionReopen_note.triggered.connect(self.reopen_note)

        self.show_snippets()



        ## Устанавливаем стили текстовых редакторов
        #texteditor_style = '''
        #                        font-family: Sans;
        #                        font-size: 17px;
        #                        color: #1a1a1a;
        #                        white-space: pre-wrap;
        #                        '''
        #self.textBrowser_Listnotes.setStyleSheet(texteditor_style)
        #self.textBrowser_Note.setStyleSheet(texteditor_style)

        # QtGui.QFileDialog.windowFilePath(self)

        #print("path_to_notes: %s" % app_settings.path_to_notes)
        #if not app_settings.path_to_notes or not os.path.exists(app_settings.path_to_notes):
        #    # print("")
        #    reply = QtWidgets.QMessageBox.question(self, "Ваши заметки были перемещены?",
        #                                 "Каталог " + str(app_settings.path_to_notes) + " с Вашими заметками не существует.\n"
        #                                                              "Открыть другой каталог с заметками?",
        #                                 QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No | QtWidgets.QMessageBox.Cancel)
        #    if reply == QtWidgets.QMessageBox.Cancel:
        #        # print("Заметки по указанному пути отсутствуют. Пользователь не хочет продолжать работу.")
        #        exit()
        #    elif reply == QtWidgets.QMessageBox.Yes:
        #        # print("Выбираем новый путь к заметкам")
        #        # app_settings.path_to_notes = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes") )
        #        # raw_path_to_notes = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes", '' , QtWidgets.QFileDialog.ShowDirsOnly)
        #        app_settings.path_to_notes = give_correct_path_under_win_and_other(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes", '' , QtWidgets.QFileDialog.ShowDirsOnly))
        #        app_settings.settings.setValue('path_to_notes', app_settings.path_to_notes)
        #        app_settings.settings.sync()
        #        print("Выбран новый путь к заметкам:", app_settings.path_to_notes)


    def minimize(self):
        # print('main_window.showMinimized()')
        main_window.showMinimized()

    def unlock_ui(self):
            # Выключаем таймеры и отключаем блокировку UI
            self.timer_lock_ui.stop()
            self.timer_window_minimize.stop()
            if self.locked:
                self.locked = False
                
                # Включаем обратно основные панели окна
                self.toolBar.setEnabled(True)
                self.menubar.setEnabled(True)
                self.stackedWidget.setEnabled(True)
                # self.frameNotelist_Filter.setEnabled(True)
                # self.frameSearchInNote.setEnabled(True)
                # self.frame_Note.setEnabled(True)
                self.dockHistory.setEnabled(True)
                # self.textBrowser_Listnotes.setEnabled(True)
                # self.textBrowser_NoteContents.setEnabled(True)
            
                # print('UI unlocked')
                self.statusbar.setStyleSheet('')
                self.statusbar.showMessage("UI unlocked", msecs=5000)

    def lock_ui(self):
        if not self.locked:
            # print('lock_ui here')
            self.locked = True
            self.statusbar.setStyleSheet("QStatusBar{font-size:18px; background:#fff8a5;"
                                         " color:#008066;font-weight:bold;}")
            self.statusbar.showMessage('Interface of programm is LOCKED! You can unlock by press Ctrl+Win')

            # Отключаем основные панели окна для демонстрации выключенности
            self.toolBar.setDisabled(True)
            self.menubar.setDisabled(True)
            self.stackedWidget.setDisabled(True)
            # self.frameNotelist_Filter.setDisabled(True)
            # self.frameSearchInNote.setDisabled(True)
            # self.frame_Note.setDisabled(True)
            self.dockHistory.setDisabled(True)
            # self.textBrowser_Listnotes.setDisabled(True)
            # self.textBrowser_NoteContents.setDisabled(True)
            
            # Запускаем таймер на сворачивание окна
            self.timer_window_minimize.start(self.window_minimize_timeout)

    def lock_ui_timer_start(self):
        if self.actionLock_UI.isChecked():
            # Инициируем первый старт таймера если включена блокировка интерфейса
            # print('lock_ui_timer_start')
            self.timer_lock_ui.start(self.lock_ui_timeout)
        else:
            self.unlock_ui()

    #def filter_note_text_changed(self, filter_text=''):
    #    notelist.items_cursor_position = 0
    #    notelist.need_rescan = True
    #    notelist.timer_update.start(notelist.update_timeout)


    def notelist_filter_cursorPositionChanged(self, old, new):
        # Реакция на изменение позиции курсора в поле редактирования фильтра списка заметок
        if notelist.filter_in_change:
            # Если производятся внутренние манипуляции с полем фильтра- ждем их окончания
            return 0

        if notelist.filter_is_empty:
            # Надо пресечь изменение положения курсора
            self.lineNotelist_Filter.setCursorPosition(0)
            filter_string = ''
        else:
            filter_string = self.lineNotelist_Filter.text()
        
        # Выводим подсказку по текущему положению курсора
        
        # Получаем строку до курсора
        left_part = filter_string[:new]
        # Строка после курсора
        right_part = filter_string[new:]
        #print('filter_string #%s#%s#' % (left_part, right_part) )
        # Подсказка о вводе имени и возможности нажать пробел
        if ' ' not in left_part:
            # Курсор стоит на имени
            if right_part:
                # Есть правая часть от имени
                tip_text_html = notelist.filter_editing_tips['name']
            else:
                # Правой части фильтра от курсора на имени нет
                tip_text_html = notelist.filter_editing_tips['empty']
        else:
            # Курсор стоит на тексте
            tip_text_html = notelist.filter_editing_tips['text']

        tip_html = '%s%s%s' % (notelist.filter_editing_tips['html_begin'],
                                tip_text_html,
                                notelist.filter_editing_tips['html_end'])
        self.labelNotelistFilterTip.setText(tip_html)


    def notelist_filter_selectionChanged(self):
        if notelist.filter_is_empty:
            # Надо пресечь изменение выделения
            self.lineNotelist_Filter.setSelection(0,0)

    def notelist_filter_changed(self, filter_text):
        # Функция обработки изменения текста фильтра заметок
        
        needed_list_update = True # Признак необходимости обновить список

        # Останавливаем отложенное обновление. Если надо - запустим заново в коде ниже.
        notelist.cancel_scheduled_update()
        main_window.lineNotelist_Filter.setFocus()
        # Проверяем - не внутреннее ли это программное изменение текста фильтра на подсказку или наоборот.
        if notelist.filter_in_change:
            #print('notelist.filter_in_change')
            return 0

        # Проверяем ситуацию, когда ввели пробел перед текстом, и фильтры при этом не изменились
        new_filter_name, new_filter_text = notelist.extract_filters(filter_text)
        if new_filter_name == notelist.filter_name and new_filter_text ==         notelist.filter_text:
            # Фильтры не изменились. Обновлять список не надо.
            #print('Фильтры не изменились.')
            needed_list_update = False

        #print('filter_text = ##%s##' % filter_text)
        #notelist_filter = filter_text
        #notelist_filter = main_window.lineNotelist_Filter.text()
        # Проверяем на пустоту поля фильтра
        if not filter_text:
            # У нас совсем пустой фильтр. Надо указать что он пуст и показать подсказку
            #print('not filter_text')
            notelist.filter_in_change = True
            main_window.lineNotelist_Filter.setText(notelist.filter_tip_for_using)
            main_window.lineNotelist_Filter.setStyleSheet('''
                                color: #aaa;
                                font-size: 14px;
                                background: white;
                                '''
                                )
            #main_window.lineNotelist_Filter.selectAll()
            #main_window.lineNotelist_Filter.cursor
            notelist.filter_in_change = False
            # Переносим вне блока "служебного изменения поля фильтров", чтобы сработала реакция на изменение положения курсора и прописала нужную подсказку в стороне от поля
            self.lineNotelist_Filter.setCursorPosition(0)
            
            if notelist.filter_is_empty:
                # Признак того, что фильтр пуст уже стоял - это инициирущий запуск функции для обновления внешнего вида
                return 0
            else:
                # Фильтр был очищен, надо обновить список заметок
                notelist.filter_is_empty = True
                # Вызываем фейковую установке курсора, чтобы стработала инициация начального значения подсказки для поля.
                #self.lineNotelist_Filter.setCursorPosition(0)
                self.notelist_filter_cursorPositionChanged(1,0)
                if needed_list_update:
                    notelist.schedule_update()
                return 0
        else:
            # Текст фильтра не пуст. Если он не подсказка - то надо указать во внутреннем признаке что фильтр не пуст и запустить отложенное обновление вида списка.
            #print('filter_text is True')
            if not ( notelist.filter_is_empty and filter_text == notelist.filter_tip_for_using):
                #print('not ( notelist.filter_is_empty and filter_text == notelist.filter_tip_for_using)')
                # Проверяем - не начал ли менять текст пользователь в начале текста подсказки
                if notelist.filter_is_empty and filter_text.endswith(notelist.filter_tip_for_using):
                    # Надо удалить подсказку из фильтра, начинаемого набирать или вставленного пользователем
                    #notelist.filter_in_change = True
                    #print('full text: #%s#' % filter_text)
                    cleared_user_filter = filter_text.rpartition(notelist.filter_tip_for_using)[0]
                    #print('text after rpartition: #%s#' % cleared_user_filter)
                    main_window.lineNotelist_Filter.setText(cleared_user_filter)
                    #notelist.filter_in_change = False
                else:
                    # Текст уже без примеси подсказки
                    main_window.lineNotelist_Filter.setStyleSheet('''
                                        color: #1a1a1a;
                                        font-size: 16px;
                                        background: #fff8a5;
                                        '''
                                        )
                    notelist.filter_is_empty = False
                    if needed_list_update:
                        notelist.schedule_update()
                    return 0

        if notelist.filter_is_empty:
            # Возможно, текст был изменен в пустом фильтре с подсказкой
            if filter_text == notelist.filter_tip_for_using:
                # Текст подсказки по-умолчанию остался без изменений. Выходим
                #print('notelist.filter_is_empty and filter_text == notelist.filter_tip_for_using')
                return 0
            else:
                # Текст в фильтре не соответствует подсказке. Меняем фильтр и стиль оформления поля ввода
                #print("notelist.filter_is_empty and text isn't filter_tip_for_using")
                notelist.filter_is_empty = False
                notelist.filter_in_change = True
                main_window.lineNotelist_Filter.setText(filter_text)
                main_window.lineNotelist_Filter.setStyleSheet('''
                                    color: #1a1a1a;
                                    font-size: 16px;
                                    background: #fff8a5;
                                    '''
                                    )
                notelist.filter_in_change = False
                if needed_list_update:
                    notelist.schedule_update()
                return 0


        #print('notelist.timer_update.start')
        #notelist.items_cursor_position = 0
        #notelist.need_rescan = True
        #notelist.timer_update.start(notelist.update_timeout)


    def show_html_source(self):
        if self.plainTextEdit_Note_Ntml_Source.isVisible():
            self.plainTextEdit_Note_Ntml_Source.setVisible(False)
        else:
            self.plainTextEdit_Note_Ntml_Source.setVisible(True)



    def save_note_cursor_position(self):
        #print('Проверка необходимости сохранить позицию открытой заметки')
        # Проверяем - есть ли открытая заметка в окне редактора

        filename = main_window.current_open_note_link
        if filename:
            current_position = main_window.textBrowser_Note.textCursor().position()
            #print('Файл открытой заметки %s и позиция курсора %s' % (filename, current_position))
            # Если есть - сохраняем для неё последнюю позицию курсора

            # Обновляем запись в базе
            app_settings.state_db_connection.execute("UPDATE file_recs SET current_position=?  WHERE filename=?",
                                        (current_position, filename))
            app_settings.state_db.commit()                        
        else:
            print('Открытой заметки нет.')
            pass


    def closeEvent(self, e):
        # self.layoutSettings.setValue("mainWindow/geometry", self.saveGeometry())
        # self.layoutSettings.setValue("mainWindow/windowState", self.saveState())
        # self.layoutSettings.sync()

        # Сохраняем позицию заметки, если она была открыта
        self.save_note_cursor_position()

        app_settings.settings.setValue("mainWindow/geometry", self.saveGeometry())
        app_settings.settings.setValue("mainWindow/windowState", self.saveState())
        app_settings.settings.sync()

        # self.settings.setValue('size', self.size())
        # self.settings.setValue('pos', self.pos())
        e.accept()        
        
    def find_in_current_note(self):
        # if self.frameSearchInNote.isVisible():
        #    self.frameSearchInNote.setVisible(False)
        # else:
        self.lineTextToFind.selectAll()
        self.lineTextToFind.setFocus()
        self.frameSearchInNote.setVisible(True)

    def find_text_in_cur_note(self, text_to_find):
        self.textBrowser_Note.moveCursor(QtGui.QTextCursor.Start)
        self.textBrowser_Note.find(text_to_find)

    def find_next_in_cur_note(self):
        self.textBrowser_Note.find(self.lineTextToFind.text())

    def open_url_from_current_note(self, url):
        print('opening url %s from note editor..' % url)
        # if sys.platform=='win32':
            # os.startfile(url)
        # elif sys.platform=='darwin':
            # subprocess.Popen(['open', url])
        # else:
            # try:
                # subprocess.Popen(['xdg-open', url])
            # except OSError:
                # print('Please open a browser on: '+url)
    

    def history_clear(self):
        # Подготовка и отображение диалога очистки истории последних открытых заметок
        clear_history_win.history_items = []
        
        #layout = QtWidgets.QVBoxLayout(clear_history_win.scrollArea)
        #layout.setAlignment(QtCore.Qt.AlignTop)

        layout = QtWidgets.QVBoxLayout(clear_history_win.scrollAreaWidgetContents)
        layout.setAlignment(QtCore.Qt.AlignTop)


        # Собираем все элементы истории
        file_recs_rows = app_settings.state_db_connection.execute("SELECT * FROM file_recs WHERE last_open NOT NULL ORDER BY last_open DESC")

        for row in file_recs_rows:
            rec_filename, rec_cute_name, rec_parent_id, rec_subnotes_count, rec_last_change, rec_last_open, rec_count_opens, rec_current_position = row

            # # Проверка файла из истории на существование 
            # if not os.path.isfile(rec_filename):
            #    # Файл не существует или это каталог, а не файл.
            #    # Удаляем из истории
            #    app_settings.state_db_connection.execute("DELETE FROM file_recs WHERE filename=?", (rec_filename,) )
            #    continue  # Переходим на следующий виток цикла

            history_item = clear_history_win.history_rec.copy()
            chb_label = rec_last_open.rpartition(':')[0] + ' - ' + str(rec_filename)
            new_checkbox = QtWidgets.QCheckBox(chb_label)

            layout.addWidget(new_checkbox)

            history_item['checkbox'] = new_checkbox
            history_item['filename'] = rec_filename
            history_item['last_open'] = rec_last_open

            clear_history_win.history_items.append(history_item)

        #print("layout.sizeHint() : %s" % layout.sizeHint())
        #layout.setGeometry(QtCore.QRect(QtCore.QPoint(0,0), layout.sizeHint()))
        #print("layout2.sizeHint() : %s" % layout2.sizeHint())
        layout.setGeometry(QtCore.QRect(QtCore.QPoint(0,0), layout.sizeHint()))


        # Запускаем диалог и получаем ответ пользователя
        if clear_history_win.exec():
            print('Надо удалить из истории:')
            for one_item in clear_history_win.history_items:
                if one_item['checkbox'].isChecked():
                    print(' - %s' % one_item['filename'])
                    app_settings.state_db_connection.execute("UPDATE file_recs SET last_open=NULL, count_opens=0 WHERE filename=?", (one_item['filename'],))
            notelist.update(history_update=True)
            self.renew_history_lists()

        # Удаляем все виджеты и компоновщик
        while layout.count():
            item = layout.takeAt(0)
            item.widget().deleteLater()
        layout.deleteLater()





    def previous_note(self):
        self.statusbar.showMessage('Open previous note in history')
        
    def next_note(self):
        self.statusbar.showMessage('Open next note in history')
        
    def forward_on_history(self):
        self.statusbar.showMessage('Forward on history')
        
    def backward_on_history(self):
        self.statusbar.showMessage('Backward on history')

    def initial_db(self):
        self.statusbar.showMessage('First read and indexing of your files..')

        # Список истории
        # rec = [ 'note' / 'list', 'filename' / 'filter' ]
        # history_recs = [ rec1, rec2, .. ]

        #try:
        #    app_settings.state_db_connection.execute('''CREATE TABLE history_recs
        #         (type text, value text, datetime integer)''')
        #except:
        #    pass
            
        # Список файлов
        # rec = [ filename, cute_name, parent_id, subnotes_count, last_change, last_open, count_opens, current_position ]
        # file_recs = [ rec1, rec2, rec3, .. ]

        try:
            app_settings.state_db_connection.execute('''CREATE TABLE file_recs
             (filename text PRIMARY KEY, cute_name text, parent_id integer, subnotes_count integer,
             last_change integer, last_open integer, count_opens integer, current_position integer)''')
        except:
            pass

        # Дерево подразделов в файлах заметок

        # Списки меток в файлах заметок
        
        # Списки задач в файлах заметок

        # Insert a row of data
        # app_settings.state_db_connection.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

        # Save (commit) the changes
        app_settings.state_db.commit()
        
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        # app_settings.state_db.close()


    def ShowHistoryWindow(self):
        if self.actionShowHistoryWindow.isChecked():
            self.dockHistory.show()
        else:
            self.dockHistory.close()

    def Show_List_of_contents_Window(self):
        if self.actionShow_List_of_contents.isChecked():
            self.dockNoteContentTable.show()
        else:            
            self.dockNoteContentTable.close()

    def show_calculator(self):
        calculator_win.show()
        # calculator_form.show()

    def show_preferences(self):
        preferences_win.show()

    def renew_history_lists(self, active_link=None):
        # Обновления листов истории - сайдбар, и может быть меню в будущем
        #print('Обновляем UI списков истории')
        html_string = notelist.make_html_source_for_items_list_in_history_sidebar()
        self.sidebar_source.setHtml(html_string)
        self.textBrowser_History.setDocument(self.sidebar_source)

    def note_text_changed(self):
        # self.plainTextEdit_Note_Ntml_Source.setPlainText(self.textBrowser_Note.toHtml())
        # self.plainTextEdit_Note_Ntml_Source.setPlainText(self.doc_source.toHtml())
        # print('Текст заметки изменен')
        pass
   

    def adjust_scrollbar_position_at_editor(self, textbrowser, cursor_line, lines_count):
        # Выставляем положение скроллинга для лучшего отображения курсора в тексте или в списке элементов

        scrollbar_maximum = textbrowser.verticalScrollBar().maximum()
        percent_of_position = cursor_line / lines_count
        scrollbar_set_pos = scrollbar_maximum * percent_of_position
        textbrowser_height = textbrowser.height()
        
        #print('Сдвиг промотки: scrollbar_maximum=%s, percent_of_position=%s, scrollbar_set_pos=%s, textbrowser_height=%s' % (scrollbar_maximum, percent_of_position,scrollbar_set_pos, textbrowser_height) )

        if scrollbar_set_pos < textbrowser_height * 0.8:
            scrollbar_set_pos = 0
        if scrollbar_set_pos > scrollbar_maximum - textbrowser_height / 2:
            scrollbar_set_pos = scrollbar_maximum
        
        # Устанавливаем выбранное значение промотки
        textbrowser.verticalScrollBar().setValue(scrollbar_set_pos)


    def extract_real_styles_note_format(self):
        # Функция извлечения реальных стилей из редактора с помощью тестовой заметки

        ### Получаем реальные стили из редактора с тестовой заметкой ###
        # Это позволяет изменяя стили в CSS получать их измененное форматирование в редакторе, чтобы потом с ними в нем оперировать, и иметь возможность конвертировать текст из редактора в wiki, markdown и т.д.
        self.textBrowser_TestNote = QtWidgets.QTextBrowser()
        # Чтобы не оказалось переноса
        self.textBrowser_TestNote.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)
        self.test_doc_source = QtGui.QTextDocument()
        testnote = ' \n' \
                 'default text\n' \
                 '====== Header level 1 ======\n' \
                 '===== Header level 2 =====\n' \
                 '==== Header level 3 ====\n' \
                 '=== Header level 4 ===\n' \
                 '== Header level 5 ==\n' \
                 '= Header level 6 =\n' \
                 '\'\'code text\'\' \n' \
                 '~~striked text~~ \n' \
                 '__marked text__ \n' \
                 'http://link_text' 

        test_note_source = note.convert_zim_text_to_html_source(testnote)
        self.test_doc_source.setHtml(test_note_source)
        self.textBrowser_TestNote.setDocument(self.test_doc_source)

        # Новая функция получения стилей через перемещение курсора
        test_cursor = self.textBrowser_TestNote.textCursor()
        test_cursor.movePosition(QtGui.QTextCursor.Start)
        
        def move_down_and_get_span(cursor, only_style=False):
            cursor.movePosition(QtGui.QTextCursor.Down)
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            return note.get_span_under_cursor(test_cursor, only_style)

        text_format.editor_default_font_span = note.get_span_under_cursor(test_cursor)
        text_format.editor_h1_span = move_down_and_get_span(test_cursor)
        text_format.editor_h2_span = move_down_and_get_span(test_cursor)
        text_format.editor_h3_span = move_down_and_get_span(test_cursor)
        text_format.editor_h4_span = move_down_and_get_span(test_cursor)
        text_format.editor_h5_span = move_down_and_get_span(test_cursor)
        text_format.editor_h6_span = move_down_and_get_span(test_cursor)


        text_format.editor_h_span = ['0-empty', text_format.editor_h1_span,
                                    text_format.editor_h2_span,
                                    text_format.editor_h3_span,
                                    text_format.editor_h4_span,
                                    text_format.editor_h5_span,
                                    text_format.editor_h6_span]

        text_format.editor_code_span = move_down_and_get_span(test_cursor)
        text_format.editor_strikethrough_span = move_down_and_get_span(test_cursor)
        text_format.editor_mark_span = move_down_and_get_span(test_cursor)
        text_format.editor_link_external_style = move_down_and_get_span(test_cursor, only_style=True)





    def open_file_in_editor(self, filename, line_number=None, found_text=None, reload=False, dont_save_in_history=False):
        # line_number - новая переменная промотки редактора на нужную строку
        # found_text - искомый текст, который надо подсветить
        self.statusbar.showMessage('Загружается файл %s' % filename)

        #print('open_file_in_editor("filename=%s", "line_number=%s")' % (filename, line_number) )
        #print('DEBUG: open_file_in_editor("filename=%s")' % filename)
        filename = get_correct_filename_from_url(filename)

        #print('Загружается файл %s с номером строки %s и поиском текста %s. Перезагрузка: %s' % (filename, line_number, found_text, reload) )
        
        # Сохраняем позицию предыдущей заметки, если она была открыта
        self.save_note_cursor_position()

        # print('link_note_pos: '+str(link_note_pos))
        # TODO: .. Профилировать скорость загрузки файла и отображения его текста
        
        rec_current_position = None
        
        if reload:
            # У нас указана внутренняя перезагрузка заметки на то-же место
            if notelist.file_in_state_db(filename):
                # Запись о файле уже есть. Получаем из неё последнюю позицию
                app_settings.state_db_connection.execute("SELECT count_opens, current_position FROM file_recs WHERE filename=?", (filename,))
                rec_count_opens, rec_current_position = app_settings.state_db_connection.fetchone()
                #print('Количество открытий заметки: %s, последняя позиция курсора: %s' % (rec_count_opens, rec_current_position))

        # Проверяем на переход из списка файлов
        elif notelist.is_visible():
            # rec = [ 'note' / 'list', 'filename' / 'filter', datetime ]
            if notelist.history_position == 0:
                new_recs_sel = []
                
                if self.lineNotelist_Filter.text() != '':
                    new_recs_sel = [('list', self.lineNotelist_Filter.text(),), ]
                # Пишем открытие заметки
                new_recs_sel += [('note', filename,), ]
                
                ########## history_recs
                ## Перед добавлением новой записи проверяем - нет-ли записи с такими-же значениями уже в списке
                #for rec in new_recs_sel:
                #    # print ( 'rec: '+str(rec) + ' len:' + str(len(rec)) )
                #    app_settings.state_db_connection.execute("SELECT * FROM history_recs WHERE type=? AND value=?", rec)
                #    existed_rec = app_settings.state_db_connection.fetchall()
                #    if len(existed_rec) > 0:
                #        # print (existed_rec)
                #        # Запись уже есть. Прописываем ей новое время открытия.
                #        app_settings.state_db_connection.execute("UPDATE history_recs SET datetime=? WHERE type=? AND value=?",
                #                                    (datetime.now(), rec[0], rec[1]))
                #        app_settings.state_db.commit()                        
                #    else:
                #        # Записи нет. Создаем новую.
                #        # print ( 'rec_tmp: '+str(rec_tmp)+' len:'+str(len(rec_tmp)) )
                #        app_settings.state_db_connection.execute("INSERT INTO history_recs VALUES (?,?,?)",
                #                                    (rec[0], rec[1], datetime.now()))
                #        app_settings.state_db.commit()


                #print('FILE_RECS for %s starting here' % filename)
                ######### file_recs
                # Перед добавлением новой записи проверяем - нет-ли записи с такими-же значениями уже в списке
                if notelist.file_in_state_db(filename):
                    #notelist.file_in_history(filename):
                    #print('FILE_RECS: для файла %s запись в базе есть. Обновляем.' % filename)
                    # Запись уже есть. Прописываем ей новое время открытия и увеличиваем счетчик открытий
                    # Получаем количество открытий данного файла
                    app_settings.state_db_connection.execute("SELECT count_opens, current_position FROM file_recs WHERE filename=?", (filename,))
                    rec_count_opens, rec_current_position = app_settings.state_db_connection.fetchone()
                    #print('Количество открытий заметки: %s, последняя позиция курсора: %s' % (rec_count_opens, rec_current_position))
                    if not dont_save_in_history:
                        # Обновляем запись в базе
                        app_settings.state_db_connection.execute("UPDATE file_recs SET last_open=?, count_opens=?  WHERE filename=?",
                                                    (datetime.now(), rec_count_opens + 1, filename))
                        app_settings.state_db.commit()
                else:
                    # Записи нет. Создаем новую.
                    # print ( 'rec_tmp: '+str(rec_tmp)+' len:'+str(len(rec_tmp)) )

                    rec_current_position = None
                    #print('FILE_RECS: для файла %s записи нет. Создаем новую.' % filename)
                    # print ( 'rec_tmp: '+str(rec_tmp)+' len:'+str(len(rec_tmp)) )

                    if not dont_save_in_history:
                        app_settings.state_db_connection.execute("INSERT INTO file_recs (filename, last_open, count_opens) VALUES (?,?,?)",
                                                        (filename, datetime.now(), 1))
                        app_settings.state_db.commit()

        if not dont_save_in_history:
            # Добавляем элемент к отдельному списку истории
            notelist.update_history_items_with_one(filename)

        fileObj = codecs.open(filename, "r", "utf-8")
        lines = fileObj.read()        
        fileObj.close()

        self.extract_real_styles_note_format()

        # Translate plain text to html and set as doc source
        note_source = note.convert_zim_text_to_html_source(lines)
        self.doc_source.setHtml(note_source)
        self.textBrowser_Note.setDocument(self.doc_source)


        # Передвигаем курсор на нужную позицию
        self.textBrowser_Note.moveCursor(QtGui.QTextCursor.Start)
        
        if not line_number == None:  # Используем -1 а не None - чтобы Питон не делал из None-переменной 0
            # У нас указано - на какую строку перематывать
            #print('Выполняется промотка на линию "%s" и поиск текста "%s"' % (line_number, found_text) )

            # Отключаем перенос строк в редакторе
            self.textBrowser_Note.setLineWrapMode(QtWidgets.QTextEdit.NoWrap)

            # Получаем копию текущего курсора
            cursor = self.textBrowser_Note.textCursor()

            # Учитываем в количестве переходов по строкам количество удаленных служебных строк в начале заметки
            lines_to_skip = int(line_number)-len(note.metadata_lines_before_note)-1
            cursor.movePosition( QtGui.QTextCursor.Down, n=lines_to_skip )

            # Восстанавливаем перенос по словам
            self.textBrowser_Note.setLineWrapMode(QtWidgets.QTextEdit.WidgetWidth)

            main_window.textBrowser_Note.setTextCursor(cursor)
            main_window.textBrowser_Note.ensureCursorVisible()
                        
            ## Надо промотать скроллбокс немного ниже или выше, чтобы отобразить курсор примерно в середине окна
            ## Надо получить положение текущего курсора в тексте с учетом переносов строк
            ##cursor = self.textBrowser_Note.textCursor()
            #pos1 = cursor.position()
            #line_current = text_format.getLineAtPosition3(pos1)
            
            #cursor.movePosition(QtGui.QTextCursor.End)
            #pos2 = cursor.position()
            #lines_all = text_format.getLineAtPosition3(pos2)

            #print('Информация для расчета изменения промотки: pos1 %s / line_current %s, pos2 %s / lines_all %s' % (pos1, line_current, pos2, lines_all))

            #self.adjust_scrollbar_position_at_editor(main_window.textBrowser_Note, line_current, lines_all)

        # self.textBrowser_Note.setTextCursor(cursor)

        main_window.frameSearchInNote.setVisible(False)
        note.set_visible()
        self.textBrowser_Note.setFocus()
        
        # file_cute_name = filename.rpartition('/')[2]
        # file_cute_name = filename.rpartition(os.path.sep)[2]
        # file_cute_name = file_cute_name.replace('_', ' ')
        # file_cute_name = file_cute_name.rpartition('.txt')[0]
        file_cute_name = notelist.make_cute_name(filename)

        self.setWindowTitle(app_settings.Name + ' - ' + file_cute_name)
        self.statusbar.showMessage('Заметка загружена')
        self.current_open_note_link = filename
        self.renew_history_lists(filename)

        # Получаем копию текущего курсора
        cursor = main_window.textBrowser_Note.textCursor()

        # Проверяем - делали ли промотку на нужную позицию найденного текста
        if not line_number == None:
           #print('Перемещение курсора на последнюю сохраненную позицию не нужно - у нас был переход на позицию найденного текста.')
           pass
        elif rec_current_position:
            # Восстанавливаем позицию предыдущую позицию курсора, если она была сохранена
            #print('Перемещаем курсор в заметке на позицию %s' % rec_current_position)
            # Устанавливаем копии нужное положение
            cursor.setPosition(rec_current_position)
            # Делаем копию основным курсором текстового редактора с новой позицией
            main_window.textBrowser_Note.setTextCursor(cursor)
        else:
            #print('Информации по позиции курсора в заметке не найдено.')
            pass

        # rec = [ 'note' / 'list', 'filename' / 'filter', datetime ]
        # if history_position==0:
        #    history_recs.append(['note', filename, datetime.now()])

        # Надо промотать скроллбокс немного ниже или выше, чтобы отобразить курсор примерно в середине окна
        # Надо получить положение текущего курсора в тексте с учетом переносов строк
        #cursor = self.textBrowser_Note.textCursor()
        pos1 = cursor.position()
        line_current = text_format.getLineAtPosition3(pos1)
            
        cursor.movePosition(QtGui.QTextCursor.End)
        pos2 = cursor.position()
        lines_all = text_format.getLineAtPosition3(pos2)

        #print('Информация для расчета изменения промотки: pos1 %s / line_current %s, pos2 %s / lines_all %s' % (pos1, line_current, pos2, lines_all))

        self.adjust_scrollbar_position_at_editor(main_window.textBrowser_Note, line_current, lines_all)




    def loadfile2(self, url):
        # self.ui.listView.
        # app_settings.path_to_notes + filenames[self.ui.listWidget.currentRow()]
        # filenames[self.ui.listWidget.currentRow()]
        # self.textEdit.setPlainText(url.toString())
        
        # Переход совершен из списка, сбрасываем позицию перемещения
        # в списке истории.
        notelist.history_position = 0
        self.open_file_in_editor(url.toString())

    def loadfile_from_history(self, url):
        # Переход совершен из истории, сбрасываем позицию перемещения
        # в списке истории, а также скрываем поле фильтрам списка
        # заметок по названию
        notelist.history_position = 0
        # self.frameNotelist_Filter.setVisible(False)
        # self.actionFast_jump_to_file_or_section.setChecked(False)
        self.open_file_in_editor(url.toString())

    def open_link(self, url):
        # Запуск программ из Питон:
        # http://www.py-my.ru/post/4bfb3c691d41c846bc000061
        # link = url.toString()
        
        # Сделать разбор линков
        # if link[:5]=='http://'
        # if link[:5]=='ftp://'
        
        # import subprocess
        # cmd = 'firefox '+link
        # subprocess.Popen(cmd, shell = True)

        self.open_file_in_editor(url.toString())

    # def load_editor_css(self, filename):
        # Обсуждения загрузки css:
        # http://www.qtcentre.org/threads/48240-Styling-a-QTextEdit
        # http://www.qtcentre.org/wiki/index.php?title=QTextBrowser_with_images_and_CSS
        # f = open(filename, "r")
        # lines = f.read()
        # f.close()
        # self.textEdit.setStyleSheet(lines)
        # self.textBrowser_Note.setStyleSheet(lines)
        # self.textBrowser_Note
        # self.doc_source.addResource(QTextDocument.StyleSheetResource, QtCore.QUrl( "default.css" ), lines)
        # self.doc_source.setHtml('<html>\
        # <head><link rel="stylesheet" type="text/css" href="styles/default.css"></head>\
        # <body>123<h3>123</h3></body></html>')
        # self.doc_source.setHtml('<html><body>123<h3>123</h3></body></html>')
        # self.textBrowser_Note.setDocument(self.doc_source)

    def copy_snippet_text_to_clipboard(self, number):
        print('Копируем в буфер сниппет номер %s' % number)
        text = app_settings.snippet_actions[number].statusTip()
        print('Полученный текст: %s' % text)
        cb = QtGui.QGuiApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(text, mode=cb.Clipboard)


    def edit_snippets(self):
        fname = app_settings.snippets_filename
        print('Открываем сниппеты для редактирования: %s' % fname)
        self.open_file_in_editor(fname, dont_save_in_history=True)

    def show_snippets(self):
        fname = app_settings.snippets_filename
        total_text = ''
        snippets = []
        print('Генерим список сниппетов и добавляем их в меню из файла %s' % fname)
        # Проверяем существование файла
        if os.path.isfile(fname):
            # Загружаем содержимое файла
            fileObj = codecs.open(fname, "r", "utf-8")
            lines = fileObj.read()
            lines_without_comments = []
            fileObj.close()
            # print(lines)
            # Перебираем строки и добавляем в меню
            is_first_block_of_comments = True
            for line in lines.splitlines():
                # Проверяем блок комментариев в начале
                if is_first_block_of_comments:
                    if line.startswith(';;'):
                        continue
                    else:
                        is_first_block_of_comments = False
                # Теперь остался несущий текст. Собираем его в один массив
                # print(line)
                lines_without_comments.append(line)
            # Сбор остального текста закончили
            # Разбиваем на блоки по сепараторам
            total_text = '\n'.join(lines_without_comments)
            snippets = total_text.split(app_settings.snippets_separator)
            # print(total_text.splitlines())
            # print(snippets)

            # Удаляем старые пункты меню и очищаем массив действий
            # for one_action in app_settings.snippet_actions:
            #     self.menuSnippets.removeAction(one_action)
            self.menuSnippets.clear()
            app_settings.snippet_actions = []

            snippet_ndx = -1
            # Добавляем новые пункты меню
            for snippet in snippets:
                # Перебираем сниппеты. Очищаем от лишнего.
                # Разделяем заголовок и текст
                snippet = snippet.strip('\n')
                snippet_lines = snippet.split('\n')
                print()
                snippet_name = snippet_lines[0]
                snippet_text = '\n'.join(snippet_lines[1:])
                if not snippet_name:
                    continue
                print('Заголовок: %s' % snippet_name)
                print('Текст: %s' % snippet_text)

                # exitAction = QAction(QIcon('exit.png'), 'snippet_name', self)
                # exitAction.setShortcut('Ctrl+Q')
                # exitAction.setStatusTip('Exit application')
                # exitAction.triggered.connect(qApp.quit)

                snippet_ndx += 1  # Увеличиваем индекс текущего сниппета
                print('snippet_ndx: %s' % snippet_ndx)
                app_settings.snippet_actions.append(
                    QtWidgets.QAction(QtGui.QIcon('clipboard.png'), snippet_name, self.menuSnippets) )
                app_settings.snippet_actions[snippet_ndx].setStatusTip(snippet_text)

                # О том, как передать параметр в цикличном создании QAction
                # и связывании их с функцией:
                # https://stackoverflow.com/questions/40322041/how-in-pyqt-connect-button-to-a-function-with-a-specific-parameter
                app_settings.snippet_actions[snippet_ndx].triggered.connect(lambda arg, snippet_ndx=snippet_ndx: self.copy_snippet_text_to_clipboard(snippet_ndx))

                self.menuSnippets.addAction(app_settings.snippet_actions[snippet_ndx])



            # Добавляем сепаратор
            self.menuSnippets.addSeparator()

            # Добавляем пункт редактирования сниппетов

            app_settings.snippet_actions.append(QtWidgets.QAction(
                QtGui.QIcon('edit.png'), 'Редактирование сниппетов..', self.menuSnippets))

            app_settings.snippet_actions[-1].triggered.connect(
                self.edit_snippets )
            self.menuSnippets.addAction(app_settings.snippet_actions[-1])


        else:
            print('Такого файла не существует')




class Theme():
    """ Все что определяет работу с темами интерфейса и текста
    """
    
    themes = ['default_for_dark_system_theme', 'default_light']

    current_theme_css = 'styles/%s.css' % themes[1]

    html_theme_head = '<head><link rel="stylesheet" type="text/css" href="%s"></head>' % current_theme_css


class Note():
    """ Все что определяет работу с заметкой:
    загрузка, форматирование, редактирование, сохранение, UI
    
    *UI* (main_window):
    frameSearchInNote, lineTextToFind
    textBrowser
    doc_source  (исходник документа)
    """
    # cursor_format = QTextCharFormat
    # cursor = QtGui.QTextCursor(main_window.doc_source)
    
    paste_as_text_once = False

    filename = ''        # Ссылка на файл открытой заметки. Внутренняя тема для класса Notes. Повсеместно для определения урла открытой заметки используется main_window.current_open_note_link
    format_type = 'zim'  # zim, md, ...
    metadata_lines_before_note = ''  # Специальные поля заметки, например, от Zim, которые надо сохранить и записать при сохранении

    # Символ пробела для замены и сохранения пробелов в исходнике для редактора
    #space_symbol = '&ensp;'
    #space_symbol = '&emsp;'
    #space_symbol = '&nbsp;'
    #space_symbol = '&#32;'
    #space_symbol = ' '




    def set_visible(self, visible=True):
        # Переключение видимости все что связано с непосредственным редактирование заметки
        if visible:
            # Отображаем все виджеты, связанные Note
            main_window.stackedWidget.setCurrentIndex(1)
            # Скрываем конкурирующие виджеты
            # note.setVisible(False)
            table_of_note_contents.setVisible(False)
            notelist.set_visible(False)

        # Переключаем все действия, связанные с форматирование и редактирование заметки
        # note_actions = [
            # main_window.actionAdd_Link, main_window.actionAdd_Image,
            # main_window.actionBold, main_window.actionItalic,
            # main_window.actionStrikethrough, main_window.actionMark,
            # main_window.actionBullet_List, main_window.actionNumber_List,
            # main_window.actionHeading_1, main_window.actionHeading_2,
            # main_window.actionHeading_3, main_window.actionHeading_4,
            # main_window.actionHeading_5, main_window.actionHeading_6,
            # main_window.actionUndo, main_window.actionRedo,
            # main_window.actionClear, main_window.actionFind_in_current_note,
            # main_window.actionFind_next_in_cur_note,
            # main_window.actionShow_content_collapse_all_H,
            # main_window.actionCollapse_all_H_exclude_cur,
            # main_window.actionCollapse_cur_H, main_window.actionExpand_all_H,
            # main_window.actionSave_note, main_window.action_ClearFormat,
            # main_window.actionCode]
        # main_window.actionNote_multiaction,
        # main_window.actionShow_note_contents
        # for action in note_actions:
        for action in main_window.note_editor_actions:
            # action.setEnabled(visible)
            action.setVisible(visible)
        for menu in main_window.note_editor_root_menus:
            # action.setEnabled(visible)
            menu.menuAction().setVisible(visible)

                # Переключаем соотстветствующее отображению действие
        # main_window.actionFast_jump_to_file_or_section.setChecked(visible)

    def is_visible(self):
        if main_window.stackedWidget.currentIndex() == 1:
            return True
        else:
            return False

    def get_span_under_cursor(self, cursor, only_style=False):
        # Функция извлечения очищенного html-кода под курсором
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor)
        html_under_cursor = cursor.selection().toHtml()
        clear_html_under_cursor = self.clear_selection_html_cover(html_under_cursor)
        #print('clear_html_under_cursor ##%s##' % clear_html_under_cursor)
        html_span = clear_html_under_cursor.partition('<span')[2]
        #print('part <span  ###%s###' % html_span)
        if only_style:
            #print('Only style!')
            html_span = html_span.partition('>')[0].lstrip()
        else:
            html_span = '<span' + html_span.partition('>')[0] + '>'
        #print('html_span ##%s##' % html_span)
        #print()
        return html_span

    #def get_style_from_span_under_cursor(self, cursor):
    #    html_span = self.get_span_under_cursor(cursor)
    #    print('STYLE html_span  ###%s###' % html_span)
    #    html_style = html_span.partition('style="')[2]
    #    print('html_style 1  ###%s###' % html_style)
    #    html_style = html_span.rpartition('">')[0]
    #    print('html_style 2  ###%s###' % html_style)
    #    return html_style



    def union_concat_ident_span(self, note_source):
        # Найти и склеить все одинаковые по стилю span в строчках ( разделение по <p> и <br> ), включая
        # <span> разделенные пробелами
        # str.find(sub[, start[, end]])
        
        pos = 0
        span_end = '</span>'
        span_begin = '<span '
        str_sign_concat = span_end + span_begin
         
        while note_source.find(str_sign_concat, pos) >= 0:
            # Позиция обнаруженного сочленения двух span
            pos_concat = note_source.find(str_sign_concat, pos)
            # Ищем конец правого span
            pos_rspan_begin = pos_concat + len(span_end)
            pos_rspan_end = note_source.find('>', pos_rspan_begin + len(span_begin)) + 1
            # Ищем начало левого span
            pos_lspan_begin = note_source.rfind(span_begin, 0, pos_concat)
            pos_lspan_end = note_source.find('>', pos_lspan_begin) + 1
            
            lspan = note_source[pos_lspan_begin: pos_lspan_end]
            rspan = note_source[pos_rspan_begin: pos_rspan_end]
            
            # print ('Найдено сочленение на позиции',pos_concat,', span-позиции:', pos_lspan_begin, '-', pos_lspan_end,
            # ', ', pos_rspan_begin, '-', pos_rspan_end)
            # print ('Результата вырезки 1: '+lspan)
            # print ('Результата вырезки 2: '+rspan)
            
            if lspan == rspan:
                # Делаем склейку двух одинаковых span
                note_source_result = note_source[:pos_concat] + note_source[pos_rspan_end:]
                note_source = note_source_result
                pos = pos_concat
            else:
                pos = pos_concat + 1        

        return note_source

    def make_all_links_to_wiki_format(self, note_source):
        # Проанализировать и заменить все ссылки <a> на ссылки вики-формата или чистый текст
        
        pos = 0
        str_a_begin = '<a href="'
        str_a_middle = '">'
        str_a_end = '</a>'
        # FIXME: .. не работает сохранение и восстановление ссылок где текст и ссылка различаются
         
        while note_source.find(str_a_begin, pos) >= 0:
            # Позиция обнаруженного линка
            pos_a_begin = note_source.find(str_a_begin, pos)
            # Ищем середину линка
            pos_a_middle = note_source.find(str_a_middle, pos_a_begin)
            # Ищем конец линка
            pos_a_end = note_source.find(str_a_end, pos_a_middle)
            
            # Вынимаем href и текст ссылки
            a_href = note_source[pos_a_begin + len(str_a_begin): pos_a_middle]
            a_text = note_source[pos_a_middle + len(str_a_middle): pos_a_end]
            a_text = re.sub('<span .*?>(.*)</span>', '\\1', a_text)
            # print ('a: '+note_source[ pos_a_begin : pos_a_end+len(str_a_end) ])
            # print ('a_href: '+a_href)
            # print ('a_text: '+a_text)
            
            if a_href == a_text:
                # print ('У нас простая ссылка')
                # У нас простая ссылка на что-то.
                # Определяем - на что ссылается a_href
                if '://' in a_href and ' ' not in a_href: 
                    # Внешний линк
                    # print ('Внешний линк: '+a_href)
                    note_source = note_source[: pos_a_begin] + a_href + note_source[pos_a_end + len(str_a_end):]
                else:
                    # Внутренний или на местные файлы линк
                    note_source = note_source[: pos_a_begin] + '[[' + a_href + ']]' + note_source[pos_a_end + len(str_a_end):]
            else:
                # print ('У нас ссылка с подмененным текстом!')
                # У нас ссылка с подмененным текстом
                # [[1234|text]]
                # Обрабатывается нормально на сохранение в блоке выше, но открытие пока не обрабатывается. 
                print ('У нас текст ссылки отличается от текста:')
                print( note_source[pos_a_begin: pos_a_end] )
                print ('a_href: '+a_href)
                print ('a_text: '+a_text)

                note_source = note_source[: pos_a_begin] + '[[' + a_href + '|' + a_text + ']]' + note_source[pos_a_end +
                                                   len(str_a_end):]
            
            pos = pos_a_begin

        return note_source

    def clear_selection_html_cover(self, html_source):
        # Удаляем html-обертку кода выделенного фрагмента заметки
        # Удаляем лишние переносы строк \n
        html_source = html_source.replace('\n', '')
        start_str = '<!--StartFragment-->'
        end_str = '<!--EndFragment-->'
        if start_str in html_source: 
            html_source = html_source.split(start_str)[1]
        if end_str in html_source: 
            html_source = html_source.split(end_str)[0]
        return html_source

    def clear_note_html_cover(self, note_source):
        # Удаляем html-обертку основного кода заметки
        # profiler.checkpoint('Начинаем очистку исходника html заметки')
        # Удаляем лишние переносы строк \n
        note_source = note_source.replace('\n', '')
        # Удаляем окантовку контента, включая <body> и крайний <p>
        pos_cut1 = note_source.find('<p ')
        pos_cut1 = note_source.find('>', pos_cut1)
        # print ('Начало html после удаления начала обертки: \n'+note_source[pos_cut1+1:pos_cut1+40]+'\n')
        
        pos_cut2 = note_source.rfind('</p>')
        # print ('Конец html после удаления конца обертки: \n'+note_source[pos_cut2-40:pos_cut2-1]+'\n')

        note_source = note_source[pos_cut1 + 1:pos_cut2]
        return note_source
    

    def health_bad_links(self, filename, html_source):
        # Лечение ссылок, испорченных ранее в самых первых версиях RelaNotes
        # [[http://webcast.emg.fm:55655/keks128.mp3.m3u|http://webcast.emg.fm:55655/]]keks128.mp3.m3u
        
        # html_source = re.sub('[[(.*?)|(.*?)]](.*?)', '\\1', html_source)
        # re.sub('\[\[(?!\[)(.+?)\]\]', '\\1', html_source)

        #html_source = re.sub('\[\[(.+?)\|(.+?)\]\](.+?)', '\\2', html_source)
        
        #AllLinksRegex = re.compile(r'\[\[(?!\[)(.*?)\]\]')
        #NoteSelectedLinks = AllLinksRegex.search(html_source)
        #if NoteSelectedLinks:
            #print('В файле %s найдены ссылки:' % filename)
            # html_source = html_source + ' ### ' + NoteSelectedText.group(1)
            #print(NoteSelectedLinks)
            #health_link = NoteSelectedText.group(1)
            #print('Исправленный линк: ##%s##' % health_link)
        

        #def normalize_orders(matchobj):
        #    if matchobj.group(1) == '-': return "A"
        #    else: return "B"
        #re.sub('([-|A-Z])', normalize_orders, '-1234⇢A193⇢ B123')

        def hide_inline_url(matchobj):
            #print('  groups: %s' % matchobj.group(0))
            matching_string = ''
            result = ''
            matching_string = matchobj.group(0)
            if '://' in matching_string:
                print('  group(0): %s' % matching_string)
                print('  group(1): %s' % matchobj.group(1))
                #print('  group(2): %s' % matchobj.group(2))
                #print('  group(3): %s' % matchobj.group(3))
                result = matching_string.replace('://', ':/&#x2F;')
                print('  after replace: %s' % result)
            else:
                result = matching_string
            #if matchobj.group(1) == '-': return "A"
            #else: return "B"
            return result

        #re.sub('([-|A-Z])', normalize_orders, '-1234⇢A193⇢ B123')

        #StrikeRegex = re.compile(r'(~~)(?!~)(.+?)(~~)')
        StrikeRegex = re.compile(r'~~(?!~)(.+?)~~')
        
        NoteSelectedText = StrikeRegex.findall(html_source)
        if NoteSelectedText:
            print('\nВ файле %s \nнайден зачеркнутый текст: ' % filename)
            for one_text in NoteSelectedText:
                if '://' in one_text:
                    print(' %s' % one_text)

        html_source = StrikeRegex.sub(hide_inline_url, html_source)

        NoteSelectedText = StrikeRegex.findall(html_source)
        if NoteSelectedText:
            print('\nПосле изменения он выглядит так: ')
            for one_text in NoteSelectedText:
                if ':/' in one_text:
                    print(' %s' % one_text)

        return 0

        #pattern = re.compile(r'\*(.*?)\*')
        #>>> pattern.sub(r"<b>\g<1>1<\\b>", text)
        #'imagine⇢a⇢new⇢<b>world1<\\b>,⇢a⇢magic⇢<b>world1<\\b>'


        BadLinksRegex = re.compile('\[\[(.+?)\|(.+?)\]\](.+?)')
        #NoteSelectedText = BadLinksRegex.search(html_source)
        NoteSelectedText = BadLinksRegex.findall(html_source)
        if NoteSelectedText:
            print('\nВ файле %s \nопознаны плохие ссылки: ' % filename)
            for one_text in NoteSelectedText:
                #print(NoteSelectedText)
                print(one_text)
                # html_source = html_source + ' ### ' + NoteSelectedText.group(1)
                #health_link = NoteSelectedText.group(1)
                #health_link = one_text.group(1)
                #print('Исправленный линк: ##%s##' % health_link)

        BadLinksRegex2 = re.compile('&lt;s&gt;(.+?)&lt;/s&gt;')
        #NoteSelectedText = BadLinksRegex2.search(html_source)
        NoteSelectedText = BadLinksRegex2.findall(html_source)
        if NoteSelectedText:
            print('\nВ файле %s \nопознаны плохие ссылки второго типа:' % filename)
            #print(NoteSelectedText)
            for one_text in NoteSelectedText:
                #print(NoteSelectedText)
                print(one_text)




    def convert_zim_text_to_html_source(self, text):
        # Конвертируем текст заметок Zim в формат для редактора заметки

        # Оригинальный код был из функции open_file_in_editor        

        # print()
        # print('1 ### convert_zim_text_to_html_source:')
        # print(text)
        # make_initiative_html

        html_source = text
        # html_source = self.textBrowser_Note.toHtml()
        # set header, include css style

        # 'blockstart': re.compile("^(\t*''')\s*?\n", re.M),
        # 'pre':        re.compile("^(?P<escape>\t*''')\s*?(?P<content>^.*?)^(?P=escape)\s*\n", re.M | re.S),
        # 'splithead':  re.compile('^(==+[ \t]+\S.*?\n)', re.M),
        # 'heading':    re.compile("\A((==+)[ \t]+(.*?)([ \t]+==+)?[ \t]*\n?)\Z"),
        # 'splitlist':  re.compile("((?:^[ \t]*(?:%s)[ \t]+.*\n?)+)" % bullet_re, re.M),
        # 'listitem':   re.compile("^([ \t]*)(%s)[ \t]+(.*\n?)" % bullet_re),
        # 'unindented_line': re.compile('^\S', re.M),
        # 'indent':     re.compile('^(\t+)'),


        # Remove ZIM wiki tags from first strings of note:
        # Content-Type:
        # Wiki-Format:
        # Creation-Date:
        zim_wiki_tags = ['Content-Type', 'Wiki-Format', 'Creation-Date']
        self.metadata_lines_before_note = []

        # 1. Режем контент заметки на строки
        text_source_lines = html_source.splitlines()  # ('\n')
        # Проверяем на наличие двух линукс-переносов строк вида \n подряд в конце файла заметки. Из таких переносов один теряется при использовании splitlines. Надо исправить этот баг вручную.
        # if text.endswith(os.linesep+os.linesep):
        # if text.endswith('\n\n'):
        #    # У нас именно такой случай. Добавляем к массиву строк ещё одну пустую
        #    #print('Обнаружили, что текст оканчивается на 2 переноса строк')
        #    text_source_lines.append('')
        # print('### text_source_lines: %s' % text_source_lines)


        first_part1 = first_part2 = first_part3 = ''
        # 2. Проверяем наличие ключевых слов в первых 3 строчках
        if len(text_source_lines) > 0:
            first_part1 = text_source_lines[0].split(':')[0]
        if len(text_source_lines) > 1:
            first_part2 = text_source_lines[1].split(':')[0]
        if len(text_source_lines) > 2:
            first_part3 = text_source_lines[2].split(':')[0]
        
        # 3. Удаляем строки, в которых обнаружены служебные слова
        if first_part1 in zim_wiki_tags and first_part2 in zim_wiki_tags and first_part3 in zim_wiki_tags:
            # Удаляем первые 3 строчки
            # print('Найдены 3 строки метаданных Zim')
            # print(text_source_lines[0:3])
            self.metadata_lines_before_note = text_source_lines[0:3]
            del text_source_lines[0:3]
        
        if first_part1 in zim_wiki_tags and first_part2 in zim_wiki_tags and first_part3 not in zim_wiki_tags:
            # Удаляем первые 2 строчки
            # print('Найденые 2 строки метаданных Zim')
            # print(text_source_lines[0:2])
            self.metadata_lines_before_note = text_source_lines[0:2]
            del text_source_lines[0:2]

        if first_part1 in zim_wiki_tags and first_part2 not in zim_wiki_tags and first_part3 not in zim_wiki_tags:
            # Удаляем первую строчку
            # print('Найдена 1 строка метаданных Zim')
            # print(text_source_lines[0:1])
            self.metadata_lines_before_note = text_source_lines[0:1]
            del text_source_lines[0:1]

        # 4. Если осталась первая пустая строка - удаляем и её (она обычно остается после служебных)
        if len(text_source_lines) > 0 and not text_source_lines[0].strip():
            # Удаляем первую строчку
            # print('А ещё найдена пустая строка после метаданных Zim.')
            self.metadata_lines_before_note.append(text_source_lines[0])
            del text_source_lines[0:1]


        # print('self.metadata_lines_before_note:')
        # print(self.metadata_lines_before_note)

        # print('2 ### convert_zim_text_to_html_source:')
        # print(text)


        # x. Собираем контент заметки обратно в строки
        
        new_text_source_lines = []
        for one_line in text_source_lines:
            #new_text_source_lines.append(html.escape(one_line).replace(' ', self.space_symbol))
            new_text_source_lines.append(html.escape(one_line))

        # html_source = '\n'.join(new_text_source_lines)
        html_source = ''
        for one_line in new_text_source_lines:
            html_source += one_line + '\n'

        # А тут надо использовать системный перенос строк: os.linesep

        # html_source = '\n'.join(text_source_lines)
        
        # print('3 ### convert_zim_text_to_html_source:')
        # print('###'+html_source+'###')

        # html_source = urllib.request.quote(html_source)

        #self.health_bad_links(html_source)
          
     #   _classes = {'c': r'[^\s"<>\']'} # limit the character class a bit
     #   url_re = Re(r'''(
	    #    \b \w[\w\+\-\.]+:// %(c)s* \[ %(c)s+ \] (?: %(c)s+ [\w/] )?  |
	    #    \b \w[\w\+\-\.]+:// %(c)s+ [\w/]                             |
	    #    \b mailto: %(c)s+ \@ %(c)s* \[ %(c)s+ \] (?: %(c)s+ [\w/] )? |
	    #    \b mailto: %(c)s+ \@ %(c)s+ [\w/]                            |
	    #    \b %(c)s+ \@ %(c)s+ \. \w+ \b
     #   )''' % _classes, re.X | re.U)
	    ## Full url regex - much more strict then the is_url_re
	    ## The host name in an uri can be "[hex:hex:..]" for ipv6
	    ## but we do not want to match "[http://foo.org]"
	    ## See rfc/3986 for the official -but unpractical- regex

        # html_source = re.sub('(Created [^\n]*)', '<font id="created">\\1</font>', html_source)
        # Информация после заголовка о времени создания заметки.
        # Наследство Zim.
        html_source = re.sub('=\n(Created [^\n]*[\d]{4})', '=\n<font id="created">\\1</font>', html_source, re.M)


        # print()
        # print('После удаления служебных полей Zim:')
        # print(html_source)

        # html_source = re.sub('(Content-Type: text/x-zim-wiki)', '<!--', html_source)
        # html_source = re.sub('(======) (.*?) (======)\n', '--><font id=hide>\\1</font> <font id=head1>\\2</font>
        #  <font id=hide>\\3</font><br>', html_source)
        # html_source = re.sub('====== (.*?) ======\n', '--><h1>\\1</h1>', html_source)
        # html_source = re.sub('===== (.*?) =====', '<h2>\\1</h2>', html_source)
        # html_source = re.sub('==== (.*?) ====', '<h3>\\1</h3>', html_source)
        # html_source = re.sub('=== (.*?) ===', '<h4>\\1</h4>', html_source)
        # html_source = re.sub('== (.*?) ==', '<h5>\\1</h5>', html_source)
        # html_source = re.sub('= (.*?) =', '<h6>\\1</h6>', html_source)
        
        # FIXME: скрытие служебных полей начала контента вики сделано неправильно, рассчитано только на 1 H1
        # html_source = re.sub('====== (.*?) ======', '--><font id=head1>\\1</font>', html_source)



        # html_source = re.sub('====== (.*?) ======', '<font id=head1>\\1</font>', html_source)
        # html_source = re.sub('===== (.*?) =====', '<font id=head2>\\1</font>', html_source)
        # html_source = re.sub('==== (.*?) ====', '<font id=head3>\\1</font>', html_source)
        # html_source = re.sub('=== (.*?) ===', '<font id=head4>\\1</font>', html_source)
        # html_source = re.sub('== (.*?) ==', '<font id=head5>\\1</font>', html_source)
        # html_source = re.sub('= (.*?) =', '<font id=head6>\\1</font>', html_source)

        #html_source = re.sub('====== (.*?) ======', '<font id=head1>\\1</font>', html_source)
        #html_source = re.sub('===== (.*?) =====', '<font id=head2>\\1</font>', html_source)
        #html_source = re.sub('==== (.*?) ====', '<font id=head3>\\1</font>', html_source)
        #html_source = re.sub('=== (.*?) ===', '<font id=head4>\\1</font>', html_source)
        #html_source = re.sub('== (.*?) ==', '<font id=head5>\\1</font>', html_source)
        #html_source = re.sub('= (.*?) =', '<font id=head6>\\1</font>', html_source)

        # Заголовки после переноса строки
        html_source = re.sub('\n====== (.*?) ======', '<div id=head1>\\1</div>', html_source)
        html_source = re.sub('\n===== (.*?) =====', '<div id=head2>\\1</div>', html_source)
        html_source = re.sub('\n==== (.*?) ====', '<div id=head3>\\1</div>', html_source)
        html_source = re.sub('\n=== (.*?) ===', '<div id=head4>\\1</div>', html_source)
        html_source = re.sub('\n== (.*?) ==', '<div id=head5>\\1</div>', html_source)
        html_source = re.sub('\n= (.*?) =', '<div id=head6>\\1</div>', html_source)

        # Те-же заголовки но в самом начале заметки
        html_source = re.sub('^====== (.*?) ======', '<div id=head1>\\1</div>', html_source)
        html_source = re.sub('^===== (.*?) =====', '<div id=head2>\\1</div>', html_source)
        html_source = re.sub('^==== (.*?) ====', '<div id=head3>\\1</div>', html_source)
        html_source = re.sub('^=== (.*?) ===', '<div id=head4>\\1</div>', html_source)
        html_source = re.sub('^== (.*?) ==', '<div id=head5>\\1</div>', html_source)
        html_source = re.sub('^= (.*?) =', '<div id=head6>\\1</div>', html_source)

        
        # html_source = re.sub('====== (.*?) ======', '--><p id=head1>\\1</p>', html_source)
        # html_source = re.sub('===== (.*?) =====', '<p id=head2>\\1</p>', html_source)
        # html_source = re.sub('==== (.*?) ====', '<p id=head3>\\1</p>', html_source)
        # html_source = re.sub('=== (.*?) ===', '<p id=head4>\\1</p>', html_source)
        # html_source = re.sub('== (.*?) ==', '<p id=head5>\\1</p>', html_source)
        # html_source = re.sub('= (.*?) =', '<p id=head6>\\1</p>', html_source)
        
        # print()
        # print('После замены заголовков:')
        # print(html_source)

        # TODO: re.search, groups - обнаружение и сохранение позиций вики-форматирования
        
        # 'strong':   Re('\*\*(?!\*)(.+?)\*\*'),
        #html_source = re.sub('\*\*(.*?)\*\*', '<strong>\\1</strong>', html_source)
        html_source = re.sub(r'\*\*(?!\*)(.*?)\*\*', '<strong>\\1</strong>', html_source)

        #html_source = re.sub('//(.*?)//', '<i>\\1</i>', html_source)
        html_source = re.sub(r'//(?!/)(.*?)//', '<i>\\1</i>', html_source)

        # 'strike':   Re('~~(?!~)(.+?)~~'),
        

        # Замена / на альтернативное его обозначение для редактора, чтобы замаскировать ссылку внутри другого форматирования
        #html_source = re.sub('~~(.*?)://(.*?)~~', '<s>\\1:&#x2F;&#x2F;\\2</s>', html_source)
        
        #html_source = re.sub('~~(.*?)~~', '<s>\\1</s>', html_source)
        html_source = re.sub(r'~~(?!~)(.+?)~~', '<s>\\1</s>', html_source)

        # 'emphasis': Re('//(?!/)(.+?)//'),

        # html_source = re.sub('\n\* ([^\n]*)', '<ul><li>\\1</li></ul>', html_source)
        #html_source = re.sub('\n\* ([^\n]*)', '<ul><li>\\1</li></ul>', html_source)
        
        # Меняем астериски в начале строки на li
        html_source = re.sub('\n\* ([^\n]*)', '\n<ul><li>\\1</li></ul>', html_source)
        # Объединяем соседние ul
        #print('</ul><ul>: %s' % html_source.find('</ul>\n<ul>') )
        html_source = html_source.replace('</ul>\n<ul>', '')
        # Финальная очистка вокруг ul
        # Удаляем перенос строки перед ul
        #print('\n<ul>: %s' % html_source.find('\n<ul>') )
        html_source = html_source.replace('\n<ul>', '<ul>')
        # Удаляем перенос строки после ul
        #print('</ul>\n: %s' % html_source.find('</ul>\n') )
        html_source = html_source.replace('</ul>\n', '</ul>')

        # Замена переноса строк в конце ul
        #html_source = re.sub('</ul>\n\n', '</ul>\n', html_source)



        # 'code':     Re("''(?!')(.+?)''"),
        # html_source = re.sub("''(?!')(.+?)''", '<font id="code">\\1</font>', html_source)
        # html_source = re.sub("''(?!')(.+?)''", '<font id="code">\\1</font>', html_source)

        # Замена / на альтернативное его обозначение для редактора, чтобы замаскировать ссылку внутри другого форматирования
        #html_source = re.sub('&#x27;&#x27;(.*?)://(.*?)&#x27;&#x27;', '<font id="code">\\1:&#x2F;&#x2F;\\2</font>', html_source)

        html_source = re.sub("&#x27;&#x27;(?!')(.+?)&#x27;&#x27;", '<font id="code">\\1</font>', html_source)
        #html_source = re.sub(r"''(?!')(.+?)''", '<font id="code">\\1</font>', html_source)

        # 'mark':     Re('__(?!_)(.+?)__'),
        #html_source = re.sub('__(?!_)(.+?)__', '<font id="mark">\\1</font>', html_source)
        html_source = re.sub(r'__(?!_)(.*?)__', '<font id="mark">\\1</font>', html_source)

        # Внутренний линк
        # 'link':     Re('\[\[(?!\[)(.+?)\]\]'),
        #html_source = re.sub('\[\[(?!\[)(.+?)\]\]', '<a href="\\1">\\1</a>', html_source)
        html_source = re.sub(r'\[\[(?!\[)(.*?)\]\]', '<a href="\\1">\\1</a>', html_source)

        # Метка
        #TAG, r'(?<!\S)@\w+',

        # Rule(SUBSCRIPT, r'_\{(?!~)(.+?)\}')
		# Rule(SUPERSCRIPT, r'\^\{(?!~)(.+?)\}')


        # Внешний линк
        # html_source = re.sub('(http://[^ \n]*)','<a href="\\1">\\1</a>', html_source)
        html_source = re.sub('([^ \n]*://[^ \n]*)', '<a href="\\1">\\1</a>', html_source)

        # 'img':      Re('\{\{(?!\{)(.+?)\}\}'),
        #html_source = re.sub('\{\{(?!\{)(.+?)\}\}', '<img src="\\1">', html_source)
        html_source = re.sub(r'\{\{(?!\{)(.*?)\}\}', '<img src="\\1">', html_source)
        #html_source = re.sub('<img src="~', '<img src="' + path_to_home, html_source)
        
        # print()
        # print('После остальной замены:')
        # print(html_source)

        # TODO: . Сделать превращение в линк электронной почты и её сохранение

        # 'tag':        Re(r'(?<!\S)@(?P<name>\w+)\b', re.U),
        # 'sub':	    Re('_\{(?!~)(.+?)\}'),
        # 'sup':	    Re('\^\{(?!~)(.+?)\}'),
        # \n --> <br>

        html_source = html_source.replace('\n', '<br>')
        # html_source = html_source.replace('\n', '</p><p>')
        
        html_source = '<html>%s<body>%s</body></html>' % (Theme.html_theme_head, html_source,)
        
        # print('Итоговый вид html:')
        # print(html_source)

        return html_source









    def convert_html_source_to_zim_text(self, html_text):
        # Конвертируем текст из редактора заметки в формат zim
        text = html_text
            
        # Оригинальный код был из функции save_note

        # begin_of_zim_note = '\n'.join(self.metadata_lines_before_note)
        begin_of_zim_note = ''
        for one_data_line in self.metadata_lines_before_note:
            begin_of_zim_note += one_data_line + '\n'

        text = self.clear_note_html_cover(text)
        
        # Удаляем виртуальные начала строк
        text = re.sub('<p .*?>', '', text)
        # Удаляем последнее закрытие </p>
        
        # profiler.checkpoint('Проводим склейку соседних span')

        # Склеиваем одинаковые соседние span
        text = self.union_concat_ident_span(text)

        # Применяем вики-форматирование
        
        # profiler.checkpoint('Заменяем html-теги заголовков на вики-форматирование')
                
        # Заголовок    
        text = re.sub(text_format.editor_h1_span + '(.*?)</span>', '====== \\1 ======', text)
        text = re.sub(text_format.editor_h2_span + '(.*?)</span>', '===== \\1 =====', text)
        text = re.sub(text_format.editor_h3_span + '(.*?)</span>', '==== \\1 ====', text)         
        text = re.sub(text_format.editor_h4_span + '(.*?)</span>', '=== \\1 ===', text)
        text = re.sub(text_format.editor_h5_span + '(.*?)</span>', '== \\1 ==', text)
        text = re.sub(text_format.editor_h6_span + '(.*?)</span>', '= \\1 =', text)         

        # Подчеркнутый (выделенный)
        text = re.sub(text_format.editor_mark_span + '(.*?)</span>', '__\\1__', text)         
        
        # Код
        text = re.sub(text_format.editor_code_span + '(.*?)</span>', '\'\'\\1\'\'', text)         

        # profiler.checkpoint('Заменяем html-теги ссылок на вики-форматирование')

        # Ссылка
        # <a href="...">
        text = self.make_all_links_to_wiki_format(text)

        # profiler.checkpoint('Заменяем html-теги основной разметки на вики-форматирование')
        
        # Нумерованный список
        # 
        
        # Зачеркнутый текст
        # <span style=" font-family:'Sans'; font-size:15px; text-decoration: line-through; color:#aaaaaa;">
        # editor_strikethrough_span
        text = re.sub('<span [^>]*text-decoration: line-through;.*?>(.*?)</span>', '~~\\1~~', text)
        # Жирный
        # <span style=" font-family:'Sans'; font-size:15px; font-weight:600;">
        text = re.sub('<span [^>]*font-weight:600;.*?>(.*?)</span>', '**\\1**', text)
        # Наклонный
        # <span style=" font-family:'Sans'; font-size:15px; font-style:italic;">
        text = re.sub('<span [^>]*font-style:italic;.*?>(.*?)</span>', '//\\1//', text)
        
        # Картинка
        # <img src="/home/vyacheslav//Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png" />
        # -->
        # {{~/Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png}}
        # Закомментировал, не работает сейчас, выдает ошибку про незакрытый \U. Наверное, это в пути к картинке.
        # text = re.sub('<img src="'+path_to_home+'(.*?)" />', '{{~\\1}}', text)
        text = re.sub('<img src="(.*?)" />', '{{\\1}}', text)

        
        # Ненумерованный список
        # <ul style="..."><li style="..."><span style="..">Пункт 1</span></li></ul> 
        # text = re.sub('<ul .*?><li .*?>(.*?)</li></ul>', '* \\1<br />', text)
        text = re.sub('<li .*?>(.*?)</li>', '* \\1<br />', text)
        #text = re.sub('<ul .*?>(.*?)</ul>', '\\1', text)

        text = re.sub('<ul .*?>(.*?)</ul>', '\\1', text, re.MULTILINE)

        # Чистим остатки
        # profiler.checkpoint('Чистим остатки html разметки')
        
        # Удаление оставшихся span
        text = re.sub('<span .*?>', '', text)
        text = text.replace('</span>', '')
        
        # Заменяем окончания на перенос строки
        text = text.replace('</p>', '\n')
        # Заменяем html переносы строк на обычные
        text = text.replace('<br />', '\n')
        
        # text = text.replace('<a name="created"></a>','')
        text = re.sub('<a name="(.*?)"></a>', '', text)

        # profiler.stop()

        # text = urllib.request.unquote(text)
        #text = text.replace(self.space_symbol, ' ')
        text = html.unescape(text)

        # Добавляем начало файла как у Zim        
        text = begin_of_zim_note + text

        return text

                
    def save_note(self):
        # profiler.start('Начинаем сохранение заметки')

        filename = main_window.current_open_note_link

        print('Сохраняем файл %s' % filename)
        
        # Обновляем запись в базе
        app_settings.state_db_connection.execute("UPDATE file_recs SET last_change=?  WHERE filename=?",
                                    (datetime.now(), filename))
        app_settings.state_db.commit()                        
        
        # Добавляем суффикс к имени файла, при этом сохраняя оригинальное его расширение
        filename_wo_ext = os.path.splitext(filename)[0]
        filename_ext_only = os.path.splitext(filename)[-1]
        filename_suffix = '-saved'
        if not filename_suffix in filename_wo_ext:
            # Если суффикса ещё нет в имени файла- добавляем его. Иначе оставляем без изменений.
            filename = filename_wo_ext + filename_suffix + filename_ext_only

        # # Сохраняем текущую заметку с суффиксом -rt
        # tmp_str = main_window.current_open_note_link[:-len('.txt')]
        # # print ('tmp_str: '+tmp_str)
        # rt_suffix = '-rt'
        # if tmp_str[-len(rt_suffix):] == rt_suffix:
        #    filename = main_window.current_open_note_link
        # else:
        #    filename = tmp_str+rt_suffix+'.txt'
        # # print ('filename: '+filename)
        # # return 0
        # # filename = main_window.current_open_note_link+'2'
    
        note_source = main_window.textBrowser_Note.toHtml()
        note_source = self.convert_html_source_to_zim_text(note_source)

        # print('self.metadata_lines_before_note:')
        # print(self.metadata_lines_before_note)

        # begin_of_zim_note = '\n'.join(self.metadata_lines_before_note)
        # # Проверка бага с Линукс-переносом строки, когда последняя строка не сохраняется при конвертации из html
        # if self.metadata_lines_before_note[len(self.metadata_lines_before_note)-1]=='\n':
        #    begin_of_zim_note += '\n'
        # print('begin_of_zim_note: ###%s###' % begin_of_zim_note)


        if main_window.actionSave_also_note_HTML_source.isChecked():
            filename_html = main_window.current_open_note_link.replace('.txt', '.html')
            f = open(filename_html, "w")
            f.writelines(note_source)
            f.close()
        
        # note_source = self.clear_note_html_cover(note_source)
        
        # # Удаляем виртуальные начала строк
        # note_source = re.sub('<p .*?>', '', note_source)
        # # Удаляем последнее закрытие </p>
        
        # # profiler.checkpoint('Проводим склейку соседних span')

        # # Склеиваем одинаковые соседние span
        # note_source = self.union_concat_ident_span(note_source)

        # # Применяем вики-форматирование
        
        # # profiler.checkpoint('Заменяем html-теги заголовков на вики-форматирование')
                
        # # Заголовок    
        # note_source = re.sub(text_format.editor_h1_span+'(.*?)</span>', '====== \\1 ======', note_source)
        # note_source = re.sub(text_format.editor_h2_span+'(.*?)</span>', '===== \\1 =====', note_source)
        # note_source = re.sub(text_format.editor_h3_span+'(.*?)</span>', '==== \\1 ====', note_source)         
        # note_source = re.sub(text_format.editor_h4_span+'(.*?)</span>', '=== \\1 ===', note_source)
        # note_source = re.sub(text_format.editor_h5_span+'(.*?)</span>', '== \\1 ==', note_source)
        # note_source = re.sub(text_format.editor_h6_span+'(.*?)</span>', '= \\1 =', note_source)         

        # # Подчеркнутый (выделенный)
        # note_source = re.sub(text_format.editor_mark_span+'(.*?)</span>', '__\\1__', note_source)         
        
        # # Код
        # note_source = re.sub(text_format.editor_code_span+'(.*?)</span>', '\'\'\\1\'\'', note_source)         

        # # profiler.checkpoint('Заменяем html-теги ссылок на вики-форматирование')

        # # Ссылка
        # # <a href="...">
        # note_source = self.make_all_links_to_wiki_format(note_source)

        # # profiler.checkpoint('Заменяем html-теги основной разметки на вики-форматирование')
        
        # # Нумерованный список
        # # 
        
        # # Зачеркнутый текст
        # # <span style=" font-family:'Sans'; font-size:15px; text-decoration: line-through; color:#aaaaaa;">
        # # editor_strikethrough_span
        # note_source = re.sub('<span [^>]*text-decoration: line-through;.*?>(.*?)</span>', '~~\\1~~', note_source)
        # # Жирный
        # # <span style=" font-family:'Sans'; font-size:15px; font-weight:600;">
        # note_source = re.sub('<span [^>]*font-weight:600;.*?>(.*?)</span>', '**\\1**', note_source)
        # # Наклонный
        # # <span style=" font-family:'Sans'; font-size:15px; font-style:italic;">
        # note_source = re.sub('<span [^>]*font-style:italic;.*?>(.*?)</span>', '//\\1//', note_source)
        
        # # Картинка
        # # <img src="/home/vyacheslav//Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png" />
        # # -->
        # # {{~/Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png}}
        # # Закомментировал, не работает сейчас, выдает ошибку про незакрытый \U. Наверное, это в пути к картинке.
        # # note_source = re.sub('<img src="'+path_to_home+'(.*?)" />', '{{~\\1}}', note_source)
        # note_source = re.sub('<img src="(.*?)" />', '{{\\1}}', note_source)

        
        # # Ненумерованный список
        # # <ul style="..."><li style="..."><span style="..">Пункт 1</span></li></ul> 
        # # note_source = re.sub('<ul .*?><li .*?>(.*?)</li></ul>', '* \\1<br />', note_source)
        # note_source = re.sub('<li .*?>(.*?)</li>', '* \\1<br />', note_source)
        # note_source = re.sub('<ul .*?>(.*?)</ul>', '\\1', note_source)

        # # Чистим остатки
        # # profiler.checkpoint('Чистим остатки html разметки')
        
        # # Удаление оставшихся span
        # note_source = re.sub('<span .*?>', '', note_source)
        # note_source = note_source.replace('</span>', '')
        
        # # Заменяем окончания на перенос строки
        # note_source = note_source.replace('</p>', '\n')
        # # Заменяем html переносы строк на обычные
        # note_source = note_source.replace('<br />', '\n')
        
        # # note_source = note_source.replace('<a name="created"></a>','')
        # note_source = re.sub('<a name="(.*?)"></a>', '', note_source)

        # # profiler.stop()
        
        # # Добавляем начало файла как у Zim        
        # note_source = begin_of_zim_note+note_source
        
        # Записываем результат преобразования исходника заметки в файл

        # f = open(filename, "w", "utf-8")
        # f.writelines(note_source)
        # f.close()

        #print("We will save notes to %s" % filename)

        # Новое сохранение с использование кодировки UTF8
        fileObj = codecs.open(filename, "w", "utf-8")
        for one_line in note_source:
            fileObj.write(one_line)
        fileObj.close()


        # Код обновления специального меню сниппетов, если сохранен
        # такой специальный файл
        if filename == app_settings.snippets_filename:
            main_window.show_snippets()

        main_window.statusbar.showMessage('Note saved as ' + filename)
        
        # TODO: Запуск перебора всех заметок и сохранения их в альтернативный каталог
        # TODO: Diff всех файлов заметок - оригиналов и сохраненных, и коррекция сохранения.
        
        # TODO: ... А если форматирование на несколько строк?
        
    def show_note_multiaction_win_button(self):
        # if main_window.textBrowser_Note.isVisible():
        if note.is_visible():
            self.show_note_multiaction_win(main_window.current_open_note_link)
        else:
            self.show_note_multiaction_win(notelist.items_cursor_url.split('?')[1])

    def show_note_multiaction_win(self, note_filename=''):
        # if note_filename == '':
        #    note_filename = 
        
        # Получаем корректный путь к файлу из линка со всякими %2U
        note_filename = get_correct_filename_from_url(note_filename)

        notemultiaction_win.labelNoteFileName.setText(note_filename)
        notemultiaction_win.lineEdit.setText('')
        notemultiaction_win.lineEdit.setFocus()
        notemultiaction_win.show()

    def paste_as_text(self):
        self.paste_as_text_once = True
        main_window.textBrowser_Note.paste()

    def __init__(self):  # Note class
        # Прописываем реакцию на сигналы
        # QtCore.QObject.connect(main_window.textBrowser_Note, QtCore.SIGNAL("textChanged()"), text_format.update_ui)
        main_window.textBrowser_Note.textChanged.connect(text_format.update_ui)
        # QtCore.QObject.connect(main_window.textBrowser_Note, QtCore.SIGNAL("cursorPositionChanged()"), text_format.update_ui)
        main_window.textBrowser_Note.cursorPositionChanged.connect(text_format.update_ui)
        
        # QtCore.QObject.connect(main_window.doc_source, QtCore.SIGNAL("textChanged()"), text_format.updateUI)
        # QtCore.QObject.connect(main_window.doc_source, QtCore.SIGNAL("cursorPositionChanged()"), text_format.updateUI)

        # Прописываем реакцию на действия
        main_window.actionBold.triggered.connect(text_format.bold)
        main_window.actionItalic.triggered.connect(text_format.italic)
        main_window.actionStrikethrough.triggered.connect(text_format.strikethrough)
        main_window.actionCode.triggered.connect(text_format.code)
        main_window.actionMark.triggered.connect(text_format.mark)
    
        main_window.action_ClearFormat.triggered.connect(text_format.clear_format)
        main_window.actionHeading_1.triggered.connect(text_format.h1)
        main_window.actionHeading_2.triggered.connect(text_format.h2)
        main_window.actionHeading_3.triggered.connect(text_format.h3)
        main_window.actionHeading_4.triggered.connect(text_format.h4)
        main_window.actionHeading_5.triggered.connect(text_format.h5)
        main_window.actionHeading_6.triggered.connect(text_format.h6)
        
        main_window.actionSave_note.triggered.connect(self.save_note)
        main_window.actionNote_multiaction.triggered.connect(self.show_note_multiaction_win_button)
        
        main_window.actionPaste_as_text.triggered.connect(self.paste_as_text)
    
        # Скрываем дополнительные фреймы
        main_window.frameSearchInNote.setVisible(False)



class Text_Format():
        # Класс форматирования текста в редакторе и его преображение при копировании и т.д.
        # h_span_preformatting = '<span style=" font-family:\'%s\'; font-size:%spx; font-weight:%s; color:%s;">'
        
        editor_h1_span = '' 
        editor_h2_span = ''
        editor_h3_span = ''
        editor_h4_span = ''
        editor_h5_span = ''
        editor_h6_span = ''
        editor_h_span = ['0-empty', editor_h1_span, editor_h2_span, editor_h3_span, editor_h4_span, editor_h5_span, editor_h6_span]

        # FIXME: Цвет текста подходит для светлой темы. Не подходит для темной.
        editor_default_font_span = '<span style=" font-family:\'Sans\'; font-size:17px; font-weight:0; color:#1a1a1a;">'
        # editor_default_font_span = '<span>'
        
        # editor_italic_span =
        editor_strikethrough_span = \
            '<span style=" font-family:\'Sans\'; font-size:17px; text-decoration: line-through; color:#aaaaaa;">'
        # editor_bold_span =
        # FIXME: Цвет кода подходит для светлой темы. Не подходит для темной.
        # editor_code_span = '<span style=" font-family:\'Mono\'; font-size:16px; color:#501616;">'
        editor_code_span = '<span style=" font-family:\'Mono\'; font-size:17px; color:#9c2b2b;">'

        editor_mark_span = \
            '<span style=" font-family:\'Sans\'; font-size:17px; color:#1a1a1a; background-color:#ffccaa;">'
        editor_li_span = \
            '<li style=" font-family:\'Sans\'; font-size:17px;" style=" margin-top:6px; margin-bottom:6px; ' \
            'margin-left:-20px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
        
        # FIXME: Цвет ссылок подходит для светлой темы. Не подходит для темной.
        # editor_link_external_style = 'style=" font-size:15px; color:#004455; text-decoration: none;"'
        editor_link_external_style = 'style=" font-size:17px; color:#0089ab; text-decoration: none;"'

        # editor_link_local_span =
        # editor_link_wiki_span =

        editor_default_font = QtGui.QFont('Sans', 17, QtGui.QFont.Normal)
        # editor_default_font.setStyle(QFont.Normal)
        # editor_default_font.setBold(False)
        # editor_default_font.setFamily('Sans')
        # editor_default_font.setPixelSize(17)
                 
        editor_default_format = QtGui.QTextCharFormat()
        editor_default_format.setFont(editor_default_font)

        '''
        def remove_concat_empty_tags(self, html_source):
            # Удаляем пустые состыковывающиеся теги
            pos = 0
            while html_source.find('></', pos)>=0:
                pos = html_source.find('></', pos)
                pos11 = html_source.rfind('<', 0, pos)
                #if html_source[pos11+1]=='/':
                if html_source[pos11+1]==os.path.sep:
                    pos += 1
                    continue
                pos21 = pos + 3
                pos22 = html_source.find('>', pos21)
                print ('block1 '+str(pos11)+'-'+str(pos)+', block2 '+str(pos21)+'-'+str(pos22))
                print ('! : '+html_source[pos-10:pos+10] + ',  '+ html_source[pos11+1:pos] + ' ?? ' +
                html_source[pos21:pos22])
                if html_source[pos11+1:pos]==html_source[pos21:pos22]:
                    # Удаляем найденный тег с открытием и закрытием
                    html_source = html_source[:pos11]+html_source[pos22+1:]
                pos = pos22
    
            return html_source
        '''

        # FIXME: . набираемые и вставляемые текстом ссылки не подсвечиваются сразу-же


        def adaptate_alien_html_styles(self, html_source):
            # Адаптируем чужие стили html к стилям текущей темы span
            print('Получили для адаптации при вставке следующий html:\n' + html_source + '\n')
            max_size_of_html_source = len(html_source)
            # TODO: ... записать в преимущества функцию умного преобразования инородного html и вставки простого текста
            #  в свой html/wiki
            # TODO: ... сделать функцию иморта из любого html на основе преобразования инородного html в свой

            # Проверяем - не наш ли это собственный текст
            '<html><head><meta name="qrichtext"'
            "<!--StartFragment-->"
            "<!--EndFragment-->"

            # Удаляем все переносы строк \n
            html_source = html_source.replace('\n', '')
            html_source = html_source.replace('\r', '')
        
            # html_source = self.remove_concat_empty_tags(html_source)
                        
            need_insert_p_at_end = False  # Исправляем багу с <li> - чтобы текст после вставки не съезжал вправо

                    #  Удаляем все div, заменяем </div> на переносы строк
                    # <h1> - <h6> в заголовки
                    # italic и <i> в италик
                    # strhroughout (?) и  <s> в зачеркнутый
                    # картинки в картинку
                    # ссылки разбиваются на линк и текст рядом
                    # принимаем списки

            # Исправляем баги оформления
            # Бага от Kinozal - h2 обрамляет весь текст названия и параметров фильма. Удаляем его
            # если внутри <h?> есть переносы строк
            str1 = html_source[:4]
            str2 = html_source[-5:]
            between = html_source[4:-5]
            if ((str1 == '<h1>' and str2 == '</h1>') or (str1 == '<h2>' and str2 == '</h2>') or (str1 == '<h3>' and
                str2 == '</h3>') or (str1 == '<h4>' and str2 == '</h4>') or (str1 == '<h5>' and str2 == '</h5>') or
                    (str1 == '<h6>' and str2 == '</h6>')) and '<br>' in between:
                # print ('str1='+str1, 'str2='+str2, 'between='+between)
                print('Clear H wrong tag from paste html source')
                html_source = between
                
            # Удаляем все что связано с размером и цветом шрифта

            # Зачеркнутому, заголовкам, pre, ссылкам, подчернутому (mark) выставляем нужный стиль

            # Сначала корректируем стиль ссылок и переносим их "влево", удаляя окончания </a>
            if html_source.find('<a') >= 0:
                # print('\nКорректируем стиль ссылок')
                # html_source = re.sub('<a[^>]>([^<])</a>', self.editor_link_external_span_in_tag+'\\1</span>',
                # html_source)
                pos = 0

                # print('\n Оригинал с A, pos='+str(pos)+':\n'+html_source)
                html_source = html_source.replace('</a>', '')
                
                # html_source = re.sub('<a .*?href="(*.?)" .*?>', '<a '+self.editor_link_external_style+'
                # href="\\1">\\1</a>', html_source)
                while html_source.find('<a', pos) >= 0:
                    if pos>max_size_of_html_source:
                        print("желаемый pos превысил размер текста")
                        break
                    print("#1 pos=%s, html_source.find('<a', pos)=%s" % (pos, html_source.find('<a', pos)))

                    pos1 = html_source.find('<a', pos)
                    pos_href_1 = html_source.find('href=', pos1)
                    pos_href_1 = html_source.find('"', pos_href_1)
                    pos_href_2 = html_source.find('"', pos_href_1 + 1)
                    pos2 = html_source.find('>', pos_href_2)
                    href = html_source[pos_href_1 + 1:pos_href_2]
                    new_link = ' <a ' + self.editor_link_external_style + ' href="' + href + '">' + href + '</a> '
                    
                    html_source = html_source[:pos1] + new_link + html_source[pos2 + 1:]
                    pos = pos2 
                
                # print('\n С заменой A:\n'+html_source)

            # Картинки заменяем ссылками на них
            if html_source.find('<img') >= 0:
                pos = 0
                while html_source.find('<img', pos) >= 0:
                    if pos>max_size_of_html_source:
                        print("желаемый pos превысил размер текста")
                        break
                    print("#2 pos=%s, html_source.find('<img', pos)=%s" % (pos, html_source.find('<a', pos)))
                    pos1 = html_source.find('<img', pos)
                    pos2 = html_source.find('>', pos1)
                    pos_src_1 = html_source.find('src=', pos1)
                    pos_src_1 = html_source.find('"', pos_src_1)
                    pos_src_2 = html_source.find('"', pos_src_1 + 1)
                    
                    pos = pos1 
                    # print('\n Оригинал с IMG, pos='+str(pos)+':\n'+html_source)

                    href = html_source[pos_src_1 + 1:pos_src_2]
                    new_link = '<br><a ' + self.editor_link_external_style + ' href="' + href + '">' + href + '</a><br>'
 
                    html_source = html_source[:pos1] + ' ' + new_link + ' ' + html_source[pos2 + 1:]
                    # print('\n С заменой IMG:\n'+html_source)

            # Корректируем заголовки
            if html_source.find('<h') >= 0:
                # print('\nКорректируем стиль заголовков')
                # html_source = re.sub('<h1[.*?]>(.*?)</h1>', '<p>'+self.editor_h1_span+self.editor_h1
                # _span+'\\1</span></p>', html_source)
                h_begin = ['<h1', '<h2', '<h3', '<h4', '<h5', '<h6']
                h_end = ['</h1>', '</h2>', '</h3>', '</h4>', '</h5>', '</h6>']
                h_span = [self.editor_h1_span, self.editor_h2_span, self.editor_h3_span, self.editor_h4_span,
                          self.editor_h5_span, self.editor_h6_span]

                # print('\n Оригинал с H, pos='+str(pos)+':\n'+html_source)

                for i in range(0, 5):
                    pos = 0
                    while html_source.find(h_begin[i], pos) >= 0:
                        if pos > max_size_of_html_source:
                            print("желаемый pos превысил размер текста")
                            break
                        print("#3 pos=%s, html_source.find(h_begin[i], pos)=%s" % (pos, html_source.find(h_begin[i], pos)))

                        pos = html_source.find(h_begin[i], pos)
                        pos2 = html_source.find('>', pos)
                        html_source = html_source[:pos] + '<p>' + h_span[i] + html_source[pos2 + 1:]

                    # pos = 0
                    html_source = html_source.replace(h_end[i], '</span></p>')            
                # print('\n С заменой H:\n'+html_source)

            # Меняем стиль маркированному списку, удаляя <ul ..> и </ul>
            if html_source.find('<li') >= 0:
                html_source = re.sub('(<li.*?>)', self.editor_li_span, html_source)
                if html_source[-len('</ul>'):] == '</ul>':
                    need_insert_p_at_end = True
                
            # Добавляем в наш редактор, предварительно обернув в div стиля нашего шрифта по-умолчанию
            html_source = text_format.editor_default_font_span.replace('<span ', '<div ') + html_source + '</div>'
            if need_insert_p_at_end:
                html_source += '</p><p>'
            print('\nИтоговый результат:\n' + html_source + '\n')
            return html_source

        def switch_format_span(self, format_span, action):
            # Универсальная функция переключения или установки формата шрифта для выделенного фрагмента
            cursor = main_window.textBrowser_Note.textCursor()
            line_html = note.clear_selection_html_cover(cursor.selection().toHtml())
            text = cursor.selectedText()
            pos_cur = cursor.position()
            if pos_cur != cursor.selectionEnd():
                selection_begin = cursor.selectionEnd()
            else:
                selection_begin = cursor.selectionStart()
            # selection_end = cursor.selectionEnd()

            if format_span in line_html[:len(format_span) + 1]:                 
                # print('Форматирование уже стоит. Убираем  его..')
                # cursor.removeSelectedText()
                cursor.insertHtml(self.editor_default_font_span + text + '</span>')
                action.setChecked(False)
            else:
                # print('Форматирования нет или есть другое. Очищаем стиль выделение и ставим наш.')
                # cursor.removeSelectedText()
                cursor.insertHtml(format_span + text + '</span>')
                action.setChecked(True)
            # Восстанавливаем выделение пользователя
            cursor.setPosition(selection_begin)
            # cursor.setPosition(selection_end, QtGui.QTextCursor.KeepAnchor)
            cursor.setPosition(pos_cur, QtGui.QTextCursor.KeepAnchor)
            main_window.textBrowser_Note.setTextCursor(cursor)
            # cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            
            # FIXME: .. при выделении строки с начала сложным форматирование с тегом <li> возникают проблемы
        
        def update_ui_with_cursor_span(self, result=False):
            # Универсальная проверка наличия определенного стиля в курсоре и обновлении связанного
            # элемента интерфейса action
            # result содержит признак присутствия ранее в строке более высокоуровневого форматирования,
            # например, заголовков
            
            # FIXME: .. Если курсор до выделения - не отображается ни сложное форматирование, ни жирн/италик
            # FIXME: .. Нажатие на форматирование без выделения не сбрасывает оформление набираемого затем текста
            
            actions = [main_window.actionStrikethrough, main_window.actionCode, main_window.actionMark]
            format_spans = [self.editor_strikethrough_span, self.editor_code_span, self.editor_mark_span]
            
            if result:
                # i = 0  # Снимаем выделение со всех действий
                for i in range(0, len(actions)):
                    actions[i].setChecked(False)                
                return result            
            
            cursor = main_window.textBrowser_Note.textCursor()
            pos_cur = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            pos_begin_line = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            # full_line_html = note.clear_selection_html_cover( cursor.selection().toHtml() )
            pos_end_line = cursor.position()
            cursor.setPosition(pos_cur)  # Возвращаем курсор на место
                        
            if pos_begin_line == pos_end_line:
                # print('Позиция начала строки равна позиции конца: '+str(pos_begin_line))
                # i = 0  # Снимаем выделение со всех действий
                for i in range(0, len(actions)):
                    actions[i].setChecked(False)                
                return result
            
            if pos_cur > pos_begin_line:
                new_pos_cur = pos_cur - 1
            else:
                new_pos_cur = pos_begin_line + 1
                            
            cursor.setPosition(new_pos_cur, QtGui.QTextCursor.KeepAnchor)  # Делаем временное виртуальное выделение
            # if cursor.selection().isEmpty():
            #    print('Выбранный текст пустой')                
            #    return result
            
            line_html = note.clear_selection_html_cover(cursor.selection().toHtml())
            # print('Выделение '+str(pos_cur)+'-'+str(new_pos_cur) + ', строка '+str(pos_begin_line)+'-'+
            # str(pos_end_line))
            # print('Полная строка: '+full_line_html)
            # print('Выделение: '+line_html)
            
            # Перебираем все сложные форматы, в поиске присутствующего.
            # У остальных снимаем выделение с действия.
            
            # i = 0
            for i in range(0, len(actions)):
            
                if not result and format_spans[i] in line_html:                 
                    # print('Форматирование найдено: '+actions[i].text())
                    actions[i].setChecked(True)
                    result = True  # Устанавливаем признак найденного формата в строке
                else:
                    # print('Форматирования '+actions[i].text()+' нет')
                    actions[i].setChecked(False)
            
            cursor.setPosition(pos_cur)
            return result

        def switch_h_line(self, h): 
            editor_h_action = ['0-empty', main_window.actionHeading_1, main_window.actionHeading_2,
                               main_window.actionHeading_3, main_window.actionHeading_4, main_window.actionHeading_5,
                               main_window.actionHeading_6]
            
            cursor = main_window.textBrowser_Note.textCursor()
            pos_cur = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            cursor.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)
            line_html = note.clear_selection_html_cover(cursor.selection().toHtml())
                            
            if self.editor_h_span[h] in line_html:                 
                # print('Заголовок уже стоит. Убираем форматирование заголовка.')
                text = cursor.selectedText()
                # cursor.removeSelectedText()
                cursor.insertHtml(self.editor_default_font_span + text + '</span>')
                editor_h_action[h].setChecked(False)
            else:
                # print('Заголовка нет или есть другой. Удаляем форматирование и ставим новый.')
                text = cursor.selectedText()
                # cursor.removeSelectedText()
                cursor.insertHtml(self.editor_h_span[h] + text + '</span>')
                editor_h_action[h].setChecked(True)
            
            cursor.movePosition(pos_cur)

        def h1(self):
            self.switch_h_line(1)

        def h2(self):
            self.switch_h_line(2)

        def h3(self):
            self.switch_h_line(3)

        def h4(self):
            self.switch_h_line(4)

        def h5(self):
            self.switch_h_line(5)

        def h6(self):
            self.switch_h_line(6)

        def bold(self):
            cursor = main_window.textBrowser_Note.textCursor()
            pos_cur = cursor.position()
            if pos_cur == cursor.selectionStart():
                # Исправляем ситуацию, когда курсор, стоя в начале, не видит выделенного текста после него
                cursor.setPosition(pos_cur + 1, QtGui.QTextCursor.KeepAnchor)
                fmt = cursor.charFormat()
                cursor.setPosition(pos_cur, QtGui.QTextCursor.KeepAnchor)
            else:
                fmt = cursor.charFormat()
            
            if fmt.fontWeight() == 75:
                # print ('Bold already. Need clear bold.')
                fmt.setFontWeight(0)
            else:
                # print ('Need set bold.')
                fmt.setFontWeight(75)
                
            cursor.setCharFormat(fmt)  # Устанавливаем стиль "с нуля", удаляя предыдущий

        def italic(self):
            cursor = main_window.textBrowser_Note.textCursor()
            pos_cur = cursor.position()
            if pos_cur == cursor.selectionStart():
                # Исправляем ситуацию, когда курсор, стоя в начале, не видит выделенного текста после него
                cursor.setPosition(pos_cur + 1, QtGui.QTextCursor.KeepAnchor)
                fmt = cursor.charFormat()
                cursor.setPosition(pos_cur, QtGui.QTextCursor.KeepAnchor)
            else:
                fmt = cursor.charFormat()
                
            if fmt.fontItalic():
                fmt.setFontItalic(False)
            else:
                fmt.setFontItalic(True)
            cursor.setCharFormat(fmt)  # Устанавливаем стиль "с нуля", удаляя предыдущий

        def strikethrough(self):
            self.switch_format_span(self.editor_strikethrough_span, main_window.actionStrikethrough)            

        def code(self):
            self.switch_format_span(self.editor_code_span, main_window.actionCode)
        
        def mark(self):
            self.switch_format_span(self.editor_mark_span, main_window.actionMark)

        def clear_format(self):
            # Устанавливаем формат шрифта по-умолчанию
            # FIXME: как и другое форматирование - удаляет оформление ссылок
            cursor = main_window.textBrowser_Note.textCursor()
            cursor.setCharFormat(self.editor_default_format)

        def getLineAtPosition3(self, pos):
            # Моя собственная функция расчета количества строк до позиции
            
            # Показываем исходник выделенного текста, если надо
            self.getHtmlSourceOfSelectedPart()
            
            # Копируем курсор текстового редактора
            cursor = main_window.textBrowser_Note.textCursor()
            # Устанавливаем курсору указанное в параметрах положение
            cursor.setPosition(pos)
            #cur_pos = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            i = 1
            while not cursor.atStart():
                cursor.movePosition(QtGui.QTextCursor.Up)
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                # Если не перемещаться на начало линии - зависнет, не достигнув начала первой строки
                i += 1
            #cursor.setPosition(cur_pos)
            return i

        def getLineAtPosition(self, pos):
            cursor = main_window.textBrowser_Note.textCursor()
            cursor.setPosition(pos)
        
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            lines = 0
            
            lines_text = cursor.block().text().splitlines()
            lines_pos = 0
            for line_text in lines_text:
                lines_pos += len(line_text) + 1
                if lines_pos > cursor.position() - cursor.block().position():
                    break
                lines += 1
        
            block = cursor.block().previous()
            while block.isValid():
                lines += block.lineCount()
                block = block.previous()
        
            return lines            

        def getLineAtPosition2(self, pos):
            cursor = main_window.textBrowser_Note.textCursor()
            # cursor.setPosition(pos)
            # cursor.movePosition(0)
            cursor.setPosition(0)
            cursor.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
            # main_window.textBrowser_Note.setTextCursor(cursor);
            # tmp_string = cursor.selection().toHtml()
            html_source = cursor.selection().toHtml()
            
            # html_source = main_window.textBrowser_Note.toHtml()
            # html_source = re.sub('(/.*/gsm</head>)', '', html_source)
            html_source = re.sub('\n', '', html_source)
            # html_source = re.sub('.*<body.*?>', '', html_source, flags=re.MULTILINE|re.DOTALL)
            html_source = re.sub('.*<body.*?>', '', html_source)
            html_source = re.sub('(</body.*>)', '', html_source)
            html_source = re.sub('(<!--.*?-->)', '', html_source)
            html_source = re.sub('(<span.*?</span>)', '', html_source)
            # html_source = re.sub('(<p.*?>)', '', html_source)
            # html_source = re.sub('(<span.*?>)', '', html_source)
            # html_source = re.sub('(</span>)', '', html_source)
            # html_source = re.sub('(</p>)', '\n', html_source)
            # html_source = re.sub('(<br.*?>)', '\n', html_source)
            
            main_window.plainTextEdit_Note_Ntml_Source.setPlainText(html_source)
            # main_window.plainTextEdit_Note_Ntml_Source.textCursor().setPosition(pos)

        def getHtmlSourceOfSelectedPart(self):
            if main_window.actionShow_note_HTML_source.isChecked():
                cursor = main_window.textBrowser_Note.textCursor()
                # html_source = cursor.selection().toPlainText() + ' ### ' + cursor.selection().toHtml()
                html_source = cursor.selection().toHtml()
                NoteSelectedTextRegex = re.compile(r'.*?-->(.*)<!--.*?', re.DOTALL)
                NoteSelectedText = NoteSelectedTextRegex.search(html_source)
                if NoteSelectedText:
                    # html_source = html_source + ' ### ' + NoteSelectedText.group(1)
                    html_source = NoteSelectedText.group(1)
                # html_source = cursor.selection().toHtml()
                            
                # # html_source = main_window.textBrowser_Note.toHtml()
                # # html_source = re.sub('(/.*/gsm</head>)', '', html_source)
                # html_source = re.sub('\n', '', html_source)
                # # html_source = re.sub('.*<body.*?>', '', html_source, flags=re.MULTILINE|re.DOTALL)
                # html_source = re.sub('.*<body.*?>', '', html_source)
                # html_source = re.sub('(</body.*>)', '', html_source)
                # html_source = re.sub('(<!--.*?-->)', '', html_source)
                # html_source = re.sub('(<span.*?</span>)', '', html_source)
                # # html_source = re.sub('(<p.*?>)', '', html_source)
                # # html_source = re.sub('(<span.*?>)', '', html_source)
                # # html_source = re.sub('(</span>)', '', html_source)
                # # html_source = re.sub('(</p>)', '\n', html_source)
                # # html_source = re.sub('(<br.*?>)', '\n', html_source)
                
                main_window.plainTextEdit_Note_Ntml_Source.setPlainText(html_source)            


        def update_ui(self):
            # Обновляем интерфейс в соответствии с выделенным или написанным текстом
            
            cursor = main_window.textBrowser_Note.textCursor()
            
            # 'pos: '+str(cursor.position())
            # 'line2: '+str( self.getLineAtPosition2(cursor.position()) )+  \
            # 'line: '+str( self.getLineAtPosition(cursor.position()) )+  \
            
            #mess = 'line: ' + str(self.getLineAtPosition3(cursor.position())) + \
            #       '  column: ' + str(cursor.columnNumber())

            mess = 'line: %s  column: %s  pos: %s' % ( self.getLineAtPosition3(cursor.position()),
                                                     cursor.columnNumber(),
                                                     cursor.position(),
                                                     )

            # + \
            # ', block: '+str(cursor.blockNumber())+ \
            # ', sel.start: '+str(cursor.selectionStart())+', sel.end: '+str(cursor.selectionEnd())
            main_window.statusbar.showMessage(mess)
            
            # cursor =  QtGui.QTextCursor(main_window.doc_source)
            # cursor =  main_window.textBrowser_Note.textCursor()
            # cursor.movePosition(QtGui.QTextCursor.End)
            # tmp_string = cursor.selection().toHtml()
            # main_window.statusbar.showMessage(tmp_string.rpartition('StartFragment-->')[2])
            # main_window.plainTextEdit_Note_Ntml_Source.setPlainText(tmp_string.rpartition('StartFragment-->')[2])

            # Проверяем строку на наличие в ней заголовка
            complex_format_was_found = False  # Признак, чтобы в жирном заголовке ниже не искать жирный текст
            
            pos_cur = cursor.position()
            # print( 'Pos: '+str(cursor.position())+', sel.start: '+str(cursor.selectionStart())+', sel.end: '
            # +str(cursor.selectionEnd()) )
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            # pos_end = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)
            # pos_begin = cursor.position()
            # print('pos line: '+ str(pos_begin)+'-'+ str(pos_end) +', NEW selection: '+str(cursor.selectionStart())+
            # '-'+str(cursor.selectionEnd()) )
            line_html1 = cursor.selection().toHtml()
            line_html = note.clear_selection_html_cover(cursor.selection().toHtml())
            # print('line_html: '+line_html)
    
            if self.editor_h1_span in line_html:                 
                main_window.actionHeading_1.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_1.setChecked(False)
    
            if self.editor_h2_span in line_html:                 
                main_window.actionHeading_2.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_2.setChecked(False)
    
            if self.editor_h3_span in line_html:                 
                main_window.actionHeading_3.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_3.setChecked(False)
    
            if self.editor_h4_span in line_html:                 
                main_window.actionHeading_4.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_4.setChecked(False)
    
            if self.editor_h5_span in line_html:                 
                main_window.actionHeading_5.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_5.setChecked(False)
    
            if self.editor_h6_span in line_html:                 
                main_window.actionHeading_6.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_6.setChecked(False)
            
            # Особое форматирование, дополняющее обычный формат текста
            if self.editor_li_span in line_html:                 
                main_window.actionBullet_List.setChecked(True)
            else:
                main_window.actionBullet_List.setChecked(False)

            cursor.setPosition(pos_cur)

            # Определяем сложное оформление текста
            if self.update_ui_with_cursor_span(complex_format_was_found):
                complex_format_was_found = True

            if not complex_format_was_found:
                # Определяем простое форматирование текста                
                cursor = main_window.textBrowser_Note.textCursor()
                fmt = cursor.charFormat()
                
                if fmt.fontItalic():
                    main_window.actionItalic.setChecked(True)
                else:
                    main_window.actionItalic.setChecked(False)
                
                if fmt.fontWeight() == 75:
                    main_window.actionBold.setChecked(True)
                else:
                    main_window.actionBold.setChecked(False)
            else:
                main_window.actionBold.setChecked(False)
                main_window.actionItalic.setChecked(False)
                # print('базовое форматирование не проверяем, снимем его отметки')

        def __init__(self):
            pass
        



#class History ():

#    def add(self, type_, value):
#        pass
    
#    def set_active(self, filename):
#        pass
    
#    def setVisible(self, visible=True):
#        # Переключаем соотстветствующее отображению действие
#        # main_window.actionFast_jump_to_file_or_section.setChecked(visible)
#        pass


class Notelist():
    """ Все что определяет работу со списком заметок и историей:
    создание списков заметок и истории, фильтры для них, операции с заметками, UI
    
    *UI* (main_window):
    dockHistory, textBrowser_History
    frameNotelist_Filter, lineNotelist_Filter
    textBrowser_Listnotes
    sidebar_source    (исходник сайдбара)
    notelist_source    (исходник списка заметок)
    """
    filter_name = ''  # Фильтрация списка заметок по имени заметки
    filter_text = ''  # Фильтрация списка заметок по тексту, содержащемуся внутри заметок
    filter_is_empty = True  # Признак пустоты пользовательского фильтра, чтобы можно было отображать подсказку в самом текстовом поле
    filter_in_change = False # Признак того, что фильтр сейчас преднамеренно меняется в другом участке кода. Чтобы не было ложных срабатываний на внутренние изменения пустоты на подсказки и наоборот.
    filter_tip_for_using = 'Name␣Text' # &blank;

    filter_editing_tips = { 
                'empty' : '''Enter <span style="color: #008066;"><b>name</b></span>
                or press Space
                to enter text''',
 
                'name' : 'Enter <span style="color: #008066;"><b>name</b></span>',
                'text' : 'Enter <span style="color: #008066;"><b>any text</b></span> (space included)',
                'html_begin' : '<p style="font-size: 15px;">&nbsp;',
                'html_end' : '</p>',
                }

    # opened_url = None # Ссылка на открытую заметку

    allowed_note_files_extensions = ['.txt']

    items = []  # Элементы списка заметок
    
    items_cursor_position = 0  # Положение курсора в списке элементов, который можно открыть по нажатию Enter
    # move_cursor_direction = None # Признак того - куда надо передвинуть реальный курсор в QTextBrowser вслед за виртуальным
    items_cursor_url = None  # Ссылка под курсором, которая откроется при нажатии Enter
    items_cursor_cutename = None  # Красивое имя под курсором
    items_notes_size = 0  # Общий объём данных в заметках из списка
    items_notes_count = 0  # Количество отдельных заметок в списке элементов

    history_items = []   # Копия элементов только с типом "история"
    history_position = 0 # Некая переменная, которая была задумана для обозначения позиции в истории. Зачем - уже забыто. Но сохранена для будущего развития программы.

    # Информация обо всех подходящих под заметки файлах, найденных в процессе обхода, но, часть из которых может быть впоследствии может быть отфильтрована
    all_found_files_count = 0
    all_found_files_size = 0

    item = {}  # Перечень полей отдельного элемента
    item['filename'] = ''  # Путь к файлу заметки
    item['cutename'] = ''  # Красивое имя/путь заметки для отображения в списке
    item['history'] = False  # Элемент истории
    item['last_open'] = None  # Когда открывали последний раз. Больше относится к истории.
    item['size'] = None  # Размер файла заметки
    # Поля для найденного текста внутри заметки
    item['found_line_number'] = None  # Номер строчки, в которой найдено
    item['found_line_text'] = None  # Текст строчки, в которой найдено

    need_rescan = True  # Признак необходимости рескана списка заметок/файлов

    history_back_offset = 0  # Обратное смещение по списку истории

    note_contents_source = QtGui.QTextDocument()
    
    # file_recs = []

    timer_update = QtCore.QTimer()
    update_timeout = 350 # 420

    progress_count_files = 0  # Счетчик прогресса поиска файлов
    progress_count_items = 0  # Счетчик прогресса формирования элементов


    # class DB():
    #     """ Основной класс работы со списками заметок, историей их использования,кешем заметок
    #     notelist.db          Список заметок с признаками отслеживания активности работы с ними или их изменений.
    #     history.db           Полная история работы с заметками, позволяем составить точное мнение об
    #                          самых используемых заметках как за последний период, так и в целом.
    #                          Если заметка была удалена из списка, а затем создана (вставлена) вновь, то у неё
    #                          потеряется вся история предыдущей работы с ней. При переименовании и переносе такого
    #                          происходить не будет.
    #     note_txt_cache.db    Кэш для быстрого поиска по содержимому.
    #     note_html_cache.db   Кэш для быстрого открытия заметок.
    #
    #     notelist.db
    #         note_id
    #         filename            text
    #         size                integer
    #         modification_time   integer         # last_change
    #         access_time         integer         # last_open
    #
    #         cute_name           text
    #         parent_id           integer
    #         subnotes_count      integer
    #         subnotes_size       integer
    #         current_position    integer
    #
    #     history.db
    #         note_id
    #         changed     datetime
    #         opened      datetime
    #
    #     note_txt_cache.db
    #         filename
    #         txt_source
    #
    #     note_html_cache.db
    #         filename
    #         html_source
    #
    #     сравнить в скорости с объединенной базой кэша
    #     note_cache.db
    #         filename
    #         txt_source
    #         html_source
    #
    #     """
    #
    #     def purge_orphaned_cache(self):
    #         # Удаляем кэш файлов, которых уже нет. Например, были удалены или переименованы в другой программе.
    #         pass
    #
    #     def total_update_cache(self):
    #         # Полное обновление кэша, например, при первом запуске программы с уже имеющейся базой заметок
    #         pass
    #
    #     def save_note_cache_html(self, filename, html_source):
    #         pass
    #
    #     def save_note_cache_txt(self, filename, txt_source):
    #         pass
    #
    #     def get_note_cache_html(self, filename):
    #         # Получаем кэш заметки. Если его нет - возвращаем None.
    #
    #         return None
    #
    #     def get_note_cache_txt(self, filename):
    #         # Получаем кэш заметки. Если его нет - возвращаем None.
    #
    #         return None
    #
    #     #def initial_db(self):
    #
    #     #    # Дерево подразделов в файлах заметок
    #
    #     #    # Списки меток в файлах заметок
    #
    #     #    # Списки задач в файлах заметок
    #
    #
    #     def __init__(self):   # class DB
    #         pass


    def move_textbrowser_cursor(self):
        # Двигаем курсор в списке заметок вслед за перемещением виртуального курсора, чтобы он всегда был в поле видимости
        # cursor = main_window.textBrowser_Listnotes.textCursor()
        # print('self.move_cursor_direction=%s' % self.move_cursor_direction)
        # if self.move_cursor_direction == 'up':
        #    cursor.movePosition(QtGui.QTextCursor.Up)
        # if self.move_cursor_direction == 'down':
        #    cursor.movePosition(QtGui.QTextCursor.Down)
        # if self.move_cursor_direction == 'end':
        #    cursor.movePosition(QtGui.QTextCursor.End)
        # if self.move_cursor_direction == 'start':
        #    cursor.movePosition(QtGui.QTextCursor.Start)
        # main_window.textBrowser_Listnotes.ensureCursorVisible()
        # self.move_cursor_direction = None

        # Если нет элементов в списке - выходим
        if len(self.items) < 1:
            return 0

        main_window.adjust_scrollbar_position_at_editor(main_window.textBrowser_Listnotes, self.items_cursor_position, len(self.items))

        #scrollbar_maximum = main_window.textBrowser_Listnotes.verticalScrollBar().maximum()
        #percent_of_position = self.items_cursor_position / len(self.items)
        #scrollbar_set_pos = scrollbar_maximum * percent_of_position
        #listnotes_height = main_window.textBrowser_Listnotes.height()
        ## print('scrollbar_maximum=%s, percent_of_position=%s, scrollbar_set_pos=%s, listnotes_height=%s' % (scrollbar_maximum, percent_of_position,scrollbar_set_pos, listnotes_height) )

        #if scrollbar_set_pos < listnotes_height * 0.8:
        #    scrollbar_set_pos = 0
        #if scrollbar_set_pos > scrollbar_maximum - listnotes_height / 2:
        #    scrollbar_set_pos = scrollbar_maximum
        #main_window.textBrowser_Listnotes.verticalScrollBar().setValue(scrollbar_set_pos)



    def search_param_message(self):
        # Получаем сообщение для верха списка заметок о текущих фильтрах для него
        notelist_search_param_string = '<div id=notelist_search_param_message>%s</div>'
        notelist_search_param_message = ''

        if self.filter_name:
            description_filter_name = ('  Show notes with a name containing <b>"%s"</b>' % self.filter_name)
        else:
            description_filter_name = '  Show notes with any name'
        if self.filter_text:
            description_filter_text = ('containing the text <b>"%s"</b>' % self.filter_text.replace(' ', '&nbsp;'))
        else:
            description_filter_text = 'containing any text'

        if main_window.current_open_note_link:
            cute_filename = self.make_cute_name(main_window.current_open_note_link)
            return_info = ' &nbsp; <small>Press <b>Esc</b> to return to <span style="color: #008066;">%s</span></small>' % cute_filename
            # <span style="color: #008066;">
        else:
            return_info = ''

        notelist_search_param_message_text = description_filter_name + ' and ' + description_filter_text + return_info
        #if not self.filter_name and not self.filter_text:
        #    # Фильтры не установлены. Минимальная строка.
        #    # Надо добавить к ней пробелов
        #    notelist_search_param_message_text += ' &nbsp;'*20 + '.'
        return notelist_search_param_string % notelist_search_param_message_text


    def html_body(self, empty_message='', html_source=''):
        # Основной шаблон списка заметок
            return '''<html>
                      <body id=notelist_body>
                      %s
                      <span style="font-size: 6px;"> </span>%s
                      %s
                      <div id=notelist>%s</div>
                      </body>
                      </html>''' % (Theme.html_theme_head,
                                    self.search_param_message(),
                                    empty_message,
                                    html_source,)


    def search_progress_indicator_init(self):
        # Будем показывать индикатор прямо в списке заметок
        #html_source = self.html_body() # html_source=html_source
        #main_window.notelist_source.setHtml(html_source)
        #main_window.textBrowser_Listnotes.setDocument(main_window.notelist_source)
        #main_window.textBrowser_Listnotes.moveCursor(QtGui.QTextCursor.Start)
        #main_window.textBrowser_Listnotes.ensureCursorVisible()
        #main_window.textBrowser_Listnotes.clear()
        #main_window.textBrowser_Listnotes.append(self.search_param_message())

        #main_window.lbSearchParam.setMinimumWidth(400)
        main_window.lbSearchParam.setText(self.search_param_message())
        #main_window.lbSearchParam.resize()

        #main_window.lbSearchParam.setStyleSheet('''
        #                        font-size: 12px;
        #                        '''
        #                        )
        main_window.lbSearchFiles.setText('Файлов в обработке: ')
        main_window.lbSearchItems.setText('Элементов найдено: ')
        main_window.lbFormatItems.setText('Элементов оформлено: ')
        
        #main_window.lbSearchFilesProgress.setMinimumWidth(40)
        #main_window.lbSearchItemsProgress.setMinimumWidth(50)
        #main_window.lbFormatItemsProgress.setMinimumWidth(50)

        main_window.progressBar_Notelist.setMaximum(0)
        self.progress_count_files = 0
        self.progress_count_items = 0
        main_window.lbSearchFilesProgress.setText('0')
        main_window.lbSearchItemsProgress.setText('0')
        main_window.lbFormatItemsProgress.setText('0')

        main_window.Search_Progressbar_Panel.show()
        ##main_window.Search_Progressbar_Panel.resize()
        #main_window.Search_Progressbar_Panel.update()
        #main_window.Search_Progressbar_Panel.repaint()
        
        #main_window.textBrowser_Listnotes.update()
        #main_window.update()

    def search_progress_indicator_add(self, files=False, items=False, add=1):
        if files:
            self.progress_count_files += add
            main_window.lbSearchFilesProgress.setText(str(self.progress_count_files))
            ##main_window.lbSearchFilesProgress.update()
            #main_window.lbSearchFilesProgress.repaint()
        if items:
            self.progress_count_items += add
            if not main_window.progressBar_Notelist.maximum():
                main_window.progressBar_Notelist.setMaximum(len(self.items))
            else:
                main_window.progressBar_Notelist.setValue(self.progress_count_items)
            main_window.lbFormatItemsProgress.setText(str(self.progress_count_items))
         
            #main_window.progressBar_Notelist.repaint()
            ##main_window.progressBar_Notelist.ensurePolished()
            ##main_window.progressBar_Notelist.update()

            ##main_window.lbFormatItemsProgress.update()
            #main_window.lbFormatItemsProgress.repaint()
            ##main_window.lbFormatItemsProgress.ensurePolished()
            ##main_window.lbFormatItemsProgress.update()


        main_window.lbSearchItemsProgress.setText(str(len(self.items)))
        #main_window.lbSearchItemsProgress.update()
        #main_window.lbSearchItemsProgress.repaint()

        ##main_window.Search_Progressbar_Panel.resize()
        #main_window.Search_Progressbar_Panel.update()
        #main_window.Search_Progressbar_Panel.repaint()
        
        ##main_window.lbSearchItems.setText('Элементов найдено: ')
        #print('progress: files %s, found %s, items %s' % ( self.progress_count_files, 
        #                 len(self.items),
        #                 self.progress_count_items, )
        #      )
        
        #main_window.textBrowser_Listnotes.repaint()
        #main_window.textBrowser_Listnotes.update()
        #main_window.repaint()
        #main_window.update()
    
    def search_progress_indicator_hide(self):
        main_window.Search_Progressbar_Panel.hide()
        #pass


    def set_visible(self, visible=True):
        # Переключение видимости всего что связано со списком заметок
        if visible:
            # Отображаем все виджеты, связанные Notelist
            main_window.stackedWidget.setCurrentIndex(0)
            # Скрываем конкурирующие виджеты
            note.set_visible(False)
            table_of_note_contents.setVisible(False)
            # notelist.setVisible(False)
            
        # Переключаем все действия, связанные со списком заметок
        # note_actions = [ main_window.actionNote_multiaction, main_window.actionShow_note_contents ]
        # for action in note_actions:
        #    action.setEnabled(visible)
        # Переключаем соотстветствующее отображению действие
        main_window.actionFast_jump_to_file_or_section.setChecked(visible)

        # Пробный код вставки виджета в панель кнопок
        # comboStyle = QtWidgets.QComboBox(main_window.toolBar)
        # main_window.toolBar.addWidget(comboStyle)
        # comboStyle.addItem("Standard")
        # comboStyle.addItem("Bullet List (Disc)")


    def is_visible(self):
        if main_window.stackedWidget.currentIndex() == 0:
            return True
        else:
            return False

    def action_triggered(self):
        if self.is_visible():
            # Список заметок сейчас отображается.
            # Надо переключиться на предыдущий вид
            pass
        else:
            # Показываем список заметок
            self.set_visible()
            # Обновляем список на случай появления новых файлов и для подсветки текущего
            self.update(history_update=True)
            # Устанавливаем фокус на поля фильтров ввода
            # При любом раскладе выделяем весь текст в поле имени и ставим на него фокус            
            main_window.lineNotelist_Filter.setFocus()
            if not notelist.filter_is_empty:
                main_window.lineNotelist_Filter.selectAll()
            
            # # Если обнаружен текст в поле поиска по содержимому - переставляем фокус в него
            # if main_window.lineEdit_Filter_Note_Text.text() != '':
            #    main_window.lineEdit_Filter_Note_Text.setFocus()
            #    main_window.lineEdit_Filter_Note_Text.selectAll()

    def update(self, history_update=False):
        # Обновляем список заметок
        self.rescan_files_in_notes_path(history_update)

    def cancel_scheduled_update(self):
        # Отменяем отложенное обновление списка элементов
        #print('notelist.timer_update STOP.')
        self.timer_update.stop()

    def schedule_update(self):
        # Запланировать обновление списка элементов с заданным в настройках таймаутов (через какую-то долю секунды)

        #if self.timer_update.isActive():
        #    print('notelist.timer_update уже активен. Останавливаем и запускаем его снова.')
        #    self.timer_update.stop()
        #else:
        #print('notelist.timer_update start')
        self.items_cursor_position = 0
        self.need_rescan = True
        self.timer_update.start(notelist.update_timeout)


    def move_cursor(self, delta=0):
        # print('Перемещаем курсор по списку с дельтой %s' % delta)
        # Перемещаем курсор по списку заметок в заданном направлении
        new_position = self.items_cursor_position + delta
        if new_position < 1:
            # Уперлись в пол. Надо мотать в конец.
            new_position = len(self.items) + new_position
            # self.move_cursor_direction = 'end'
        elif new_position > len(self.items):
            # Уперлись в потолок. Надо мотать в начало.
            new_position = new_position - len(self.items)
            # self.move_cursor_direction = 'start'
        # elif delta>0:
        #    self.move_cursor_direction = 'up'
        # elif delta<0:
        #    self.move_cursor_direction = 'down'
        self.items_cursor_position = new_position
        self.update()


    def extract_filters(self, notelist_filter):
        # Функция извлечения фильтра для имени и фильтра для текста из единой строки

        # Делим фильтр заметок на фильтр имени и фильтр текста внутри
        if ' ' not in notelist_filter:
            # Если и есть фильтр - он только по имени
            extracted_filter_text = ''
            extracted_filter_name = notelist_filter
        else:
            # У нас указан фильтр по тексту. Может ещё и по имени.
            # Первое слово до пробела - имя. Остальные - текст.
            filter_words = notelist_filter.split(' ')
            extracted_filter_name = filter_words[0]
            extracted_filter_text = ' '.join(filter_words[1:])
        return extracted_filter_name, extracted_filter_text



    def get_and_display_filters(self):
        # Получаем текущий фильтр для списка заметок

        ## Проверяем - не внутреннее ли это программное изменение текста фильтра на подсказку или наоборот.
        #if self.filter_in_change:
        #    return 0
        
        if self.filter_is_empty:
            # Если стоит признак пустого фильтра - указываем это в анализируемой переменной
            notelist_filter = ''
        else:
            # Иначе берем фильтр из поля в UI
            notelist_filter = main_window.lineNotelist_Filter.text()
        
        self.filter_name, self.filter_text = self.extract_filters(notelist_filter)

        ## Проверяем на пустоту поля фильтра
        #if not notelist_filter:
        #    # У нас совсем пустой фильтр. Надо указать что он пуст и показать подсказку
        #    self.filter_is_empty = True
        #    self.filter_in_change = True
        #    main_window.lineNotelist_Filter.setText(self.filter_tip_for_using)
        #    main_window.lineNotelist_Filter.setStyleSheet('''
        #                        color: #aaa;
        #                        font-size: 14px;
        #                        background: white;
        #                        '''
        #                        )
        #    self.filter_in_change = False
        #    return 0

        #if self.filter_is_empty:
        #    # Возможно, текст был изменен в пустом фильтре с подсказкой
        #    if notelist_filter == self.filter_tip_for_using:
        #        # Текст подсказки по-умолчанию остался без изменений. Выходим
        #        return 0
        #    else:
        #        # Текст в фильтре не соответствует подсказке. Меняем фильтр и стиль оформления поля ввода
        #        self.filter_is_empty = False
        #        self.filter_in_change = True
        #        main_window.lineNotelist_Filter.setText(self.filter_tip_for_using)
        #        main_window.lineNotelist_Filter.setStyleSheet('''
        #                            color: #1a1a1a;
        #                            font-size: 16px;
        #                            background: #fff8a5;
        #                            '''
        #                            )
        #        self.filter_in_change = False


        ## Делим фильтр заметок на фильтр имени и фильтр текста внутри
        #if ' ' not in notelist_filter:
        #    # Если и есть фильтр - он только по имени
        #    self.filter_text = ''
        #    self.filter_name = notelist_filter
        #else:
        #    # У нас указан фильтр по тексту. Может ещё и по имени.
        #    # Первое слово до пробела - имя. Остальные - текст.
        #    filter_words = notelist_filter.split(' ')
        #    self.filter_name = filter_words[0]
        #    self.filter_text = ' '.join(filter_words[1:])
        
        #if self.filter_text or self.filter_name:
        #    # Отображаем в интерфейсе полученные указания по фильтрам
        #    if self.filter_name:
        #        description_filter_name = ('Name contains <b>"%s"</b>' % self.filter_name)
        #    else:
        #        description_filter_name = 'Any name'
        #    if self.filter_text:
        #        description_filter_text = ('text contains <b>"%s"</b>' % self.filter_text.replace(' ', '&nbsp;'))
        #    else:
        #        description_filter_text = 'any text contains'

        #    main_window.label_DisplayFilters.setText(description_filter_name + ' and ' + description_filter_text)
        #else:
        #    # main_window.label_DisplayFilters.setText('Example: "proj ninja"')
        #    main_window.label_DisplayFilters.setText('<html><head></head><body>Example: <b>proj ninja</b></body></html>')
                
        # print('Filters: notelist.filter_name=%s, notelist.filter_text=%s' % (self.filter_name, self.filter_text) )



    def make_cute_name(self, filename):
        # Создаем симпатичное длинное имя заметки из имени файла
        # 1. Убираем из пути каталог до заметок
        cute_filename = filename.replace(app_settings.path_to_notes + os.path.sep, '')
        # 2. Убираем расширение файла
        # 2.1 Разрезаем на отдельные слова - папки и имя файла
        list_of_words = cute_filename.split(os.path.sep)
        # 2.2 В последнем слове отрезаем все после точки, если она есть
        if '.' in list_of_words[-1]:
            list_of_words[-1] = list_of_words[-1].rpartition('.')[0]
        # cute_filename = cute_filename.rpartition('.txt')[0]
        # 3. Соединяем обратно, вместо разделителя пути используя двоеточие с пробелом после
        cute_filename = ': '.join(list_of_words)
        # cute_filename = cute_filename.replace(os.path.sep, ': ')         
        # 4. Меняем нижнее подчеркивание на пробелы
        cute_filename = cute_filename.replace('_', ' ')            
        return cute_filename


    def file_in_history(self, filename):
        # Проверяем - есть ли файл в списке истории
        app_settings.state_db_connection.execute("SELECT * FROM file_recs WHERE filename=? AND last_open NOT NULL", (filename,))
        existed_rec = app_settings.state_db_connection.fetchall()
        if len(existed_rec) > 0:
            # print('Файл обнаружен в истории: ', filename)
            return True
        else:
            return False

    def file_in_state_db(self, filename):
        # Проверяем - есть ли файл в списке истории
        app_settings.state_db_connection.execute("SELECT * FROM file_recs WHERE filename=?", (filename,))
        existed_rec = app_settings.state_db_connection.fetchall()
        if len(existed_rec) > 0:
            # print('Файл обнаружен в базе: ', filename)
            return True
        else:
            return False


    def cute_filename_is_allowed(self, cute_filename):
        # Проверяем - проходит ли установленный фильтр имени текущее симпатичное имя заметки
        return (self.filter_name != '' and self.filter_name.lower() not in cute_filename.lower())


    def add_item(self,
                 filename=None,
                 cutename=None,
                 history=False,
                 last_open=None,
                 size=None,
                 found_line_number=None,
                 found_line_text=None
                 ):
        # Добавляем элемент списка
        rec_item = self.item.copy()  # Делаем копию образца словаря
        rec_item['filename'] = filename
        rec_item['cutename'] = cutename
        rec_item['history'] = history
        rec_item['last_open'] = last_open
        rec_item['size'] = size

        rec_item['found_line_number'] = found_line_number
        rec_item['found_line_text'] = found_line_text

        if size:
            # Добавляем в общий размер
            self.items_notes_size += size
        
        # Добавляем элемент во внутренний список элементов
        self.items.append(rec_item)
        if history:
            # Добавляем и в отдельный список для истории, если это она
            # Переводим дату из строки в datetime
            rec_item_copy = rec_item.copy()
            if rec_item['last_open']:
                # Если запись последнего открытия не пустая
                rec_item_copy['last_open']= datetime.strptime(rec_item['last_open'], '%Y-%m-%d %H:%M:%S.%f')
            self.history_items.append(rec_item_copy)
        
    def delete_item(self, item_filename=None, items_array=[]):
        # Удаляем элемент списка из указанного массива (это может быть и не items)

        item_number = 0
        item_was_found = False # Признак того, что элемент в итоге нашли

        for one_item in items_array:
            
            if one_item['filename'] == item_filename:
                # Нашли нужный item
                item_was_found = True
            else:
                item_number += 1
        if item_was_found:
            # Удаляем из указанного списка элемент с указанным номером
            items_array.pop(item_number)
            print('Из массива элементов был удален %s' % item_filename)
        else:
            print('При поиске в элементах %s для удаления, этого элемента найти не удалось!' % item_filename)

    
    def clear_items(self):
        # Очищаем данные об элементах 
        
        # Общие данные обо всех файлах заметок
        self.all_found_files_count = 0
        self.all_found_files_size = 0
        
        # Данные об отображенных (отфильтрованных) заметках
        self.items = []
        self.items_notes_size = 0
        self.items_notes_count = 0
        
        # Копия данных об истории
        self.history_items = []

        # Данные о курсоре
        # self.items_cursor_url = None
        # self.items_cursor_position = 0



    def work_with_found_note(self, filename, history=False, size=None, last_open=None):
        # Определяем - надо ли добавлять заметку в список.
        # Надо ли искать в ней текст.
        # И удовлетворяет ли она всем установленным фильтрам.
        # Затем добавляем все необходимое в список и меняем соответствующие переменные.

        # print('Работаем с файлом %s' % filename)
        # if self.file_in_history(filename):
            # print('Файл из истории: %s' % filename)

        cutename = self.make_cute_name(filename)
        
        # Если не подходит под фильтр имени - выходим
        if self.cute_filename_is_allowed(cutename):
            return 0

        lines = ''

        # Проверяем на неудовлетворение фильтру по тексту содержимого заметки
        # if main_window.lineEdit_Filter_Note_Text.text() != '':
        if self.filter_text != '':
            # Надо загрузить заметку и провести поиск в ней на предмет содержимого
            fileObj = codecs.open(filename, "r", "utf-8")
            lines = fileObj.read()
            fileObj.close()
            # if main_window.lineEdit_Filter_Note_Text.text().lower() not in lines.lower():
            if self.filter_text.lower() not in lines.lower():
                # Если искомого текста в заметке нет - просто идем к следующей
                # print('Файл %s не подходит под фильтр текста "%s"' % (cute_filename.lower(), self.filter_text.lower()) )
                return 0

        self.add_item(filename=filename,
                      cutename=cutename,
                      history=history,
                      last_open=last_open,
                      size=size)

        # Увеличиваем счетчик количества заметок в списке
        self.items_notes_count += 1

        # Если надо, добавляем ссылки на позиции вхождения текста в заметке
        if self.filter_text != '':
            filter_note_text = self.filter_text
            founded_i = 0
            # print('Ищем текст "'+filter_note_text+'" в строчках внутри заметки')
            line_i = 1
            for line in lines.split('\n'):
                pos = line.lower().find(filter_note_text.lower())
                if pos >= 0:
                    # print('Нашли вхождение в строку '+str(line_i)+' - '+filter_note_text)
                    # Нашли вхождение. Подсвечиваем и добавляем к выводу в Notelist

                    self.add_item(filename=filename,
                                  history=history,
                                  found_line_number=line_i,
                                  found_line_text=line)

                    founded_i += 1

                line_i += 1

        
        
        


    def collect_history_items_list(self, update_items_list=True):
        # Собираем элементы (заметки) из истории при рескане файлов в переменную self.items[]

        file_recs_rows = app_settings.state_db_connection.execute("SELECT * FROM file_recs WHERE last_open NOT NULL ORDER BY last_open DESC")

        for row in file_recs_rows:
            rec_filename, rec_cute_name, rec_parent_id, rec_subnotes_count, rec_last_change, rec_last_open, rec_count_opens, rec_current_position = row
            self.search_progress_indicator_add(files=True)
            # Проверка файла из истории на существование 
            if not os.path.isfile(rec_filename):
                # Файл не существует или это каталог, а не файл.
                # Удаляем из истории
                app_settings.state_db_connection.execute("DELETE FROM file_recs WHERE filename=?", (rec_filename,))
                continue  # Переходим на следующий виток цикла

            self.work_with_found_note(filename=rec_filename,
                                      history=True,
                                      size=os.stat(rec_filename).st_size,
                                      last_open=rec_last_open)


    def collect_other_items_list(self):
        # Собираем новые элементы (заметки) при рескане файлов (которых не было в истории)

        # Как собирать список файлов:
        # http://stackoverflow.com/questions/1274506/how-can-i-create-a-list-of-files-in-the-current-directory-and-its-
        # subdirectories
        # http://stackoverflow.com/questions/2225564/get-a-filtered-list-of-files-in-a-directory

        for root, dirs, files in os.walk(app_settings.path_to_notes):
            for file in files:
                self.search_progress_indicator_add(files=True)
                # print('Найдено во время обхода: %s' % os.path.join(root, file))
                # Проверяем - разрешенное ли расширение у файла
                if os.path.splitext(file)[-1] in self.allowed_note_files_extensions:
                # if file.endswith('.txt'):
                    # Обрабатываем файл заметки
                    filename = os.path.join(root, file)
                    size = os.stat(filename).st_size
                    # access_time = os.stat(filename).st_atime  # time of most recent access.
                    # modification_time = os.stat(filename).st_mtime  # time of most recent content modification

                    # Добавляем инфу о найденных файлах в общий счетчик всех доступных файлов заметок
                    self.all_found_files_count += 1
                    self.all_found_files_size += size
                    # print('Файл с разрешенным расширением')

                    # Продолжаем с найденным файловым элементом
                    # Проверяем - нет ли этого элемента уже добавленного из истории
                    if self.file_in_history(filename):
                        # print('Файл есть в истории: %s' % filename)
                        continue  # Переходим на следующий виток цикла

                    self.work_with_found_note(filename=filename,
                                              size=size)


    def update_history_items_with_one(self, filename):
        # Быстрое обновление отдельного списка истории заметок для случая открытия указанного файла
        for one_item in self.history_items:
            if one_item['filename'] == filename:
                #print('Элемент найден в старой истории')
                return 0
        history_items_copy = []
        for one_item in self.items:
            if one_item['filename'] == filename:
                #print('Элемент будет добавлен в новую историю')
                #print('Старая история %s' % self.history_items)
                # Нашли элемент, который надо добавить в начало списка истории
                one_item_copy = one_item
                one_item_copy['history'] = True
                one_item_copy['last_open'] = datetime.now()
                history_items_copy.append(one_item_copy)

                # Добавляем в новый список все остальные элементы
                for one_history_item in self.history_items:
                    history_items_copy.append(one_history_item.copy())
                # Заменяем старый список на новый
                self.history_items = history_items_copy.copy()
                #print('Новая история %s' % self.history_items)
                return 0


    def update_items_list_with_history_status(self):
        # Обновляем список элементов после изменении истории

        # 0. Запомнить - на какой заметке (по имени файла) должен быть курсор
        if notelist.items_cursor_position > 0:
            cursor_filename = notelist.items[notelist.items_cursor_position-1]['filename']
        else:
            cursor_filename = ''
        print('cursor_filename %s' % cursor_filename)

        # 1. Копировать айтемы в отдельный список
        items_copy = self.items.copy()

        # Копируем статистику (изменилась история, а не реально найденные элементы)
        all_found_files_count_copy = self.all_found_files_count
        all_found_files_size_copy = self.all_found_files_size
        items_notes_size_copy = self.items_notes_size
        items_notes_count_copy = self.items_notes_count

        # Очистить список элементов notelist
        self.clear_items()
        # А что будет с общей статистикой?

        # 2. collect_history_items
        self.collect_history_items_list()

        # Собираем массив имен файлов из текущей истории
        new_history_items = []
        for one_item in self.items:
            new_history_items.append(one_item['filename'])

        # Проходим по старым айтемам и те, что не история или не в новой истории - добавляем к новому массиву
        #print('Добавляем элементы, которые не были и не есть в истории')
        for one_item in items_copy:
            if not one_item['filename'] in new_history_items:
                # Нету в новой истории
                one_item['history'] = False # Даже если был в истории - теперь он обычный элемент
                self.items.append(one_item.copy())

        #print('Удаляем новую историю из старых айтемов')
        ## 3. пройтись по айтемам из истории и выкинуть их из копии
        #for one_item in self.items:
        #    # В элементах только история
        #    self.delete_item(one_item['filename'], items_copy)

        #print('Удаляем остатки старой истории из старых айтемов')
        ## Выкинуть всю историю из копии
        #for one_item in items_copy:
        #    if one_item['history']:
        #        self.delete_item(one_item['filename'], items_copy)


        ## 4. добавить айтемы файлов к айтемам истории
        #for one_item in items_copy:
        #    self.items.append(one_item)


        # 5. найти положение заметки, у которой стоял курсор, и обновить положение курсора в классе
        new_cursor_position = 1  # Да, позиция тут начинается с единицы
        for one_item in self.items:
            if one_item['filename'] == cursor_filename:
                # Нашли новое положение курсора
                self.items_cursor_position = new_cursor_position
            else:
                new_cursor_position += 1
        #print('cursor_filename: %s, position: %s' % (cursor_filename, self.items_cursor_position))
        #print('items: %s' % self.items)

        # 6. Обновить информацию об общей статистике найденного и отображенных элементов в Notelist
        # Восстанавливаем статистику
        self.all_found_files_count = all_found_files_count_copy
        self.all_found_files_size = all_found_files_size_copy
        self.items_notes_size = items_notes_size_copy
        self.items_notes_count = items_notes_count_copy



    def highlight_found_text_in_html_source(self, item_source, highlight_text):
        # Выполняем замену подстроки html кода элемента для подсветки найденного текста
        insensitive_text = re.compile('(' + re.escape(highlight_text) + ')', re.IGNORECASE)
        return insensitive_text.sub('<span id="highlight">\\1</span>', item_source)

    
    action_link_items_separator = '?'

    def action_link(self, action_type, filename=None, line_number=None, found_text=None):
        # Формируем ссылку действий (внутренний линк) для использования в списке заметок
        link_string = action_type
        if filename:
            link_string += self.action_link_items_separator + filename
            if line_number:
                link_string += self.action_link_items_separator + str(line_number)
        return link_string

    def action_link_items(self, link):
        # Извлекаем элементы ссылки действий
        return link.split(self.action_link_items_separator)


    def make_html_source_for_item_cursor(self, item_number, one_item, filename, active_link):
        # Проверяем- активный ли элемент в списке. 
        # Если да - добавляем курсор. Если нет - оформляем без выделения, как обычно.
        img_src = ''

        # Устанавливаем картинку - заметка с курсором, или без него
        if self.items_cursor_position == item_number:
            # Текущая позиция - должна быть с курсором
            img_src = 'resources/icons/notelist/arrow130_h11.png'
            self.items_cursor_url = 'note?' + filename
            # Проверяем наличие указания номера строки с найденным текстом
            if one_item['found_line_number']:
                # Это найденный текст внутри заметки
                line = one_item['found_line_text']
                line_i = one_item['found_line_number']
                # Добавляем позицию с найденным текстом
                self.items_cursor_url += '?' + str(line_i)

            self.items_cursor_cutename = self.make_cute_name(filename)
        else:
            # Позиция без курсора.
            # Проверяем - какую иконку отображать для типа элемента

            # Проверяем - элемент заметка или найденный текст в ней
            if one_item['found_line_number']:
                # Это найденный текст внутри заметки. Никакую картинку не указываем
                pass
            else:
                # Это обычная заметка. Делаем ей иконку.
                if filename == active_link:
                    img_src = 'resources/icons/notelist/g3-g1.png'
                else:
                    img_src = 'resources/icons/notelist/g3.png'

        if img_src:
            # Есть иконка. Делаем для неё обертку.
            item_cursor_source = '<img src="%s"> ' % img_src # &nbsp;
        else:
            # Иконки нет. Ставим в исходник просто пробелы
            item_cursor_source = '   '
        return item_cursor_source


    def make_html_source_for_item_history_sidebar(self, one_item, item_number, active_link):
        # Создаем html для элемента истории в сайдбаре
        html_string = ''
        filename = one_item['filename']
        cute_name = self.make_cute_name(filename)
        note_link = self.action_link('note', filename)
        if filename == active_link:
            line_style = ' id="note_opened" '
            # img_src = 'resources/icons/notelist/g3-g1.png'
        else:
            # img_src = 'resources/icons/notelist/g3.png'
            line_style = ''

        html_string += '<p' + line_style + '><a href="' + note_link + '" title="'\
                        + cute_name + '">' + cute_name + '</a></p>'

        return html_string



    def make_html_source_for_item(self, one_item, item_number):
        # Создаем оформление и html-форматирование для представления одного элемента из списка в общем исходнике html
        html_source = ''
        # Готовим переменные, которые понадобятся в любом случае
        filename = one_item['filename']
        cute_filename = self.make_cute_name(filename)
        active_link = main_window.current_open_note_link
        last_open = ''  # Признак элемента из истории

        item_cursor_source = self.make_html_source_for_item_cursor(item_number, one_item, filename, active_link)

        if one_item['found_line_number']:
            # Это найденный текст внутри заметки
            line = one_item['found_line_text']
            line_i = one_item['found_line_number']

            note_link = self.action_link('note', filename, line_i)

            # line = re.sub('(' + self.filter_text + ')', '<span id="highlight">' + '\\1</span>', line, flags=re.I)
            #line = line.replace(self.filter_text, '<span id="highlight">' + self.filter_text + '</span>')
            line = self.highlight_found_text_in_html_source(line, self.filter_text)
                # &nbsp;&nbsp;&nbsp;

            #html_source += '<p id=founded_text_in_note>' + item_cursor_source + \
            #    '   <small>' + str(line_i) + ':</small>&nbsp;&nbsp;<a href="note?' + filename + '?' + str(line_i) + '">' + line + '</a></p>'

            html_source += '<p id=founded_text_in_note>' + item_cursor_source + \
                '   <small>' + str(line_i) + ':</small>&nbsp;&nbsp;<a href="' + note_link + '">' + line + '</a></p>'

            return html_source


        if one_item['history']:
            # Это элемент истории. Заполняем признак last_open
            last_open = one_item['last_open'].rpartition(':')[0]
            # Переопределяем в ячейку для элемента истории
            last_open = '&nbsp;' * 4 + '<span id=history_date>%s</span>' % last_open
            
                        

        # Если продолжаем - значит или обычный элемент списка или из истории
        size = one_item['size']

        ## Устанавливаем картинку - заметка с курсором, или без него
        #if self.items_cursor_position == item_number:
        #    # Текущая позиция - должна быть с курсором
        #    img_src = 'resources/icons/notelist/arrow130_h11.png'
        #    self.items_cursor_url = 'note?' + filename
        #    self.items_cursor_cutename = self.make_cute_name(filename)
        #else:
        #    if filename == active_link:
        #        img_src = 'resources/icons/notelist/g3-g1.png'
        #    else:
        #        img_src = 'resources/icons/notelist/g3.png'

        if filename == active_link:
            line_style = ' id="note_opened" '
        else:
            line_style = ' id="note_other"'

        if self.filter_name != '':
            # Делаем подсветку текста из фильтра в списке заметки
            # cute_filename = re.sub('(' + self.filter_name + ')', '<span id="highlight">' + '\\1</span>', cute_filename, flags=re.I)
            #cute_filename = cute_filename.replace(self.filter_name, '<span id="highlight">' + self.filter_name + '</span>')
            cute_filename = self.highlight_found_text_in_html_source(cute_filename, self.filter_name)

         # html_source += '<p><a href="'+filename+'">'+cute_filename+'</a></p>'
         # Format: multiaction / note :|: note_filename

        note_link = self.action_link('note', filename)
        multiaction_link = self.action_link('multiaction', filename)


        html_source += '<p' + line_style + '><a href="' + note_link + '">' + item_cursor_source + \
            cute_filename + '</a>' + '&nbsp;&nbsp;<font id=filesize>' + hbytes(size) + '</font>' + \
            '&nbsp;&nbsp;&nbsp;&nbsp; <a href="' + multiaction_link + \
            '"><img src="resources/icons/notelist/document62-3.png"></a> ' + \
            last_open + '</p>'
        # print('Сделали html для элемента %s:' % filename)
        # print(html_source)
        # print()
        return html_source



    def make_html_source_for_items_list_in_history_sidebar(self):
        # Создаем html исходник для всего сайдбара истории

        today_ = date.today()

        headers = [
            ['Сегодня', today_, None, [] ],
            ['Вчера', today_ - timedelta(1), today_, [] ],
            ['На неделе', today_ - timedelta(7), today_ - timedelta(1), [] ],
            ['Раньше', None, today_ - timedelta(7), [] ],
            ] 

        html_source = ''
        item_number = 0  # Порядковый номер элемента в списке
        header_element_string = '<p id=history_date>%s</p>'
        current_header_ndx = 0
        current_header_ndx_max = 3
        history_items_count = 0
        active_link = main_window.current_open_note_link

        header, time_period_begin, time_period_end, tmp_items = headers[current_header_ndx]

        for one_item in self.history_items:
            #print('last_open orig: ##%s##' % one_item['last_open'])
            if one_item['last_open'] is None:
                print('Нет записи о последнем открытии у (поиск в контенте?) %s' % one_item['filename'])
                last_open_date = today_
            else:
                if not one_item['last_open'].date():
                    print('Пустая дата в сайдбаре истории у %s' % one_item['filename'])
                last_open_date = one_item['last_open'].date()

            #print('filename: %s\nlast_open: %s\n' % (one_item['filename'], last_open_date) )

            while not current_header_ndx > current_header_ndx_max:

                if not time_period_end:
                    #print('# Сравниваем без конца')
                    item_in_period = (time_period_begin <= last_open_date)
                elif not time_period_begin:
                    #print('# Сравниваем без начала')
                    item_in_period = (last_open_date < time_period_end)
                else:
                    #print('# Просто сравниваем с периодом')
                    item_in_period = (time_period_begin <= last_open_date < time_period_end)

                if item_in_period:
                    #print('Нашли подходящий период: ndx %s, %s - %s, добавляем в массив' % (current_header_ndx, time_period_begin, time_period_end) )
                    #headers[current_header_ndx][3].append(one_item,)
                    # Обрабатываем и добавляем html-исходник
                    headers[current_header_ndx][3].append(self.make_html_source_for_item_history_sidebar(one_item, item_number, active_link))
                    history_items_count += 1
                    break
                else:
                    current_header_ndx += 1
                    if not current_header_ndx > current_header_ndx_max:
                        header, time_period_begin, time_period_end, tmp_items = headers[current_header_ndx]
                        #print('Период не подходит. Следующий: ndx %s, название %s, интервал %s - %s' % (current_header_ndx, header, time_period_begin, time_period_end) )

            # Увеличиваем порядковый номер элемента
            item_number += 1
            # print('Создаем html-код для элемента %s' % item_number)

            #html_source += self.make_html_source_for_item_history_sidebar(one_item)
            
        #print('headers: %s' % headers)
        #history_items_count = 0 
        # Проверка на пустой список элементов
        if history_items_count<1:
            sidebar_empty_string = '<div id=notelist_empty_message>%s</div>'
            history_sidebar_is_empty = '''<br>
  История<br>
  заметок<br>
   saveпуста
'''
            html_source = sidebar_empty_string % history_sidebar_is_empty
        else:
            # Собираем полный исходник на основе двумерного массива элементов, собранного ранее
            for header_item in headers:
                if len(header_item[3])>0:
                    # Есть элементы. Добавляем раздел
                    html_source +=  header_element_string % header_item[0]
                    for one_item in header_item[3]:
                        html_source +=  one_item

        # Используем настройки темы для оформления списка элементов
        #html_source = self.html_body(empty_message=sidebar_empty_message,
                                       #html_source=html_source)

        html_source = '<html>%s<body><div id=sidebar>%s</div></body></html>' % (Theme.html_theme_head, html_source,)

        #print('html_source of notelist: ###%s###' % html_source)
        return html_source







    def make_html_source_from_items_list(self):
        # Собираем html-исходник для окна со списком заметок, используя внутриклассовый список найденных элементов
        html_source = ''
        collect_history_is_done = False  # Признак завершения обработки всех элементов истории
        first_history_item_done = False  # Признак завершения обработки первого элемента истории
        item_number = 0  # Порядковый номер элемента в списке

        #header_element_string = '<div id=notelist_header>%s</div>'
        header_element_string = '<p id=notelist_header>%s</p>'

        for one_item in self.items:
            self.search_progress_indicator_add(items=True)
            if not first_history_item_done and not one_item['history']:
                # У нас отсутствует история - ещё не обработали первый элемент истории, а уже обычная заметка
                first_history_item_done = True
            elif not first_history_item_done and one_item['history']:
                # У нас первый элемент истории. Добавляем заголовк для этого блока
                first_history_item_done = True
                if self.filter_name or self.filter_text:
                    header_string = "Найдено в истории обращений к заметкам:"
                else:
                    header_string = "История обращений к заметкам"
                html_source += header_element_string % header_string

            if not collect_history_is_done and not one_item['history']:
                # У нас первый элемент, который не связан с историей. Надо внести новый заголовок
                collect_history_is_done = True
                if self.filter_name or self.filter_text:
                    header_string = "Найдено в списке неоткрытых заметок:"
                else:
                    header_string = "Список неоткрытых заметок"
                html_source += header_element_string % header_string

            # Увеличиваем порядковый номер элемента
            item_number += 1
            # print('Создаем html-код для элемента %s' % item_number)

            # Добавляем собственно сам элемент в html-обертке
            html_source += self.make_html_source_for_item(one_item, item_number)


        # Проверка на пустой список элементов
        if len(self.items)<1:
            # Проверка на полное отсутствие элементов в списке
            
            notelist_empty_string = '<div id=notelist_empty_message>%s</div>'
            notelist_empty_by_filter = '''<br>
Нет заметок, удовлетворяющих текущему фильтру.

<small>Всего заметок по текущим настройкам: %s</small>''' % self.all_found_files_count

            notelist_empty_by_settings = '''<br>
Нет заметок, удовлетворяющих текущим настройкам.
<small>Проверьте указанный путь к каталогу заметок и настройки выбранных типов файлов заметок.</small>'''

            if self.all_found_files_count<1:
                # Заметок по указанному пути нет вообще
                notelist_empty_message = notelist_empty_string % notelist_empty_by_settings
            else:
                # Заметки есть, но выставленным фильтрам они не удовлетворяют
                notelist_empty_message = notelist_empty_string % notelist_empty_by_filter
        else:
            notelist_empty_message = ''

        ## Получение информации о текущей установке фильтров списка заметок
        #notelist_search_param_string = '<div id=notelist_search_param_message>%s</div>'
        #notelist_search_param_message = ''

        #if self.filter_name:
        #    description_filter_name = ('  Show notes with a name containing <b>"%s"</b>' % self.filter_name)
        #else:
        #    description_filter_name = '  Show notes with any name'
        #if self.filter_text:
        #    description_filter_text = ('containing the text <b>"%s"</b>' % self.filter_text.replace(' ', '&nbsp;'))
        #else:
        #    description_filter_text = 'containing any text'

        #notelist_search_param_message_text = description_filter_name + ' and ' + description_filter_text
        #notelist_search_param_message = notelist_search_param_string % notelist_search_param_message_text

        # Используем настройки темы для оформления списка элементов
        html_source = self.html_body(empty_message=notelist_empty_message,
                                       html_source=html_source)
        #print('html_source of notelist: ###%s###' % html_source)
        return html_source



    def rescan_files_in_notes_path(self, history_update=False):
        # Обновляем список заметок в зависимости от фильтров
        #print('rescan_files, need_rescan: %s, history_update: %s' % (self.need_rescan, history_update) )

        self.get_and_display_filters()
        notelist.set_visible()

        if self.need_rescan:
            # Если требуется рескан файлов - проводим его
            # print('Требуется рескан файлов')
            self.clear_items()
            self.search_progress_indicator_init()
            self.collect_history_items_list()
            self.collect_other_items_list()
            self.need_rescan = False
        else:
            # Обновляем только по статусу истории
            if history_update:
                self.update_items_list_with_history_status()

        # Обновляем информацию в статусной строке главного окна
        main_window.statusbar.showMessage('Found ' + str(self.all_found_files_count) + ' notes (' + hbytes(self.all_found_files_size) + ') at ' + app_settings.path_to_notes + 
                                            ', showed ' + str(self.items_notes_count) + ' notes (' + hbytes(self.items_notes_size) + ') in list.')

        if self.items_notes_count and not self.items_cursor_position:
            # Инициализируем положение курсора в списке
            self.items_cursor_position = 1

        html_string = self.make_html_source_from_items_list()

        print('Делаем исходник для списка заметок')
        root_logger.info('Делаем исходник для списка заметок')
        print('=' * 40)
        root_logger.info('=' * 40)
        # print(html_string)
        root_logger.info(html_string)
        print('=' * 40)
        '=' * 40
        main_window.notelist_source.setHtml(html_string)
        print('Делаем документ для списка заметок')
        main_window.textBrowser_Listnotes.setDocument(main_window.notelist_source)
        print('Закончили со списком заметок')
        self.move_textbrowser_cursor()
        self.search_progress_indicator_hide()
        




    def link_action(self, url=None):
        # Обрабатываем клик по линку в списке заметок
        # Определяем - клик перехода на заметку или на мультидействие по ней
        # Format: multiaction / note :|: note_filename
        if not url:
            # Нажали Enter в списке заметок. Надо получить url из Notelist
            url_string = self.items_cursor_url
        else:
            # Кликнули мышкой на ссылке в списке заметок
            url_string = url.toString()
        #link_attributes = url_string.split('?')
        link_attributes = self.action_link_items(url_string)
        link_type = link_attributes[0] 
        link_filename = link_attributes[1]
        founded_i = None
        if len(link_attributes) > 2:
            founded_i = link_attributes[2]
        if link_type == 'note':
            main_window.open_file_in_editor(link_filename, founded_i)
        if link_type == 'multiaction':
            note.show_note_multiaction_win(link_filename)

    #def open_selected_url(self):
    #    print('DEBUG: open_selected_url("self.items_cursor_url=%s")' % self.items_cursor_url)
    #    link_type, link_filename = self.items_cursor_url.split('?')
    #    if link_type == 'note':
    #        main_window.open_file_in_editor(link_filename)
    #    if link_type == 'multiaction':
    #        note.show_note_multiaction_win(link_filename)
    
    
    #def switch_show_note_content(self)
    #:
    #    if main_window.textBrowser_NoteContents.isVisible():
    #        # Скрываем панель содержания, включаем показ заметки
    #        main_window.textBrowser_NoteContents.setVisible(False)
    #        #main_window.textBrowser_Note.setVisible(True)
    #        main_window.frame_Note.setVisible(True)
    #        #main_window.actionShow_note_contents.setChecked(False)
    #    else:
    #        # Показывам панель содержания, выключаем показ заметки
    #        self.make_note_contents()  # Обновляем html исходник содержание
    #        main_window.textBrowser_NoteContents.setVisible(True)
    #        #main_window.textBrowser_Note.setVisible(False)
    #        main_window.frame_Note.setVisible(False)
    #        #main_window.actionShow_note_contents.setChecked(True)
    

    def __init__(self):
        # QtCore.QObject.connect(main_window.textBrowser_Listnotes, QtCore.SIGNAL("anchorClicked (const QUrl&)"),
                               # self.link_action)
        main_window.textBrowser_Listnotes.anchorClicked.connect(self.link_action)

        main_window.textBrowser_History.anchorClicked.connect(self.link_action)

        # QtCore.QObject.connect(main_window.lineNotelist_Filter, QtCore.SIGNAL("returnPressed ()"),
                               # self.open_selected_url)
        #main_window.lineNotelist_Filter.returnPressed.connect(self.open_selected_url)
        main_window.lineNotelist_Filter.returnPressed.connect(self.link_action)
        
        # QtCore.QObject.connect(main_window.textBrowser_Listnotes, QtCore.SIGNAL("anchorClicked (const QUrl&)"),
        # self.link_action)
        # keyPressed
  
        main_window.actionFast_jump_to_file_or_section.triggered.connect(self.action_triggered)
        
        # QtCore.QObject.connect(main_window.lineEdit_Filter_Note_Text, QtCore.SIGNAL("textChanged( const QString& )"),
                               # main_window.filter_note_text_changed)
        # main_window.lineEdit_Filter_Note_Text.textChanged.connect(main_window.filter_note_text_changed)
        
        # QtCore.QObject.connect(main_window.lineEdit_Filter_Note_Text, QtCore.SIGNAL("returnPressed ()"),
        # main_window.checkBox_Filter_Note_Content_Text_switch_state)

        # self.timer_update = QtCore.QTimer()
        # self.timer_update.setInterval(self.update_timeout)
        self.timer_update.setSingleShot(True)
        
        # QtCore.QObject.connect(self.timer_update, QtCore.SIGNAL("timeout ()"), self.update)
        self.timer_update.timeout.connect(self.update)
        
        # Скрываем дополнительные фреймы
        # main_window.frameNotelist_Filter.setVisible(False)
                
        # self.db = self.DB()


class Table_of_note_contents():
    # Класс работы с таблицей содержания заметки
    
    def __init__(self):
        main_window.actionShow_note_contents.triggered.connect(self.action_triggered)

    def setVisible(self, visible=True):
        if visible:
            # print ('Make visible')
            # Отображаем все виджеты, связанные содержанием заметки
            main_window.stackedWidget.setCurrentIndex(2)
            # Скрываем конкурирующие виджеты
            note.set_visible(False)
            # table_of_note_contents.setVisible(False)
            notelist.set_visible(False)

        # Переключаем все действия, связанные с содержанием
        # note_actions = [ main_window.actionNote_multiaction, main_window.actionShow_note_contents ]
        # for action in note_actions:
        #    action.setEnabled(visible)         
        # Переключаем соотстветствующее отображению действие
        main_window.actionShow_note_contents.setChecked(visible)

    def isVisible(self):
        if main_window.stackedWidget.currentIndex() == 2:
            return True
        else:
            return False

    def action_triggered(self):
        if self.isVisible():
            # Таблица содержимого сейчас отображается.
            # Надо переключиться на предыдущий вид
            pass
            # print ('Table_of_note_contents set INvisible')
        else:
            # Показываем таблицу содержимого
            # print ('Table_of_note_contents set Visible')
            self.setVisible()

    def make_note_contents(self):
        return

        # main_window.actionShow_note_contents
        # note_contents_source

        cursor = main_window.textBrowser_Note.textCursor()
        cur_pos = cursor.position()
        # Вычисляем позицию последней строки в документе
        cursor.movePosition(QtGui.QTextCursor.End)
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        pos_last_line = cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        # Переносимся в начало документа и начинаем перебирать строки
        cursor.movePosition(QtGui.QTextCursor.Start)

        # cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        # cursor.movePosition(QtGui.QTextCursor.EndOfLine)
        
        cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        i = 1
        while cursor.position() > 0:
            cursor.movePosition(QtGui.QTextCursor.Down)
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            # Если не перемещаться на начало линии - зависнет на <li> и др.
            i += 1

        cursor.setPosition(cur_pos)
        

class PreferencesWindow(QtWidgets.QDialog, preferences_window.Ui_DialogPreferences):  # src.ui.
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        # self.connect(self.lineEdit, SIGNAL("textEdited ( const QString& )"), self.updateUi)
        # self.connect(self.lineEdit, SIGNAL("returnPressed()"), self.addToHistory)
        # self.connect(self.labelClearHistory, SIGNAL("	linkActivated( const QString& )"), self.clearHistory)
        # self.labelResult.setText('-')
        # self.lineEdit.setFocus()


class ClearHistoryDialog(QtWidgets.QDialog, clear_history_dialog.Ui_ClearHistoryDialog):

    history_items = []

    history_rec = {}
    history_rec['checkbox'] = None
    history_rec['filename'] = None
    history_rec['last_open'] = None

    def select_all(self):
        for one_item in self.history_items:
            one_item['checkbox'].setChecked(True)

    def select_none(self):
        for one_item in self.history_items:
            one_item['checkbox'].setChecked(False)

    def select_older_than_two_weeks(self):
        today = datetime.now()
        two_weeks = timedelta(days=14)
        for one_item in self.history_items:
            last_open = datetime.strptime(one_item['last_open'], '%Y-%m-%d %H:%M:%S.%f')
            if last_open + two_weeks < today:
                one_item['checkbox'].setChecked(True)
            else:
                one_item['checkbox'].setChecked(False)

    def ok_pressed(self):
        pass
    def cancel_pressed(self):
        pass


    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).clicked.connect(self.accept)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self.pbutSelectAll.clicked.connect(self.select_all)
        self.pbutSelectOlderThanTwoWeeks.clicked.connect(self.select_older_than_two_weeks)
        self.pbutSelectNone.clicked.connect(self.select_none)


class NoteMultiactionWindow(QtWidgets.QDialog, note_multiaction.Ui_DialogNoteMultiaction):  # src.ui.
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)
        
        #
        # pushButton_AddNoteNearly
        # self.connect(self.pushButton_AddChildNote, SIGNAL("Clicked()"), self.add_child_note)
        self.pushButton_AddChildNote.clicked.connect(self.add_child_note)
        self.pushButton_AddNoteNearly.clicked.connect(self.add_note_nearly)
        
        # self.connect(self.lineEdit, SIGNAL("textEdited ( const QString& )"), self.updateUi)
        # self.connect(self.lineEdit, SIGNAL("returnPressed()"), self.addToHistory)
        # self.connect(self.labelClearHistory, SIGNAL("    linkActivated( const QString& )"), self.clearHistory)
        # self.labelResult.setText('-')
        # self.lineEdit.setFocus()

    def make_new_note_file(self, filename, notename):
        # Создание новой пустой заметки

#        note_source = '''Content-Type: text/x-zim-wiki
#Wiki-Format: zim 0.4
#Creation-Date: 2012-09-02T11:16:31+04:00

#''' + '====== ' + notename + ''' ======


#'''
        note_source = '====== ' + notename + ''' ======


'''

        #f = open(filename, "w")
        #f.writelines(note_source)
        #f.close()
        # Новое сохранение в UTF
        fileObj = codecs.open(filename, "w", "utf-8")
        for one_line in note_source:
            fileObj.write(one_line)
        fileObj.close()



    def add_note_nearly(self):
        # Создаем новый файл рядом с указанным, с заданным именем
        new_note_name = self.lineEdit.text()
        new_filename = new_note_name.replace(' ', '_') + '.txt'
        note_path = self.labelNoteFileName.text()
        # note_path = note_path.rpartition('/')[0]
        note_path = note_path.rpartition(os.path.sep)[0]
        # full_filename = note_path+'/'+new_filename
        full_filename = note_path + os.path.sep + new_filename
        self.make_new_note_file(full_filename, new_note_name)
        main_window.open_file_in_editor(full_filename, line_number=3)
        main_window.statusbar.showMessage('New note created: ' + full_filename)
        self.close()

    def add_child_note(self):
        # Создаем новый файл под указанной заметкой, с заданным именем
        new_note_name = self.lineEdit.text()
        new_filename = new_note_name.replace(' ', '_') + '.txt'
        note_path = self.labelNoteFileName.text()
        note_path = note_path.rpartition('.txt')[0]
        # full_filename = note_path+'/'+new_filename
        full_filename = note_path + os.path.sep + new_filename
        if not os.path.exists(note_path):
            # Создаем каталог нужный
            os.makedirs(note_path)
        self.make_new_note_file(full_filename, new_note_name)
        main_window.open_file_in_editor(full_filename, line_number=3)
        main_window.statusbar.showMessage('New note created: ' + full_filename)
        self.close()
    

class MyTextBrowser(QtWidgets.QTextBrowser):
    # Класс, переопределяющий работу основного навигатора заметок
    def __init__(self, parent=None):
        super(MyTextBrowser, self).__init__(parent)
        self.setReadOnly(False)
        self.setObjectName('MyTextBrowser')
    
    def canInsertFromMimeData(self, source):
        if source.hasImage():
            return True
        else:
            return super(MyTextBrowser, self).canInsertFromMimeData(source)

    def insertFromMimeData(self, source):
        # self.insertPlainText(source.text())
        source_html = source.html()
        '''
        if source.hasImage():
            image = QtCore.QVariant(source.imageData())

            document = self.document()
            document.addResource(
                QtGui.QTextDocument.ImageResource,
                QtCore.QUrl("image"),
                image
            )

            cursor = self.textCursor()
            cursor.insertImage("image")
        '''
        
        if source_html == '' or note.paste_as_text_once :
            note.paste_as_text_once = False
            self.insertPlainText(source.text())
        else:
            self.insertHtml(text_format.adaptate_alien_html_styles(source_html))
            

class App_Tests():
    # Класс для внутренних тестов программы. В том числе вызываемых через меню.

    path_to_notes_convertation = ''  # Путь к каталогу, в котором надо проводить тесты
    items = []      # Массив элементов, для которого надо провести тесты

    def collect_items(self, from_directory=False, change_path = False, from_notelist=False):
        # Собираем элементы для последующего тестирования
        self.items = []
        if from_notelist:
            for one_item in notelist.items:
                self.items.append(one_item['filename'])
                #print('one_item %s' % one_item['filename'])

        if from_directory:
            # Диалог выбора пути для сканирования
            if change_path or not self.path_to_notes_convertation:
                print('Предлагаем смену каталога для теста')
                new_path = give_correct_path_under_win_and_other(QtWidgets.QFileDialog.getExistingDirectory(main_window, "Select Directory with your Notes for Test", '' , QtWidgets.QFileDialog.ShowDirsOnly))
                print('path_to_notes_convertation: ##%s##' % new_path)
                #return 0
                if not new_path:
                    print('Каталог не выбран.')
                    return 0
                else:
                    print('Выбран новый каталог для тестов: %s' % new_path)
                    self.update_path_info_for_notes_convertation(new_path, save=True)
            else:
                print('Готовим тест без смены каталога')
            #return 0
            #if not app_settings.path_to_notes:
            #    app_settings.path_to_notes = "D:\Test\\Notes"
            print('Пользователь выбрал для теста каталог %s' % self.path_to_notes_convertation)

            for root, dirs, files in os.walk(self.path_to_notes_convertation):
                for file in files:
                    if os.path.splitext(file)[-1] in notelist.allowed_note_files_extensions:
                    #if file.endswith('.txt'):
                        filename = os.path.join(root, file)
                        self.items.append(filename)
                        print('filename %s' % filename)




    def update_path_info_for_notes_convertation(self, new_path, save=False):
        # Обновляем информацию о новом каталоге для теста
        self.path_to_notes_convertation = give_correct_path_under_win_and_other(new_path)
        # Обновляем текст в действии с запуском в последнем каталоге, чтобы там отображался наш новый путь
        if self.path_to_notes_convertation:
            main_window.actionRun_test_for_notes_convertation_in_last_directory.setText('Run test for notes convertation in %s' % self.path_to_notes_convertation)
        else:
            main_window.actionRun_test_for_notes_convertation_in_last_directory.setText('Run test for notes convertation in last directory')
        if save:
            # Сохраняем переменную с новым каталогом
            app_settings.settings.setValue('path_to_notes_convertation_test', self.path_to_notes_convertation)
            app_settings.settings.sync()

    
    def test_notes_items_for_health_bad_link(self):
        # Тестовая функция, позволяющая проверить результативность функции исправления испорченных ранее ссылок
        print('Запускаем функцию тестирования лечения испорченных ссылок')

        for filename in self.items:
            fileObj = codecs.open(filename, "r", "utf-8")
            original_text = fileObj.read()
            fileObj.close()

            note.health_bad_links(filename, original_text)

        print()
        print('Тестирование завершено.')                                


    def test_notes_items_for_convertation(self):
        # Тестовая функция, позволяющая проверить корректность конвертации форматирования при открытии и сохранении заметок
        print('Запускаем функцию тестирования конвертации форматирования при открытии и сохранении заметок')

        for filename in self.items:
            fileObj = codecs.open(filename, "r", "utf-8")
            original_text = fileObj.read()
            fileObj.close()

            # Загружаем файл в окно редактора
            main_window.open_file_in_editor(filename, dont_save_in_history=True)

            # Конвертируем zim text в html для редактора
            html_source = note.convert_zim_text_to_html_source(original_text)
            # Устанавливаем html-исходник для редактора
            main_window.doc_source.setHtml(html_source)
            main_window.textBrowser_Note.setDocument(main_window.doc_source)


            # Конвертируем файл как-бы для сохранения на диск
            note_source = main_window.textBrowser_Note.toHtml()
            saved_text = note.convert_html_source_to_zim_text(note_source)

            # Сравниваем оригинал и "сохраненный" вариант
            diff_result = get_diff_text(original_text, saved_text, filename, filename + '-saved')
            if diff_result:
                print()
                # print('Результат сравнения:')
                print(diff_result)
                # for line in diff_result:
                #    print(line)
            else:
                print('.', end="", flush=True)

        print()
        print('Тестирование завершено.')

    def health_bad_links_for_notes_from_notelist(self):
        # Выполняем тест для текущего списка заметок
        self.collect_items(from_notelist=True)
        self.test_notes_items_for_health_bad_link()

    def notes_convertation_for_notelist(self):
        # Выполняем тест для текущего списка заметок
        self.collect_items(from_notelist=True)
        self.test_notes_items_for_convertation()

    def notes_convertation_for_directory(self, change_path=False):
        # Выполняем тест для директории из настроек
        self.collect_items(from_directory=True, change_path=change_path)
        self.test_notes_items_for_convertation()

    def notes_convertation_change_path(self):
        self.notes_convertation_for_directory(change_path=True)

    
    def __init__(self):
        print('Инициализация класса тестов')

        # Получение из настроек пути к каталогу тестов
        new_path = app_settings.settings.value('path_to_notes_convertation_test')
        self.update_path_info_for_notes_convertation(new_path)

        main_window.actionRun_test_for_notes_convertation_in_last_directory.triggered.connect(self.notes_convertation_for_directory)
        main_window.actionRun_test_notes_convertation_for_notelist.triggered.connect(self.notes_convertation_for_notelist)
    
        main_window.actionSelect_another_directory_and_run_test_for_notes_convertation.triggered.connect(self.notes_convertation_change_path)
        
        main_window.actionRun_test_health_bad_links_for_notes_from_notelist.triggered.connect(self.health_bad_links_for_notes_from_notelist)




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
calculator_win = calculator.CalculatorWindow()

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


