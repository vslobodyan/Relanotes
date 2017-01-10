# -*- coding: utf-8 -*-

# __author__ = 'vyacheslav'
# __version__ = '0.03'


import sys
import os
import re
import time
import sqlite3
from datetime import datetime  # , date  #, time
import codecs

#from src.ui import calculator_window, preferences_window, note_multiaction
from src.ui import preferences_window, note_multiaction
from src.ui.main_window import *
from src import calculator

#from PyQt4.QtCore import *
#from PyQt4.QtGui import *

from PyQt5 import QtCore, QtGui, QtWidgets

from src.routines import *

# from PyQt5.QtCore import *
# from PyQt5.QtGui import *



settingsNameOrganization = 'DigiTect'
settingsNameGlobal = 'Relanotes'
QtCore.QCoreApplication.setOrganizationName(settingsNameOrganization)
QtCore.QCoreApplication.setApplicationName(settingsNameGlobal)

# Получаем путь к каталогу с настройками программы по данным QStandardPaths
app_config_path = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppDataLocation);
# Подробнее о выборе пути: http://doc.qt.io/qt-5/qstandardpaths.html
#config_homePath = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppConfigLocation);
#config_homePath = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.AppLocalDataLocation);

app_config_path = give_correct_path_under_win_and_other(app_config_path)

print("Каталог с настройками программы: %s" % app_config_path)
# Если не существует - создаем.
if not os.path.exists(app_config_path):
    os.makedirs(app_config_path)

full_ini_filename = os.path.join(app_config_path, 'settings.ini')
# print("Полный путь к ini-файлу настроек: %s" % full_ini_filename)

settings = QtCore.QSettings(full_ini_filename, QtCore.QSettings.IniFormat)
# settings.setFallbacksEnabled(False)    # File only, no fallback to registry or or.

# settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
#     settingsNameOrganization, settingsNameGlobal)
    

path_to_notes = settings.value('path_to_notes')
print('DEBUG: path_to_notes from settings: %s' % path_to_notes)
# Проверяем БАГ, когда в переменную библиотека QT занесла неправильные слеши
path_to_notes = give_correct_path_under_win_and_other(path_to_notes)

# Основные переменные

# Получаем путь к каталогу, в котором лежат файлы и подкаталоги программы
path_to_me = os.path.split(os.path.abspath(sys.argv[0]))[0]
print("path_to_me:", path_to_me)
# '/home/vchsnr/Dropbox/Projects/Relanotes/Relanotes-next/'
# Переходим в свой каталог, чтобы относительные пути до настроек и прочих файлов оказались
# корректными при запуске из любого каталога.
os.chdir(path_to_me)

path_to_home = os.path.expanduser("~")
print("path_to_home:", path_to_home)

prog_name = 'Relanotes'

# path_to_notes = '/home/rat/Dropbox/Data/s_zim/Notes/'
# path_to_notes = path_to_me+'Notes/'
#print("path_to_notes:", path_to_notes)

# FIXME: . При зачеркивании (или другом выделении) текста дальнейшая печать идет в таком-же новом стиле. Надо сделать
# чтобы шла как обычный текст. Пример - зачеркивание старого пароля и запись после него нового.

notelist_selected_position = 0  # Позиция курсора в списке заметок, открываемой по Enter
notelist_selected_url = ''  # Ссылка выбранного

# Список истории
# rec = [ 'note' / 'list', 'filename' / 'filter', datetime ]
# history_recs = [ rec1, rec2, .. ]

# history_recs = []
history_position = 0

full_state_db_filename = os.path.join(app_config_path, 'state.db')
state_db = sqlite3.connect(full_state_db_filename)
state_db_connection = state_db.cursor()

# full_notelist_db_filename = os.path.join(app_config_path, 'notelist.db')
# notelist_db = sqlite3.connect(full_notelist_db_filename)
# notelist_db_connection = notelist_db.cursor()


"""
Список заметок и статус работы с ними - реализовано в классе Notelist, переменная file_recs
rec = [ id, filename, cute_name, parent_id, subnotes_count, size, favorite, hidden, 
        last_change, last_open, count_opens, opened ]

file_recs = [ rec1, rec2, rec3, .. ]
file_recs = []
"""



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
        global notelist_selected_position

        # if not main_window: exit()

        # После блокировки и сворачивания окна перехыватываем восстановление окна и
        # запускаем таймер сворачивания снова, если он неактивный.
        if main_window.locked and main_window.isVisible() and (event.type() in [QEvent.WindowStateChange]) and \
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
            #print('keypress to '+receiver.objectName())
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
                        
                        # cursor.setCharFormat(note.format.editor_default_format)
                        cursor.insertHtml(note.format.editor_default_font_span+'<br>')
                        # note.format.clear_format()
                        # return super(MyEventFilter,self).eventFilter(receiver, event)
                        return True
                    
            # Клавиатурные события приходящие на окно общего списка заметок
            # передаем на поле фильтра имени заметок
            if receiver.objectName() == 'textBrowser_Listnotes':
                main_window.lineNotelist_Filter.keyPressEvent(event)

                # На клавишу вниз - увеличиваем индекс выбранного
                if event.key() == QtCore.Qt.Key_Down:
                    # QMessageBox.information(None,"Filtered Key Press Event!!", "Key Down")
                    notelist_selected_position += 1
                    notelist.update()
                    return True
                    
                # На клавишу вверх - уменьшаем индекс выбранного
                if event.key() == QtCore.Qt.Key_Up:
                    # QMessageBox.information(None,"Filtered Key Press Event!!", "Key Down")
                    notelist_selected_position -= 1
                    notelist.update()
                    return True

                # На Esc- возвращаемся в предыдущее открытую панель (текст заметки или содержание)
                if event.key() == QtCore.Qt.Key_Escape:
                    if notelist_selected_url != '':
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
                    notelist_selected_position += 1
                    notelist.update()
                    return True

                # На клавишу вверх - уменьшаем индекс выбранного
                if event.key() == QtCore.Qt.Key_Up:
                    # QMessageBox.information(None,"Filtered Key Press Event!!", "Key Down")
                    notelist_selected_position -= 1
                    notelist.update()
                    return True

                # На Esc- возвращаемся в предыдущее открытую панель (текст заметки или содержание)
                if event.key() == QtCore.Qt.Key_Escape:
                    if notelist_selected_url != '':
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
    doc_source = QtGui.QTextDocument()
    sidebar_source = QtGui.QTextDocument()
    notelist_source = QtGui.QTextDocument()
    current_open_note_link = ''
    timer_lock_ui = QtCore.QTimer()
    lock_ui_timeout = 10000
    locked = False
    timer_window_minimize = QtCore.QTimer()
    window_minimize_timeout = 10000

    # Действия, относящиеся только к редактору заметки
    note_editor_actions = None
    # Какие действия выводить в панели справа от редактора заметки
    note_editor_toolbar_actions = None

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)
        self.setupUi(self)

        # settings.setValue('int_value', 42)
        try:
            #self.layoutSettings = QtCore.QSettings(os.path.join(path_to_me, "./layout.ini"), QtCore.QSettings.IniFormat)
            #self.restoreGeometry(self.layoutSettings.value("mainWindow/geometry"))
            #self.restoreState(self.layoutSettings.value("mainWindow/windowState"))

            self.restoreGeometry(settings.value("mainWindow/geometry"))
            self.restoreState(settings.value("mainWindow/windowState"))
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
            self.actionClear, self.actionFind_in_current_note,
            self.actionFind_next_in_cur_note,
            self.actionShow_content_collapse_all_H,
            self.actionCollapse_all_H_exclude_cur,
            self.actionCollapse_cur_H, self.actionExpand_all_H,
            self.actionSave_note, self.action_ClearFormat,
            self.actionCode
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
        #QtCore.QObject.connect(self.timer_window_minimize, QtCore.SIGNAL("timeout ()"), self.minimize)
        self.timer_window_minimize.timeout.connect(self.minimize)
    
        # self.webView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        # self.textBrowser_History.setOpenExternalLinks(true)
        # self.connect(self.ui.webView, QtCore.SIGNAL("linkClicked (const QUrl&)"), self.loadfile2)
        # QtCore.QObject.connect(self.webView, QtCore.SIGNAL("linkClicked (const QUrl&)"), self.loadfile2)
        
        #QtCore.QObject.connect(self.textBrowser_History, QtCore.SIGNAL("anchorClicked (const QUrl&)"), self.loadfile_from_history)
        self.textBrowser_History.anchorClicked.connect(self.loadfile_from_history)

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
        self.lineNotelist_Filter.textChanged.connect(self.notelist_filter_changed)

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
        
        self.actionSelect_dir_and_run_test_open_save_notes.triggered.connect(self.select_dir_and_run_test_open_save_notes)

        self.actionShow_note_HTML_source.triggered.connect(self.show_html_source)
        self.plainTextEdit_Note_Ntml_Source.setVisible(False)

        # QtGui.QFileDialog.windowFilePath(self)
        global path_to_notes
        print("path_to_notes: %s" % path_to_notes)
        if not path_to_notes or not os.path.exists(path_to_notes):
            # print("")
            reply = QtWidgets.QMessageBox.question(self, "Ваши заметки были перемещены?",
                                         "Каталог " + str(path_to_notes) + " с Вашими заметками не существует.\n"
                                                                      "Открыть другой каталог с заметками?",
                                         QtWidgets.QMessageBox.Yes|QtWidgets.QMessageBox.No|QtWidgets.QMessageBox.Cancel)
            if reply == QtWidgets.QMessageBox.Cancel:
                # print("Заметки по указанному пути отсутствуют. Пользователь не хочет продолжать работу.")
                exit()
            elif reply == QtWidgets.QMessageBox.Yes:
                # print("Выбираем новый путь к заметкам")
                #path_to_notes = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes") )
                #raw_path_to_notes = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes", '' , QtWidgets.QFileDialog.ShowDirsOnly)
                path_to_notes = give_correct_path_under_win_and_other(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes", '' , QtWidgets.QFileDialog.ShowDirsOnly))
                settings.setValue('path_to_notes', path_to_notes)
                settings.sync()
                print("Выбран новый путь к заметкам:", path_to_notes)

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

    def filter_note_text_changed(self, filter_text=''):
        global notelist_selected_position
        notelist_selected_position = 0
        notelist.timer_update.start(notelist.update_timeout)

    def notelist_filter_changed(self, filter_text):
        global notelist_selected_position
        notelist_selected_position = 0
        notelist.timer_update.start(notelist.update_timeout)

    def show_html_source(self):
        if self.plainTextEdit_Note_Ntml_Source.isVisible():
            self.plainTextEdit_Note_Ntml_Source.setVisible(False)
        else:
            self.plainTextEdit_Note_Ntml_Source.setVisible(True)

    def select_dir_and_run_test_open_save_notes(self):
        # Тестовая функция, позволяющая проверить корректность конвертации форматирования при открытии и сохранении заметок
        print('Запускаем функцию тестирования конвертации форматирования при открытии и сохранении заметок')

        # Диалог выбора пути для сканирования
        path_to_notes = give_correct_path_under_win_and_other(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory with your Notes for Test", '' , QtWidgets.QFileDialog.ShowDirsOnly))
        if not path_to_notes:
            print('Каталог не выбран.')
            return 0
        print('Пользователь выбрал для теста каталог %s' % path_to_notes)

        for root, dirs, files in os.walk(path_to_notes):
            for file in files:
                if file.endswith('.txt'):
                    filename = os.path.join(root, file)
                    # Читаем файл в память

                    # Загружаем файл в окно редактора

                    # Конвертируем файл для сохранения на диск





    def save_note_cursor_position(self):
        print('Проверка необходимости сохранить позицию открытой заметки')
        # Проверяем - есть ли открытая заметка в окне редактора

        filename = main_window.current_open_note_link
        if filename:
            current_position = main_window.textBrowser_Note.textCursor().position()
            print('Файл открытой заметки %s и позиция курсора %s' % (filename, current_position) )
            # Если есть - сохраняем для неё последнюю позицию курсора

            # Обновляем запись в базе
            state_db_connection.execute("UPDATE file_recs SET current_position=?  WHERE filename=?",
                                        (current_position, filename) )
            state_db.commit()                        
        else:
            print('Открытой заметки нет.')


    def closeEvent(self, e):
        #self.layoutSettings.setValue("mainWindow/geometry", self.saveGeometry())
        #self.layoutSettings.setValue("mainWindow/windowState", self.saveState())
        #self.layoutSettings.sync()

        # Сохраняем позицию заметки, если она была открыта
        self.save_note_cursor_position()

        settings.setValue("mainWindow/geometry", self.saveGeometry())
        settings.setValue("mainWindow/windowState", self.saveState())
        settings.sync()

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

        try:
            state_db_connection.execute('''CREATE TABLE history_recs
                 (type text, value text, datetime integer)''')
        except:
            pass
            
        # Список файлов
        # rec = [ filename, cute_name, parent_id, subnotes_count, last_change, last_open, count_opens, current_position ]
        # file_recs = [ rec1, rec2, rec3, .. ]

        try:
            state_db_connection.execute('''CREATE TABLE file_recs
             (filename text PRIMARY KEY, cute_name text, parent_id integer, subnotes_count integer,
             last_change integer, last_open integer, count_opens integer, current_position integer)''')
        except:
            pass

        # Дерево подразделов в файлах заметок

        # Списки меток в файлах заметок
        
        # Списки задач в файлах заметок

        # Insert a row of data
        # state_db_connection.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")

        # Save (commit) the changes
        state_db.commit()
        
        # We can also close the connection if we are done with it.
        # Just be sure any changes have been committed or they will be lost.
        # state_db.close()


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

    def renew_history_list(self, active_link):
        html_string = '<p id=history_date>Сегодня</p>'

        # state_db_connection.execute('''CREATE TABLE history_recs
        #     (type text, value text, datetime integer)''')

        for row in state_db_connection.execute("SELECT * FROM history_recs WHERE type='note' ORDER BY datetime DESC"):
            type_rec, file_rec, date_rec = row

        # for file_rec in filenames:
            # self.listWidget.addItem(file_rec)
            # file_rec = path_to_notes + file_rec
            
            # if type_rec == 'note':
        
            file_rec = give_correct_path_under_win_and_other(file_rec)
            
            #if file_rec.rpartition('/')[0]+'/' == path_to_notes:
            if file_rec.rpartition(os.path.sep)[0]+os.path.sep == path_to_notes:
                # У нас корневая заметка
                file_parent = ''
            else:
                #file_parent = file_rec.split('/')[-2] + ': '
                # print('DEBUG: file_rec.split= %s' % file_rec.split(os.path.sep) )
                file_parent = file_rec.split(os.path.sep)[-2] + ': '
            
            #file_cute_name = file_rec.rpartition('/')[2]
            file_cute_name = file_rec.rpartition(os.path.sep)[2]
            file_cute_name = file_cute_name.rpartition('.txt')[0]
            file_cute_name = file_cute_name.replace('_', ' ')
            # else:
            #    file_cute_name = file_rec

            if file_rec == active_link:
                line_style = ' id="current_note" '
                # img_src = 'resources/icons/notelist/g3-g1.png'
            else:
                # img_src = 'resources/icons/notelist/g3.png'
                line_style = ''

            # html_string += '<p'+line_style+'><a href="'+file_rec+'"><img src="'
            # +img_src+'">&nbsp;'+file_parent+file_cute_name+'</a></p>'
            html_string += '<p'+line_style+'><a href="'+file_rec+'" title="'\
                           + file_parent + file_cute_name + '">' + file_parent + file_cute_name + '</a></p>'
            # state_db.commit()

        html_string += '<p id=history_date>Вчера</p> .....'
        html_string = '<html>%s<body><div id=sidebar>%s</div></body></html>' % (Theme.html_theme_head, html_string, )
        self.sidebar_source.setHtml(html_string)
        self.textBrowser_History.setDocument(self.sidebar_source)
        # self.textBrowser_History.setHtml(html_string)

    def note_text_changed(self):
        # self.plainTextEdit_Note_Ntml_Source.setPlainText(self.textBrowser_Note.toHtml())
        # self.plainTextEdit_Note_Ntml_Source.setPlainText(self.doc_source.toHtml())
        # print('Текст заметки изменен')
        pass
   
    def open_file_in_editor(self, filename, founded_i=0):
        self.statusbar.showMessage('Загружается файл '+filename)
        print('DEBUG: open_file_in_editor("filename=%s")' % filename)
        filename = get_correct_filename_from_url(filename)
        print('DEBUG: open_file_in_editor(" after unquote =%s")' % filename)
        
        # Сохраняем позицию предыдущей заметки, если она была открыта
        self.save_note_cursor_position()

        # print('link_note_pos: '+str(link_note_pos))
        # TODO: .. Профилировать скорость загрузки файла и отображения его текста
        
        # Проверяем на переход из списка файлов
        if notelist.is_visible():
            # rec = [ 'note' / 'list', 'filename' / 'filter', datetime ]
            if history_position == 0:
                # history_recs.append(['list', self.lineNotelist_Filter.text(), datetime.now()])
                # state_db_connection.execute('''CREATE TABLE history_recs
                # (type text, value text, datetime integer)''')
                # rec = [ 'note' / 'list', 'filename' / 'filter' ]
                # new_recs = []
                new_recs_sel = []
                
                if self.lineNotelist_Filter.text() != '':
                    # Фильтр есть, записываем его в историю
                    # new_recs = [ ( 'list', self.lineNotelist_Filter.text(), datetime.now() ),]
                    new_recs_sel = [('list', self.lineNotelist_Filter.text(), ), ]
                # Пишем открытие заметки
                # new_recs += [ ( 'note', filename, datetime.now() ), ]
                new_recs_sel += [('note', filename, ), ]
                
                ######### history_recs
                # Перед добавлением новой записи проверяем - нет-ли записи с такими-же значениями уже в списке
                for rec in new_recs_sel:
                    # print ( 'rec: '+str(rec) + ' len:' + str(len(rec)) )
                    state_db_connection.execute("SELECT * FROM history_recs WHERE type=? AND value=?", rec )
                    existed_rec = state_db_connection.fetchall()
                    if len(existed_rec) > 0:
                        # print (existed_rec)
                        # Запись уже есть. Прописываем ей новое время открытия.
                        state_db_connection.execute("UPDATE history_recs SET datetime=? WHERE type=? AND value=?",
                                                    (datetime.now(), rec[0], rec[1]))
                        state_db.commit()                        
                    else:
                        # Записи нет. Создаем новую.
                        # print ( 'rec_tmp: '+str(rec_tmp)+' len:'+str(len(rec_tmp)) )
                        state_db_connection.execute("INSERT INTO history_recs VALUES (?,?,?)",
                                                    (rec[0], rec[1], datetime.now()))
                        state_db.commit()


                print('FILE_RECS for %s starting here' % filename)
                ######### file_recs
                # Перед добавлением новой записи проверяем - нет-ли записи с такими-же значениями уже в списке
                if notelist.file_in_history(filename):
                    print('FILE_RECS: для файла %s запись есть. Обновляем.' % filename)
                    # Запись уже есть. Прописываем ей новое время открытия и увеличиваем счетчик открытий
                    # Получаем количество открытий данного файла
                    state_db_connection.execute("SELECT count_opens, current_position FROM file_recs WHERE filename=?", (filename,) )
                    rec_count_opens, rec_current_position = state_db_connection.fetchone()
                    print('Количество открытий заметки: %s, последняя позиция курсора: %s' % ( rec_count_opens, rec_current_position ) )
                    # Обновляем запись в базе
                    state_db_connection.execute("UPDATE file_recs SET last_open=?, count_opens=?  WHERE filename=?",
                                                (datetime.now(), rec_count_opens+1, filename) )
                    state_db.commit()                        
                else:
                    # Записи нет. Создаем новую.
                    # print ( 'rec_tmp: '+str(rec_tmp)+' len:'+str(len(rec_tmp)) )

                    rec_current_position = None
                    print('FILE_RECS: для файла %s записи нет. Создаем новую.' % filename)
                    # print ( 'rec_tmp: '+str(rec_tmp)+' len:'+str(len(rec_tmp)) )
                    state_db_connection.execute("INSERT INTO file_recs (filename, last_open, count_opens) VALUES (?,?,?)",
                                                    (filename, datetime.now(), 1) )
                    state_db.commit()


        #f = open(filename, "r")
        #lines = f.read()
        #f.close()

        fileObj = codecs.open( filename, "r", "utf-8" )
        lines = fileObj.read()        
        fileObj.close()

        # В конец добавляем образцы заголовков, чтобы снять реальный стиль, созданный им в редакторе
        lines += '====== T ======\n' \
                 '===== T =====\n' \
                 '==== T ====\n' \
                 '=== T ===\n' \
                 '== T ==\n' \
                 '= T =\n'

        # Translate plain text to html and set as doc source
        self.doc_source.setHtml(self.convert_txt_to_html(lines))
        self.textBrowser_Note.setDocument(self.doc_source)

        # Получаем реальные стили заголовков. И удаляем их из документа
        tmp_html_source = self.textBrowser_Note.toHtml()

        # print(tmp_html_source, '=============')

        l_a_name = len('<a name="head1"></a>')
        pos_added_fonts = pos_font_end = tmp_html_source.rfind('<a name="head1')-1
        for i in range(1,7):
            pos_font_begin = tmp_html_source.find('<a name="head', pos_font_end)
            pos_font_end = tmp_html_source.find('>T<', pos_font_begin)+1
            tmp_str = tmp_html_source[pos_font_begin+l_a_name:pos_font_end]
            if i == 1:
                note.format.editor_h1_span = tmp_str
            if i == 2:
                note.format.editor_h2_span = tmp_str
            if i == 3:
                note.format.editor_h3_span = tmp_str
            if i == 4:
                note.format.editor_h4_span = tmp_str
            if i == 5:
                note.format.editor_h5_span = tmp_str
            if i == 6:
                note.format.editor_h6_span = tmp_str

            # print('str:', tmp_str)

        note.format.editor_h_span = ['0-empty', note.format.editor_h1_span, note.format.editor_h2_span,
                                      note.format.editor_h3_span, note.format.editor_h4_span,
                                      note.format.editor_h5_span, note.format.editor_h6_span]

        tmp_html_source = tmp_html_source[:pos_added_fonts-len('--&gt;</span>')]
        self.textBrowser_Note.setHtml(tmp_html_source)

        # self.textBrowser_Note.setHtml(tmp_html_source)

        # Передвигаем курсор на нужную позицию методом поиска, по номеру
        # вхождения искомой фразы, несколько раз выполняя встроенный в редактор поиск
        i = 0
        self.textBrowser_Note.moveCursor(QtGui.QTextCursor.Start)
        while i < int(founded_i):
            #text_to_find = self.lineEdit_Filter_Note_Text.text()
            text_to_find = notelist.filter_text
            self.textBrowser_Note.find(text_to_find)
            # print ('Выполняем поиск')
            # cursor.movePosition(QtGui.QTextCursor.Down)
            i += 1
        # self.textBrowser_Note.setTextCursor(cursor)

        main_window.frameSearchInNote.setVisible(False)
        note.set_visible()
        self.textBrowser_Note.setFocus()
        
        #file_cute_name = filename.rpartition('/')[2]
        file_cute_name = filename.rpartition(os.path.sep)[2]
        file_cute_name = file_cute_name.replace('_', ' ')
        file_cute_name = file_cute_name.rpartition('.txt')[0]
        self.setWindowTitle(prog_name + ' - ' + file_cute_name)
        self.renew_history_list(filename)
        self.statusbar.showMessage('Заметка загружена')
        self.current_open_note_link = filename

        # Восстанавливаем позицию предыдущую позицию курсора, если она была сохранена
        if rec_current_position:
            print('Перемещаем курсор в заметке на позицию %s' % rec_current_position)
            # Получаем копию текущего курсора
            cursor = main_window.textBrowser_Note.textCursor()
            # Устанавливаем копии нужное положение
            cursor.setPosition(rec_current_position)
            # Делаем копию основным курсором текстового редактора с новой позицией
            main_window.textBrowser_Note.setTextCursor(cursor)

        # rec = [ 'note' / 'list', 'filename' / 'filter', datetime ]
        # if history_position==0:
        #    history_recs.append(['note', filename, datetime.now()])

    def loadfile2(self, url):
        # self.ui.listView.
        # path_to_notes + filenames[self.ui.listWidget.currentRow()]
        # filenames[self.ui.listWidget.currentRow()]
        # self.textEdit.setPlainText(url.toString())
        
        # Переход совершен из списка, сбрасываем позицию перемещения
        # в списке истории.
        history_position = 0
        self.open_file_in_editor(url.toString())

    def loadfile_from_history(self, url):
        # Переход совершен из истории, сбрасываем позицию перемещения
        # в списке истории, а также скрываем поле фильтрам списка
        # заметок по названию
        history_position = 0
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

    def convert_txt_to_html(self, lines):
        # make_initiative_html

        html_source = lines
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
        
        # 1. Режем контент заметки на строки
        text_source_lines = html_source.split('\n')
        
        # 2. Проверяем наличие ключевых слов в первых 3 строчках
        first_part1 = text_source_lines[0].split(':')[0]
        first_part2 = text_source_lines[1].split(':')[0]
        first_part3 = text_source_lines[2].split(':')[0]
        
        # 3. Удаляем строки, в которых обнаружены служебные слова
        if first_part1 in zim_wiki_tags and first_part2 in zim_wiki_tags and first_part3 in zim_wiki_tags:
            # Удаляем первые 3 строчки
            del text_source_lines[0:3]
        
        if first_part1 in zim_wiki_tags and first_part2 in zim_wiki_tags and first_part3 not in zim_wiki_tags:
            # Удаляем первые 2 строчки
            del text_source_lines[0:2]

        if first_part1 in zim_wiki_tags and first_part2 not in zim_wiki_tags and first_part3 not in zim_wiki_tags:
            # Удаляем первую строчку
            del text_source_lines[0:1]

        # 4. Если осталась первая пустая строка - удаляем и её (она обычно остается после служебных)
        if not text_source_lines[0].strip():
            # Удаляем первую строчку
            del text_source_lines[0:1]


        # x. Собираем контент заметки обратно в строки
        html_source = '\n'.join(text_source_lines)
        

        #html_source = re.sub('(Content-Type: text/x-zim-wiki)', '<!--', html_source)
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
        html_source = re.sub('====== (.*?) ======', '<font id=head1>\\1</font>', html_source)
        html_source = re.sub('===== (.*?) =====', '<font id=head2>\\1</font>', html_source)
        html_source = re.sub('==== (.*?) ====', '<font id=head3>\\1</font>', html_source)
        html_source = re.sub('=== (.*?) ===', '<font id=head4>\\1</font>', html_source)
        html_source = re.sub('== (.*?) ==', '<font id=head5>\\1</font>', html_source)
        html_source = re.sub('= (.*?) =', '<font id=head6>\\1</font>', html_source)
        
        # html_source = re.sub('====== (.*?) ======', '--><p id=head1>\\1</p>', html_source)
        # html_source = re.sub('===== (.*?) =====', '<p id=head2>\\1</p>', html_source)
        # html_source = re.sub('==== (.*?) ====', '<p id=head3>\\1</p>', html_source)
        # html_source = re.sub('=== (.*?) ===', '<p id=head4>\\1</p>', html_source)
        # html_source = re.sub('== (.*?) ==', '<p id=head5>\\1</p>', html_source)
        # html_source = re.sub('= (.*?) =', '<p id=head6>\\1</p>', html_source)
        
        # TODO: re.search, groups - обнаружение и сохранение позиций вики-форматирования
        
        # 'strong':   Re('\*\*(?!\*)(.+?)\*\*'),
        html_source = re.sub('\*\*(.*?)\*\*', '<strong>\\1</strong>', html_source)

        html_source = re.sub('//(.*?)//', '<i>\\1</i>', html_source)

        # 'strike':   Re('~~(?!~)(.+?)~~'),
        html_source = re.sub('~~(.*?)~~', '<s>\\1</s>', html_source)

        # 'emphasis': Re('//(?!/)(.+?)//'),
        html_source = re.sub('\n\* ([^\n]*)', '<ul><li>\\1</li></ul>', html_source)
        html_source = re.sub('</ul>\n', '</ul>', html_source)

        html_source = re.sub('(Created [^\n]*)', '<font id="created">\\1</font>', html_source)

        # 'code':     Re("''(?!')(.+?)''"),
        html_source = re.sub("''(?!')(.+?)''", '<font id="code">\\1</font>', html_source)

        # 'mark':     Re('__(?!_)(.+?)__'),
        html_source = re.sub('__(?!_)(.+?)__', '<font id="mark">\\1</font>', html_source)

        # Внутренний линк
        # 'link':     Re('\[\[(?!\[)(.+?)\]\]'),
        html_source = re.sub('\[\[(?!\[)(.+?)\]\]', '<a href="\\1">\\1</a>', html_source)

        # Внешний линк
        # html_source = re.sub('(http://[^ \n]*)','<a href="\\1">\\1</a>', html_source)
        html_source = re.sub('([^ \n]*://[^ \n]*)', '<a href="\\1">\\1</a>', html_source)

        # 'img':      Re('\{\{(?!\{)(.+?)\}\}'),
        html_source = re.sub('\{\{(?!\{)(.+?)\}\}', '<img src="\\1">', html_source)
        html_source = re.sub('<img src="~', '<img src="'+path_to_home, html_source)
        
        # TODO: . Сделать превращение в линк электронной почты и её сохранение

        # 'tag':        Re(r'(?<!\S)@(?P<name>\w+)\b', re.U),
        # 'sub':	    Re('_\{(?!~)(.+?)\}'),
        # 'sup':	    Re('\^\{(?!~)(.+?)\}'),
        # \n --> <br>

        html_source = html_source.replace('\n', '<br>')
        # html_source = html_source.replace('\n', '</p><p>')
        
        html_source = '<html>%s<body>%s</body></html>' % (Theme.html_theme_head, html_source, )
        return html_source


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

    class Format():
        
        # h_span_preformatting = '<span style=" font-family:\'%s\'; font-size:%spx; font-weight:%s; color:%s;">'
        
        editor_h1_span = '' 
        editor_h2_span = ''
        editor_h3_span = ''
        editor_h4_span = ''
        editor_h5_span = ''
        editor_h6_span = ''
        editor_h_span = ['0-empty', editor_h1_span, editor_h2_span, editor_h3_span, editor_h4_span, editor_h5_span, editor_h6_span]

        # FIXME: Цвет текста подходит для светлой темы. Не подходит для темной.
        editor_default_font_span = '<span style=" font-family:\'Sans\'; font-size:15px; font-weight:0; color:#1a1a1a;">'
        #editor_default_font_span = '<span>'
        
        # editor_italic_span =
        editor_strikethrough_span = \
            '<span style=" font-family:\'Sans\'; font-size:15px; text-decoration: line-through; color:#aaaaaa;">'
        # editor_bold_span =
        # FIXME: Цвет кода подходит для светлой темы. Не подходит для темной.
        # editor_code_span = '<span style=" font-family:\'Mono\'; font-size:16px; color:#501616;">'
        editor_code_span = '<span style=" font-family:\'Mono\'; font-size:16px; color:#9c2b2b;">'

        editor_mark_span = \
            '<span style=" font-family:\'Sans\'; font-size:15px; color:#1a1a1a; background-color:#ffccaa;">'
        editor_li_span = \
            '<li style=" font-family:\'Sans\'; font-size:15px;" style=" margin-top:6px; margin-bottom:6px; ' \
            'margin-left:-20px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'
        
        # FIXME: Цвет ссылок подходит для светлой темы. Не подходит для темной.
        # editor_link_external_style = 'style=" font-size:15px; color:#004455; text-decoration: none;"'
        editor_link_external_style = 'style=" font-size:15px; color:#0089ab; text-decoration: none;"'

        # editor_link_local_span =
        # editor_link_wiki_span =

        editor_default_font = QtGui.QFont()
        # editor_default_font.setStyle(QFont.Normal)
        # editor_default_font.setBold(False)
        editor_default_font.setFamily('Sans')
        editor_default_font.setPixelSize(15)
                 
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
            print('Получили для адаптации при вставке следующий html:\n'+html_source+'\n')

            # TODO: ... записать в преимущества функцию умного преобразования инородного html и вставки простого текста
            #  в свой html/wiki
            # TODO: ... сделать функцию иморта из любого html на основе преобразования инородного html в свой
            
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
                    pos1 = html_source.find('<a', pos)
                    pos_href_1 = html_source.find('href=', pos1)
                    pos_href_1 = html_source.find('"', pos_href_1)
                    pos_href_2 = html_source.find('"', pos_href_1+1)
                    pos2 = html_source.find('>', pos_href_2)
                    href = html_source[pos_href_1+1:pos_href_2]
                    new_link = ' <a '+self.editor_link_external_style+' href="'+href+'">'+href+'</a> '
                    
                    html_source = html_source[:pos1]+new_link+html_source[pos2+1:]
                    pos = pos2 
                
                # print('\n С заменой A:\n'+html_source)

            # Картинки заменяем ссылками на них
            if html_source.find('<img') >= 0:
                pos = 0
                while html_source.find('<img', pos) >= 0:
                    pos1 = html_source.find('<img', pos)
                    pos2 = html_source.find('>', pos1)
                    pos_src_1 = html_source.find('src=', pos1)
                    pos_src_1 = html_source.find('"', pos_src_1)
                    pos_src_2 = html_source.find('"', pos_src_1+1)
                    
                    pos = pos1 
                    # print('\n Оригинал с IMG, pos='+str(pos)+':\n'+html_source)

                    href = html_source[pos_src_1+1:pos_src_2]
                    new_link = '<br><a '+self.editor_link_external_style+' href="'+href+'">'+href+'</a><br>'
 
                    html_source = html_source[:pos1]+' '+new_link+' '+html_source[pos2+1:]
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
                        pos = html_source.find(h_begin[i], pos)
                        pos2 = html_source.find('>', pos)
                        html_source = html_source[:pos]+'<p>'+h_span[i]+html_source[pos2+1:]

                    # pos = 0
                    html_source = html_source.replace(h_end[i], '</span></p>')            
                # print('\n С заменой H:\n'+html_source)

            # Меняем стиль маркированному списку, удаляя <ul ..> и </ul>
            if html_source.find('<li') >= 0:
                html_source = re.sub('(<li.*?>)', self.editor_li_span, html_source)
                if html_source[-len('</ul>'):] == '</ul>':
                    need_insert_p_at_end = True
                
            # Добавляем в наш редактор, предварительно обернув в div стиля нашего шрифта по-умолчанию
            html_source = note.format.editor_default_font_span.replace('<span ', '<div ') + html_source + '</div>'
            if need_insert_p_at_end:
                html_source += '</p><p>'
            print('\nИтоговый результат:\n'+html_source+'\n')
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

            if format_span in line_html[:len(format_span)+1]:                 
                # print('Форматирование уже стоит. Убираем  его..')
                # cursor.removeSelectedText()
                cursor.insertHtml(self.editor_default_font_span+text+'</span>')
                action.setChecked(False)
            else:
                # print('Форматирования нет или есть другое. Очищаем стиль выделение и ставим наш.')
                # cursor.removeSelectedText()
                cursor.insertHtml(format_span+text+'</span>')
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
            
            actions = [main_window.actionStrikethrough,    main_window.actionCode, main_window.actionMark]
            format_spans = [self.editor_strikethrough_span, self.editor_code_span,  self.editor_mark_span]
            
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
                new_pos_cur = pos_cur-1
            else:
                new_pos_cur = pos_begin_line+1
                            
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
                cursor.insertHtml(self.editor_default_font_span+text+'</span>')
                editor_h_action[h].setChecked(False)
            else:
                # print('Заголовка нет или есть другой. Удаляем форматирование и ставим новый.')
                text = cursor.selectedText()
                # cursor.removeSelectedText()
                cursor.insertHtml(self.editor_h_span[h]+text+'</span>')
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
                cursor.setPosition(pos_cur+1, QtGui.QTextCursor.KeepAnchor)
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
                
            cursor.setCharFormat(fmt)   # Устанавливаем стиль "с нуля", удаляя предыдущий

        def italic(self):
            cursor = main_window.textBrowser_Note.textCursor()
            pos_cur = cursor.position()
            if pos_cur == cursor.selectionStart():
                # Исправляем ситуацию, когда курсор, стоя в начале, не видит выделенного текста после него
                cursor.setPosition(pos_cur+1, QtGui.QTextCursor.KeepAnchor)
                fmt = cursor.charFormat()
                cursor.setPosition(pos_cur, QtGui.QTextCursor.KeepAnchor)
            else:
                fmt = cursor.charFormat()
                
            if fmt.fontItalic():
                fmt.setFontItalic(False)
            else:
                fmt.setFontItalic(True)
            cursor.setCharFormat(fmt)   # Устанавливаем стиль "с нуля", удаляя предыдущий

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
            
            cursor = main_window.textBrowser_Note.textCursor()
            # cursor.setPosition(pos)
            cur_pos = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            i = 1
            while cursor.position() > 0:
                cursor.movePosition(QtGui.QTextCursor.Up)
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                # Если не перемещаться на начало линии - зависнет на <li> и др.
                i += 1
            cursor.setPosition(cur_pos)
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
            
            mess = 'line: ' + str(self.getLineAtPosition3(cursor.position())) + \
                   '  column: ' + str(cursor.columnNumber())
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
        
        # --- End of class Format ---       

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
        # Переключаем соотстветствующее отображению действие
        # main_window.actionFast_jump_to_file_or_section.setChecked(visible)

    def is_visible(self):
        if main_window.stackedWidget.currentIndex() == 1:
            return True
        else:
            return False

    def union_concat_ident_span(self, note_source):
        # Найти и склеить все одинаковые по стилю span в строчках ( разделение по <p> и <br> ), включая
        # <span> разделенные пробелами
        # str.find(sub[, start[, end]])
        
        pos = 0
        span_end = '</span>'
        span_begin = '<span '
        str_sign_concat = span_end+span_begin
         
        while note_source.find(str_sign_concat, pos) >= 0:
            # Позиция обнаруженного сочленения двух span
            pos_concat = note_source.find(str_sign_concat, pos)
            # Ищем конец правого span
            pos_rspan_begin = pos_concat+len(span_end)
            pos_rspan_end = note_source.find('>', pos_rspan_begin+len(span_begin))+1
            # Ищем начало левого span
            pos_lspan_begin = note_source.rfind(span_begin, 0, pos_concat)
            pos_lspan_end = note_source.find('>', pos_lspan_begin)+1
            
            lspan = note_source[pos_lspan_begin: pos_lspan_end]
            rspan = note_source[pos_rspan_begin: pos_rspan_end]
            
            # print ('Найдено сочленение на позиции',pos_concat,', span-позиции:', pos_lspan_begin, '-', pos_lspan_end,
            # ', ', pos_rspan_begin, '-', pos_rspan_end)
            # print ('Результата вырезки 1: '+lspan)
            # print ('Результата вырезки 2: '+rspan)
            
            if lspan == rspan:
                # Делаем склейку двух одинаковых span
                note_source_result = note_source[:pos_concat]+note_source[pos_rspan_end:]
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
                    note_source = note_source[: pos_a_begin] + a_href + note_source[pos_a_end+len(str_a_end):]
                else:
                    # Внутренний или на местные файлы линк
                    note_source = note_source[: pos_a_begin] + '[['+a_href+']]' + note_source[pos_a_end+len(str_a_end):]
            else:
                # print ('У нас ссылка с подмененным текстом!')
                # У нас ссылка с подмененным текстом
                # [[1234|text]]
                # Обрабатывается нормально на сохранение в блоке выше, но открытие пока не обрабатывается. 
                note_source = note_source[: pos_a_begin] + '[['+a_href+'|'+a_text+']]' + note_source[pos_a_end +
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

        note_source = note_source[pos_cut1+1:pos_cut2]
        return note_source
                
    def save_note(self):
        # profiler.start('Начинаем сохранение заметки')

        filename = main_window.current_open_note_link

        print('Сохраняем файл %s' % filename)
        
        # Обновляем запись в базе
        state_db_connection.execute("UPDATE file_recs SET last_change=?  WHERE filename=?",
                                    (datetime.now(), filename) )
        state_db.commit()                        
        
        # Сохраняем текущую заметку
        tmp_str = main_window.current_open_note_link[:-len('.txt')]
        # print ('tmp_str: '+tmp_str)
        rt_suffix = '-rt'
        if tmp_str[-len(rt_suffix):] == rt_suffix:
            filename = main_window.current_open_note_link
        else:
            filename = tmp_str+rt_suffix+'.txt'
        # print ('filename: '+filename)
        # return 0
        # filename = main_window.current_open_note_link+'2'
        note_source = main_window.textBrowser_Note.toHtml()
        
        begin_of_zim_note = '''Content-Type: text/x-zim-wiki
Wiki-Format: zim 0.4
Creation-Date: 2012-09-02T11:16:31+04:00

'''
        if main_window.actionSave_also_note_HTML_source.isChecked():
            filename_html = main_window.current_open_note_link.replace('.txt', '.html')
            f = open(filename_html, "w")
            f.writelines(note_source)
            f.close()
        
        note_source = self.clear_note_html_cover(note_source)
        
        # Удаляем виртуальные начала строк
        note_source = re.sub('<p .*?>', '', note_source)
        # Удаляем последнее закрытие </p>
        
        # profiler.checkpoint('Проводим склейку соседних span')

        # Склеиваем одинаковые соседние span
        note_source = self.union_concat_ident_span(note_source)

        # Применяем вики-форматирование
        
        # profiler.checkpoint('Заменяем html-теги заголовков на вики-форматирование')
                
        # Заголовок    
        note_source = re.sub(self.format.editor_h1_span+'(.*?)</span>', '====== \\1 ======', note_source)
        note_source = re.sub(self.format.editor_h2_span+'(.*?)</span>', '===== \\1 =====', note_source)
        note_source = re.sub(self.format.editor_h3_span+'(.*?)</span>', '==== \\1 ====', note_source)         
        note_source = re.sub(self.format.editor_h4_span+'(.*?)</span>', '=== \\1 ===', note_source)
        note_source = re.sub(self.format.editor_h5_span+'(.*?)</span>', '== \\1 ==', note_source)
        note_source = re.sub(self.format.editor_h6_span+'(.*?)</span>', '= \\1 =', note_source)         

        # Подчеркнутый (выделенный)
        note_source = re.sub(self.format.editor_mark_span+'(.*?)</span>', '__\\1__', note_source)         
        
        # Код
        note_source = re.sub(self.format.editor_code_span+'(.*?)</span>', '\'\'\\1\'\'', note_source)         

        # profiler.checkpoint('Заменяем html-теги ссылок на вики-форматирование')

        # Ссылка
        # <a href="...">
        note_source = self.make_all_links_to_wiki_format(note_source)

        # profiler.checkpoint('Заменяем html-теги основной разметки на вики-форматирование')
        
        # Нумерованный список
        # 
        
        # Зачеркнутый текст
        # <span style=" font-family:'Sans'; font-size:15px; text-decoration: line-through; color:#aaaaaa;">
        # editor_strikethrough_span
        note_source = re.sub('<span [^>]*text-decoration: line-through;.*?>(.*?)</span>', '~~\\1~~', note_source)
        # Жирный
        # <span style=" font-family:'Sans'; font-size:15px; font-weight:600;">
        note_source = re.sub('<span [^>]*font-weight:600;.*?>(.*?)</span>', '**\\1**', note_source)
        # Наклонный
        # <span style=" font-family:'Sans'; font-size:15px; font-style:italic;">
        note_source = re.sub('<span [^>]*font-style:italic;.*?>(.*?)</span>', '//\\1//', note_source)
        
        # Картинка
        # <img src="/home/vyacheslav//Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png" />
        # -->
        # {{~/Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png}}
        # Закомментировал, не работает сейчас, выдает ошибку про незакрытый \U. Наверное, это в пути к картинке.
        # note_source = re.sub('<img src="'+path_to_home+'(.*?)" />', '{{~\\1}}', note_source)
        note_source = re.sub('<img src="(.*?)" />', '{{\\1}}', note_source)

        
        # Ненумерованный список
        # <ul style="..."><li style="..."><span style="..">Пункт 1</span></li></ul> 
        # note_source = re.sub('<ul .*?><li .*?>(.*?)</li></ul>', '* \\1<br />', note_source)
        note_source = re.sub('<li .*?>(.*?)</li>', '* \\1<br />', note_source)
        note_source = re.sub('<ul .*?>(.*?)</ul>', '\\1', note_source)

        # Чистим остатки
        # profiler.checkpoint('Чистим остатки html разметки')
        
        # Удаление оставшихся span
        note_source = re.sub('<span .*?>', '', note_source)
        note_source = note_source.replace('</span>', '')
        
        # Заменяем окончания на перенос строки
        note_source = note_source.replace('</p>', '\n')
        # Заменяем html переносы строк на обычные
        note_source = note_source.replace('<br />', '\n')
        
        # note_source = note_source.replace('<a name="created"></a>','')
        note_source = re.sub('<a name="(.*?)"></a>', '', note_source)

        # profiler.stop()
        
        # Добавляем начало файла как у Zim        
        note_source = begin_of_zim_note+note_source
        
        # Записываем результат преобразования исходника заметки в файл

        # f = open(filename, "w", "utf-8")
        # f.writelines(note_source)
        # f.close()

        print("We will save notes to %s" % filename)

        # Новое сохранение с использование кодировки UTF8
        fileObj = codecs.open( filename, "w", "utf-8" )
        for one_line in note_source:
            fileObj.write(one_line)
        fileObj.close()


        main_window.statusbar.showMessage('Note saved as '+filename)
        
        # TODO: Запуск перебора всех заметок и сохранения их в альтернативный каталог
        # TODO: Diff всех файлов заметок - оригиналов и сохраненных, и коррекция сохранения.
        
        # TODO: ... А если форматирование на несколько строк?
        
    def show_note_multiaction_win_button(self):
        # if main_window.textBrowser_Note.isVisible():
        if note.is_visible():
            self.show_note_multiaction_win(main_window.current_open_note_link)
        else:
            self.show_note_multiaction_win(notelist_selected_url.split('?')[1])

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

    def __init__(self):    # Note class
        self.format = self.Format()
        # Прописываем реакцию на сигналы
        # QtCore.QObject.connect(main_window.textBrowser_Note, QtCore.SIGNAL("textChanged()"), self.format.update_ui)
        main_window.textBrowser_Note.textChanged.connect(self.format.update_ui)
        # QtCore.QObject.connect(main_window.textBrowser_Note, QtCore.SIGNAL("cursorPositionChanged()"), self.format.update_ui)
        main_window.textBrowser_Note.cursorPositionChanged.connect(self.format.update_ui)
        
        # QtCore.QObject.connect(main_window.doc_source, QtCore.SIGNAL("textChanged()"), self.format.updateUI)
        # QtCore.QObject.connect(main_window.doc_source, QtCore.SIGNAL("cursorPositionChanged()"), self.format.updateUI)

        # Прописываем реакцию на действия
        main_window.actionBold.triggered.connect(self.format.bold)
        main_window.actionItalic.triggered.connect(self.format.italic)
        main_window.actionStrikethrough.triggered.connect(self.format.strikethrough)
        main_window.actionCode.triggered.connect(self.format.code)
        main_window.actionMark.triggered.connect(self.format.mark)
    
        main_window.action_ClearFormat.triggered.connect(self.format.clear_format)
        main_window.actionHeading_1.triggered.connect(self.format.h1)
        main_window.actionHeading_2.triggered.connect(self.format.h2)
        main_window.actionHeading_3.triggered.connect(self.format.h3)
        main_window.actionHeading_4.triggered.connect(self.format.h4)
        main_window.actionHeading_5.triggered.connect(self.format.h5)
        main_window.actionHeading_6.triggered.connect(self.format.h6)
        
        main_window.actionSave_note.triggered.connect(self.save_note)
        main_window.actionNote_multiaction.triggered.connect(self.show_note_multiaction_win_button)
        
        main_window.actionPaste_as_text.triggered.connect(self.paste_as_text)
    
        #Скрываем дополнительные фреймы
        main_window.frameSearchInNote.setVisible(False)


class History ():

    def add(self, type_, value):
        pass
    
    def set_active(self, filename):
        pass
    
    def setVisible(self, visible=True):
        # Переключаем соотстветствующее отображению действие
        # main_window.actionFast_jump_to_file_or_section.setChecked(visible)
        pass


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
    filter_name = '' # Фильтрация списка заметок по имени заметки
    filter_text = ''  # Фильтрация списка заметок по тексту, содержащемуся внутри заметок
    
    items = []  # Элементы списка заметок
    items_cursor_position = 0  # Положение курсора в списке элементов
    items_size = 0 # Общий объём данных в заметках из списка
        
    item = {}  # Перечень полей отдельного элемента
    item['filename'] = ''  # Путь к файлу заметки
    item['cutename'] = ''  # Красивое имя/путь заметки для отображения в списке
    item['history'] = False  # Элемент истории
    item['last_open'] = None  # Когда открывали последний раз. Больше относится к истории.
    item['size'] = None  # Размер файла заметки
 
    need_rescan = True  # Признак необходимости рескана списка заметок/файлов

    history_back_offset = 0  # Обратное смещение по списку истории
    
    note_contents_source = QtGui.QTextDocument()
    
    file_recs = []

    timer_update = QtCore.QTimer()
    update_timeout = 350  # было 350


    class DB():
        """ Основной класс работы со списками заметок, историей их использования,кешем заметок
        notelist.db          Список заметок с признаками отслеживания активности работы с ними или их изменений.
        history.db           Полная история работы с заметками, позволяем составить точное мнение об
                             самых используемых заметках как за последний период, так и в целом.
                             Если заметка была удалена из списка, а затем создана (вставлена) вновь, то у неё
                             потеряется вся история предыдущей работы с ней. При переименовании и переносе такого
                             происходить не будет.
        note_txt_cache.db    Кэш для быстрого поиска по содержимому.
        note_html_cache.db   Кэш для быстрого открытия заметок.
        
        notelist.db
            note_id
            filename            text
            size                integer
            modification_time   integer         # last_change
            access_time         integer         # last_open

            cute_name           text
            parent_id           integer
            subnotes_count      integer
            subnotes_size       integer
            current_position    integer

        history.db
            note_id
            changed     datetime
            opened      datetime
            
        note_txt_cache.db
            filename
            txt_source
        
        note_html_cache.db
            filename
            html_source
        
        сравнить в скорости с объединенной базой кэша
        note_cache.db
            filename
            txt_source
            html_source
        
        """
        
        def purge_orphaned_cache(self):
            # Удаляем кэш файлов, которых уже нет. Например, были удалены или переименованы в другой программе.
            pass
        
        def total_update_cache(self):
            # Полное обновление кэша, например, при первом запуске программы с уже имеющейся базой заметок
            pass
        
        def save_note_cache_html(self, filename, html_source):
            pass
        
        def save_note_cache_txt(self, filename, txt_source):
            pass
        
        def get_note_cache_html(self, filename):
            # Получаем кэш заметки. Если его нет - возвращаем None.
            
            return None
        
        def get_note_cache_txt(self, filename):
            # Получаем кэш заметки. Если его нет - возвращаем None.
            
            return None
        
        #def initial_db(self):
    
        #    # Дерево подразделов в файлах заметок
    
        #    # Списки меток в файлах заметок
            
        #    # Списки задач в файлах заметок
    

        def __init__(self):   # class DB
            pass

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
            self.update()
            # Устанавливаем фокус на поля фильтров ввода
            # При любом раскладе выделяем весь текст в поле имени и ставим на него фокус            
            main_window.lineNotelist_Filter.setFocus()
            main_window.lineNotelist_Filter.selectAll()
            
            ## Если обнаружен текст в поле поиска по содержимому - переставляем фокус в него
            #if main_window.lineEdit_Filter_Note_Text.text() != '':
            #    main_window.lineEdit_Filter_Note_Text.setFocus()
            #    main_window.lineEdit_Filter_Note_Text.selectAll()

    def update(self):
        # Обновляем список заметок 
        self.rescan_files_in_notes_path()

    def get_and_display_filters(self):
        # Получаем текущий фильтр для списка заметок

        # Делим фильтр заметок на фильтр имени и фильтр текста внутри
        notelist_filter = main_window.lineNotelist_Filter.text()
        if ' ' not in notelist_filter:
            self.filter_text = ''
            self.filter_name = notelist_filter
        else:
            # Первое слово до пробела - имя. Остальные - текст.
            filter_words = notelist_filter.split(' ')
            self.filter_name = filter_words[0]
            self.filter_text = ' '.join(filter_words[1:])
        
        if self.filter_text or self.filter_name:
            # Отображаем в интерфейсе полученные указания по фильтрам
            if self.filter_name:
                description_filter_name = ('Name contains <b>"%s"</b>' % self.filter_name)
            else:
                description_filter_name = 'Any name'
            if self.filter_text:
                description_filter_text = ('text contains <b>"%s"</b>' % self.filter_text.replace(' ', '&nbsp;') )
            else:
                description_filter_text = 'any text contains'

            main_window.label_DisplayFilters.setText(description_filter_name + ' and '+ description_filter_text)
        else:
            #main_window.label_DisplayFilters.setText('Example: "proj ninja"')
            main_window.label_DisplayFilters.setText('<html><head></head><body>Example: <b>proj ninja</b></body></html>')
                
        # print('Filters: notelist.filter_name=%s, notelist.filter_text=%s' % (self.filter_name, self.filter_text) )



    def make_cute_name(self, filename):
        # Создаем симпатичное длинное имя заметки из имени файла
        # 1. Убираем из пути каталог до заметок
        cute_filename = filename.replace(path_to_notes + os.path.sep, '')
        # 2. Убираем расширение файла
        # 2.1 Разрезаем на отдельные слова - папки и имя файла
        list_of_words = cute_filename.split(os.path.sep)
        # 2.2 В последнем слове отрезаем все после точки, если она есть
        if '.' in list_of_words[-1]:
            list_of_words[-1] = list_of_words[-1].rpartition('.')[0]
        #cute_filename = cute_filename.rpartition('.txt')[0]
        # 3. Соединяем обратно, вместо разделителя пути используя двоеточие с пробелом после
        cute_filename = ': '.join(list_of_words)
        #cute_filename = cute_filename.replace(os.path.sep, ': ')         
        # 4. Меняем нижнее подчеркивание на пробелы
        cute_filename = cute_filename.replace('_', ' ')            
        return cute_filename


    def file_in_history(self, filename):
        # Проверяем - есть ли файл в списке истории
        state_db_connection.execute("SELECT * FROM file_recs WHERE filename=?", (filename,) )
        existed_rec = state_db_connection.fetchall()
        if len(existed_rec) > 0:
            return True
        else:
            return False


    def rescan_files_in_notes_path(self):
        # Обновляем список заметок в зависимости от фильтров
        self.get_and_display_filters()
        
        # Как собирать список файлов:
        # http://stackoverflow.com/questions/1274506/how-can-i-create-a-list-of-files-in-the-current-directory-and-its-
        # subdirectories
        # http://stackoverflow.com/questions/2225564/get-a-filtered-list-of-files-in-a-directory

        # rec = [ filename, cute_name, parent_id, subnotes_count, last_change, last_open, count_opens ]
        # file_recs = [ rec1, rec2, rec3, .. ]
        # При полном рескане очищаем полностью список файлов

        #filter_note_name = main_window.lineNotelist_Filter.text()
        
        #notelist.file_recs = []
        self.file_recs = []
        
        # Обнуляем внутренний список элементов
        self.items = []
        self.items_size = 0

        global notelist_selected_url
        


        html_string = '<p id=history_date>История обращений к заметкам</p>'

        file_recs_rows = state_db_connection.execute("SELECT * FROM file_recs WHERE last_open NOT NULL ORDER BY last_open DESC")

        for row in file_recs_rows:
            rec_filename, rec_cute_name, rec_parent_id, rec_subnotes_count, rec_last_change, rec_last_open, rec_count_opens, rec_current_position = row
            # Проверка файла из истории на существование 
            if not os.path.isfile(rec_filename):
                # Файл не существует или это каталог, а не файл.
                # Удаляем из истории
                state_db_connection.execute("DELETE FROM file_recs WHERE filename=?", (rec_filename,) )
                continue  # Переходим на следующий виток цикла

            # Продолжаем с элементом истории, у которого есть файл
            rec_item = self.item.copy()  # Делаем копию образца словаря
            rec_item['filename'] = rec_filename
            rec_item['cutename'] = self.make_cute_name(rec_filename)
            rec_item['history'] = True
            rec_item['last_open'] = rec_last_open
            rec_item['size'] = os.stat(rec_filename).st_size
            self.items_size += rec_item['size']  # Добавляем в общий размер
            # Добавляем элемент во внутренний список элементов
            self.items.append(rec_item)

            html_string += '<p>%s <span id=history_date>%s</span></p>' % (self.make_cute_name(rec_filename), rec_last_open)


        html_string += '<p id=history_date>Список всех заметок</p>'

        html_string += '<div id=notelist>'
        
        active_link = main_window.current_open_note_link
        
        asps = []
        notes_count = 0
        notes_count_all = 0
        notes_size = 0
        notes_size_all = 0
        i = 0
        # print('Обновляем список файлов. Найдено:')

        for root, dirs, files in os.walk(path_to_notes):
            for file in files:
                if file.endswith('.txt'):
                    # main_window.statusbar.showMessage('Rescan notes: '+str(i+1)+' of ?')
                    # if root[-1] != '/':
                    #    filename = root + '/' + file
                    # else:
                    #    filename = root + file
                    filename = os.path.join(root, file)
                    #print('DEBUG: ROOT="%s" FILE="=%s"' % (root, file) )
                    #print('DEBUG: os.path.join(root, file)=%s' % filename)
                    size = os.stat(filename).st_size
                    
                    access_time = os.stat(filename).st_atime  # time of most recent access.
                    modification_time = os.stat(filename).st_mtime  # time of most recent content modification
                    # print('filename: '+filename, 'size: '+str(size), 'access_time: %s' % time.ctime(access_time),
                    #  'modification_time: %s' % time.ctime(modification_time) )

                    # Продолжаем с найденным файловым элементом
                    # Проверяем - нет ли этого элемента уже добавленного из истории
                    if self.file_in_history(filename):
                        continue # Переходим на следующий виток цикла

                    cute_filename = self.make_cute_name(filename)

                    # Анализ актуальности кеша, обновление базы списка заметок

                    notes_count_all += 1
                    notes_size_all += size
                    lines = ''
                    
                    # Проверяем на неудовлетворение фильтру
                    if self.filter_name != '' and self.filter_name.lower() not in cute_filename.lower():
                        continue

                    # Проверяем на неудовлетворение фильтру по тексту содержимого заметки
                    #if main_window.lineEdit_Filter_Note_Text.text() != '':
                    if self.filter_text != '':
                        # Надо загрузить заметку и провести поиск в ней на предмет содержимого
                        fileObj = codecs.open( filename, "r", "utf-8" )
                        lines = fileObj.read()
                        fileObj.close()
                        #if main_window.lineEdit_Filter_Note_Text.text().lower() not in lines.lower():
                        if self.filter_text.lower() not in lines.lower():
                            continue

                    notes_count += 1
                    notes_size += size
                    asps.append(file)

                    # rec = [ filename, cute_name, parent_id, subnotes_count, last_change, last_open, count_opens ]
                    # file_recs = [ rec1, rec2, rec3, .. ]
                    # При полном рескане очищаем полностью список файлов

                    # Вынимаем текстовый контент заметки и добавляем в массив

                    #notelist.file_recs.append([filename, cute_filename, lines])
                    self.file_recs.append([filename, cute_filename, lines])

                    # Добавляем в список элементов
                    rec_item = self.item.copy()  # Делаем копию образца словаря
                    rec_item['filename'] = filename
                    rec_item['cutename'] = self.make_cute_name(filename)
                    rec_item['size'] = size
                    self.items_size += rec_item['size']  # Добавляем в общий размер
                    # Добавляем элемент во внутренний список элементов
                    self.items.append(rec_item)



                    # Устанавливаем картинку - заметка с курсором, или без него
                    if notelist_selected_position == i:
                        # Текущая позиция - должна быть с курсором
                        img_src = 'resources/icons/notelist/arrow130_h11.png'
                        notelist_selected_url = 'note?'+filename
                    else:
                        if filename == active_link:
                            img_src = 'resources/icons/notelist/g3-g1.png'
                        else:
                            img_src = 'resources/icons/notelist/g3.png'

                    if filename == active_link:
                        line_style = ' id="current_note" '
                    else:
                        line_style = ' id="notelist"'

                    if self.filter_name != '':
                        # Делаем подсветку текста из фильтра в списке заметки
                        cute_filename = re.sub('('+self.filter_name+')', '<span id="highlight">'+'\\1</span>',
                                               cute_filename, flags=re.I)

                    # html_string += '<p><a href="'+filename+'">'+cute_filename+'</a></p>'
                    # Format: multiaction / note :|: note_filename
                    '''html_string += '<p'+line_style+'><a href="note?'+filename+'"><img src="'+img_src+'">&nbsp;' + \
                                   cute_filename+'</a>' + '&nbsp;&nbsp;<a href="contents?'+filename + \
                                   '"><img src="resources/icons/notelist/list41-2-4.png"></a>' + \
                                   '&nbsp;&nbsp;<a href="multiaction?'+filename + \
                                   '"><img src="resources/icons/notelist/document62-3.png"></a>' + \
                                   '&nbsp;&nbsp;<font id=filesize>'+hbytes(size)+'</font>' + '</p>'
                                   '''
                    html_string += '<p'+line_style+'><a href="note?'+filename+'"><img src="'+img_src+'">&nbsp;' + \
                                   cute_filename+'</a>' + '&nbsp;&nbsp;<font id=filesize>'+hbytes(size)+'</font>' + \
                                   '&nbsp;&nbsp;&nbsp;&nbsp; <a href="multiaction?'+filename + \
                                   '"><img src="resources/icons/notelist/document62-3.png"></a> </p>'

                    i += 1

                    # Если надо, добавляем ссылки на позиции вхождения текста в заметке
                    #if main_window.lineEdit_Filter_Note_Text.text() != '':
                    #    filter_note_text = main_window.lineEdit_Filter_Note_Text.text()
                    if self.filter_text != '':
                        filter_note_text = self.filter_text
                        founded_i = 0
                        # print('Ищем текст "'+filter_note_text+'" в строчках внутри заметки')
                        line_i = 1
                        for line in lines.split('\n'):
                            pos = line.lower().find(filter_note_text.lower())
                            if pos >= 0:
                            # if filter_note_text.lower() in line.lower():
                                # print('Нашли вхождение в строку '+str(line_i)+' - '+filter_note_text)
                                # Нашли вхождение. Подсвечиваем и добавляем к выводу в Notelist
                                founded_i += 1
                                line = re.sub('('+filter_note_text+')', '<span id="highlight">'+'\\1</span>', line,
                                              flags=re.I)
                                html_string += '<p id=founded_text_in_note>&nbsp;&nbsp;&nbsp;&nbsp;<small>' + str(line_i) + \
                                               ':</small>&nbsp;&nbsp;<a href="note?' + \
                                               filename+'?'+str(founded_i)+'">'+line+'</a></p>'
                                # <ul id=founded_text_in_note>
                            line_i += 1  

        main_window.statusbar.showMessage('Found ' + str(notes_count_all)+' notes ('+hbytes(notes_size_all) + ') at ' + path_to_notes +
                                            ', showed ' + str(notes_count)+' notes ('+hbytes(notes_size)+') in list.' )

                
        html_string = '<html>%s<body id=notelist>%s</body></html>' % (Theme.html_theme_head, html_string, )
        main_window.notelist_source.setHtml(html_string)
        main_window.textBrowser_Listnotes.setDocument(main_window.notelist_source)
        notelist.set_visible()

    def link_action(self, url):
        # Обрабатываем клик по линку в списке заметок
        # Определяем - клик перехда на заметку или на мультидействие по ней
        # Format: multiaction / note :|: note_filename
        link_attributes = url.toString().split('?')
        link_type = link_attributes[0] 
        link_filename = link_attributes[1]
        founded_i = 0
        if len(link_attributes) > 2:
            founded_i = link_attributes[2]
        if link_type == 'note':
            main_window.open_file_in_editor(link_filename, founded_i)
        if link_type == 'multiaction':
            note.show_note_multiaction_win(link_filename)

    def open_selected_url(self):
        print('DEBUG: open_selected_url("notelist_selected_url=%s")' % notelist_selected_url)
        link_type, link_filename = notelist_selected_url.split('?')
        if link_type == 'note':
            main_window.open_file_in_editor(link_filename)
        if link_type == 'multiaction':
            note.show_note_multiaction_win(link_filename)
    
    '''
    def switch_show_note_content(self)
    :
        if main_window.textBrowser_NoteContents.isVisible():
            # Скрываем панель содержания, включаем показ заметки
            main_window.textBrowser_NoteContents.setVisible(False)
            #main_window.textBrowser_Note.setVisible(True)
            main_window.frame_Note.setVisible(True)
            #main_window.actionShow_note_contents.setChecked(False)
        else:
            # Показывам панель содержания, выключаем показ заметки
            self.make_note_contents()  # Обновляем html исходник содержание
            main_window.textBrowser_NoteContents.setVisible(True)
            #main_window.textBrowser_Note.setVisible(False)
            main_window.frame_Note.setVisible(False)
            #main_window.actionShow_note_contents.setChecked(True)
    '''

    def __init__(self):
        # QtCore.QObject.connect(main_window.textBrowser_Listnotes, QtCore.SIGNAL("anchorClicked (const QUrl&)"),
                               # self.link_action)
        main_window.textBrowser_Listnotes.anchorClicked.connect(self.link_action)
        # QtCore.QObject.connect(main_window.lineNotelist_Filter, QtCore.SIGNAL("returnPressed ()"),
                               # self.open_selected_url)
        main_window.lineNotelist_Filter.returnPressed.connect(self.open_selected_url)
        
        # QtCore.QObject.connect(main_window.textBrowser_Listnotes, QtCore.SIGNAL("anchorClicked (const QUrl&)"),
        # self.link_action)
        # keyPressed
  
        main_window.actionFast_jump_to_file_or_section.triggered.connect(self.action_triggered)
        
        # QtCore.QObject.connect(main_window.lineEdit_Filter_Note_Text, QtCore.SIGNAL("textChanged( const QString& )"),
                               # main_window.filter_note_text_changed)
        #main_window.lineEdit_Filter_Note_Text.textChanged.connect(main_window.filter_note_text_changed)
        
        # QtCore.QObject.connect(main_window.lineEdit_Filter_Note_Text, QtCore.SIGNAL("returnPressed ()"),
        # main_window.checkBox_Filter_Note_Content_Text_switch_state)

        # self.timer_update = QtCore.QTimer()
        # self.timer_update.setInterval(self.update_timeout)
        self.timer_update.setSingleShot(True)
        
        # QtCore.QObject.connect(self.timer_update, QtCore.SIGNAL("timeout ()"), self.update)
        self.timer_update.timeout.connect(self.update)
        
        # Скрываем дополнительные фреймы
        # main_window.frameNotelist_Filter.setVisible(False)
                
        self.db = self.DB()


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
        if main_window.stackedWidget.currentIndex()==2:
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
        while cursor.position()>0:
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
        note_source = '''Content-Type: text/x-zim-wiki
Wiki-Format: zim 0.4
Creation-Date: 2012-09-02T11:16:31+04:00

'''+'====== '+notename+''' ======


'''

        f = open(filename, "w")
        f.writelines(note_source)
        f.close()

    def add_note_nearly(self):
        # Создаем новый файл рядом с указанным, с заданным именем
        new_note_name = self.lineEdit.text()
        new_filename = new_note_name.replace(' ', '_')+'.txt'
        note_path = self.labelNoteFileName.text()
        #note_path = note_path.rpartition('/')[0]
        note_path = note_path.rpartition(os.path.sep)[0]
        #full_filename = note_path+'/'+new_filename
        full_filename = note_path+os.path.sep+new_filename
        self.make_new_note_file(full_filename, new_note_name)
        main_window.open_file_in_editor(full_filename)
        main_window.statusbar.showMessage('New note created: '+full_filename)
        self.close()

    def add_child_note(self):
        # Создаем новый файл под указанной заметкой, с заданным именем
        new_note_name = self.lineEdit.text()
        new_filename = new_note_name.replace(' ', '_')+'.txt'
        note_path = self.labelNoteFileName.text()
        note_path = note_path.rpartition('.txt')[0]
        #full_filename = note_path+'/'+new_filename
        full_filename = note_path+os.path.sep+new_filename
        if not os.path.exists(note_path):
            # Создаем каталог нужный
            os.makedirs(note_path)
        self.make_new_note_file(full_filename, new_note_name)
        main_window.open_file_in_editor(full_filename)
        main_window.statusbar.showMessage('New note created: '+full_filename)
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
            self.insertHtml(note.format.adaptate_alien_html_styles(source_html))
            

# if __name__ == "__main__":
app = QtWidgets.QApplication(sys.argv)
# myapp = MyForm()

# theme = Theme()

myFilter = MyEventFilter()
main_window = Window()

# Переопределяем класс редактора заметок
new_textBrowser = MyTextBrowser(main_window.textBrowser_Note)
main_window.textBrowser_Note.setVisible(False)  # Скрываем старый класс редактора заметки
main_window.textBrowser_Note = new_textBrowser 
main_window.horizontalLayout_Note.layout().addWidget(main_window.textBrowser_Note)
main_window.horizontalLayout_Note.layout().addWidget(main_window.frame_NoteMinimap)


note = Note()
notelist = Notelist()
history = History()

table_of_note_contents = Table_of_note_contents()
calculator_win = calculator.CalculatorWindow()

preferences_win = PreferencesWindow()
notemultiaction_win = NoteMultiactionWindow()

app.installEventFilter(myFilter)

# history.setVisible()
notelist.set_visible()  # По-умолчанию встречаем пользователя списком заметок

main_window.show()

main_window.statusbar.showMessage('Application initializing..')
# self.open_file_in_editor(path_to_notes + 'компьютерное.txt')
main_window.initial_db()
main_window.renew_history_list('')
notelist.update()

sys.exit(app.exec_())


