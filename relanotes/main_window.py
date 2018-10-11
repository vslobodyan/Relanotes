import codecs
import os
from datetime import datetime

from PyQt5 import QtWidgets, QtGui, QtCore

from relanotes.qtdesign_ui.main_window import Ui_MainWindow
# from relanotes.relanotes import app_settings, notelist, main_window, clear_history_win, calculator_win, preferences_win, \
#     note, root_logger, text_format
from relanotes.routines import give_correct_path_under_win_and_other, get_correct_filename_from_url


class Window(QtWidgets.QMainWindow, Ui_MainWindow):
    # Главное окно приложения.
    doc_source = '' # QtGui.QTextDocument()
    sidebar_source = '' # QtGui.QTextDocument()
    notelist_source = '' # QtGui.QTextDocument()
    current_open_note_link = ''    # Ссылка на текущую открытую заметку
    timer_lock_ui = '' # QtCore.QTimer()
    lock_ui_timeout = 10000
    locked = False
    timer_window_minimize = '' # QtCore.QTimer()
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

    def open_logfile_in_text_editor(self):
        # Открываем лог-файл в дефолтовой программе среды исполнения.
        # os.startfile(app_settings.logfile)
        import webbrowser
        webbrowser.open(app_settings.logfile)

    def open_notes(self):
        # Открываем другой каталог с заметками
        self.check_path_to_notes_or_select_new(select_new=True)
        notelist.update()

    def reopen_note(self):
        # Перезагружаем заметку из её файла
        if self.current_open_note_link:
            self.open_file_in_editor(self.current_open_note_link, reload=True)

    def __init__(self, parent=None):
        self.doc_source = QtGui.QTextDocument()
        self.sidebar_source = QtGui.QTextDocument()
        self.notelist_source = QtGui.QTextDocument()
        self.timer_lock_ui = QtCore.QTimer()
        self.timer_window_minimize = QtCore.QTimer()

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

        self.actionOpen_logfile_in_text_editor.triggered.connect(self.open_logfile_in_text_editor)


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

        # Новая функция получения стилей перебором html-исходника текста редактора
        html_with_styles = self.textBrowser_TestNote.toHtml()

        def next_span_style(pos, str='', skip_next=False, log=True, comment=''):
            'Ищем следующий span и получаем его стиль'
            span_begin = '<span style="'
            style_end = '">'
            style = ''
            # Ищем span
            begin_pos = str.find(span_begin, pos) + len(span_begin)
            # Ищем завершение его стиля
            end_pos = str.find(style_end, begin_pos)
            # Берем его стиль
            style = str[begin_pos:end_pos]
            # Возвращаем найденную позицию span, его стиль и позицию окончания стиля
            skip_next_notify = ''
            if skip_next:
                # Надо проскочить следующий стиль
                useless, end_pos = next_span_style(end_pos, str, log=False)
                skip_next_notify = ' (skip_next)'
            if log:
                root_logger.info('Извлечение стиля %s из span%s,  pos %s-%s, "%s"' % (comment, skip_next_notify, begin_pos, end_pos, style))
            else:
                pass
                # Надо вынуть текст из пропускаемого тега
                #text_end = str.find("<", end_pos)
                #root_logger.info('Текст пропускаемого тега "%s"' % str[end_pos:text_end])

            return style, end_pos

        # Ищем первую значащую строку
        style_default, next_pos = next_span_style(0, html_with_styles, comment='Default')

        style_h1, next_pos = next_span_style(next_pos, html_with_styles, skip_next=True, comment='H1')
        style_h2, next_pos = next_span_style(next_pos, html_with_styles, skip_next=True, comment='H2')
        style_h3, next_pos = next_span_style(next_pos, html_with_styles, skip_next=True, comment='H3')
        style_h4, next_pos = next_span_style(next_pos, html_with_styles, skip_next=True, comment='H4')
        style_h5, next_pos = next_span_style(next_pos, html_with_styles, skip_next=True, comment='H5')
        style_h6, next_pos = next_span_style(next_pos, html_with_styles, skip_next=True, comment='H6')

        style, next_pos = next_span_style(next_pos, html_with_styles, comment='<br>', log=False)
        style_code, next_pos = next_span_style(next_pos, html_with_styles, skip_next=True, comment='Code')
        style, next_pos = next_span_style(next_pos, html_with_styles, comment='<br>', log=False)
        style_strike, next_pos = next_span_style(next_pos, html_with_styles, comment='Strike')
        style, next_pos = next_span_style(next_pos, html_with_styles, comment='<br>', log=False)
        style_mark, next_pos = next_span_style(next_pos, html_with_styles, skip_next=True, comment='Mark')
        style, next_pos = next_span_style(next_pos, html_with_styles, comment='<br>', log=False)
        style_link, next_pos = next_span_style(next_pos, html_with_styles, comment='Link')

        span_template = '<span style="%s">'
        text_format.editor_default_font_span = span_template % style_default
        text_format.editor_h1_span = span_template % style_h1
        text_format.editor_h2_span = span_template % style_h2
        text_format.editor_h3_span = span_template % style_h3
        text_format.editor_h4_span = span_template % style_h4
        text_format.editor_h5_span = span_template % style_h5
        text_format.editor_h6_span = span_template % style_h6

        text_format.editor_code_span = span_template % style_code
        text_format.editor_strikethrough_span = span_template % style_strike
        text_format.editor_mark_span = span_template % style_mark
        text_format.editor_link_external_style = style_link #move_down_and_get_span(test_cursor, only_style=True)


        # Новая функция получения стилей через перемещение курсора
        # test_cursor = self.textBrowser_TestNote.textCursor()
        # test_cursor.movePosition(QtGui.QTextCursor.Start)
        #
        # def move_down_and_get_span(cursor, only_style=False):
        #     cursor.movePosition(QtGui.QTextCursor.Down)
        #     cursor.movePosition(QtGui.QTextCursor.StartOfLine)
        #     return note.get_span_under_cursor(test_cursor, only_style)
        #
        # text_format.editor_default_font_span = note.get_span_under_cursor(test_cursor)
        # text_format.editor_h1_span = move_down_and_get_span(test_cursor)
        # text_format.editor_h2_span = move_down_and_get_span(test_cursor)
        # text_format.editor_h3_span = move_down_and_get_span(test_cursor)
        # text_format.editor_h4_span = move_down_and_get_span(test_cursor)
        # text_format.editor_h5_span = move_down_and_get_span(test_cursor)
        # text_format.editor_h6_span = move_down_and_get_span(test_cursor)


        text_format.editor_h_span = ['0-empty', text_format.editor_h1_span,
                                    text_format.editor_h2_span,
                                    text_format.editor_h3_span,
                                    text_format.editor_h4_span,
                                    text_format.editor_h5_span,
                                    text_format.editor_h6_span]

        # text_format.editor_code_span = move_down_and_get_span(test_cursor)
        # text_format.editor_strikethrough_span = move_down_and_get_span(test_cursor)
        # text_format.editor_mark_span = move_down_and_get_span(test_cursor)
        # text_format.editor_link_external_style = move_down_and_get_span(test_cursor, only_style=True)



        root_logger.info('\nИсходник для получения стилей:')
        root_logger.info('=' * 40)
        root_logger.info(self.textBrowser_TestNote.toHtml())
        # print('Получили для адаптации при вставке следующий html:\n' + html_source + '\n')
        root_logger.info('=' * 40)


        # root_logger.info('\nПолучены следующие дефолтовые стили:')
        # root_logger.info('text_format.editor_h_span: %s' % text_format.editor_h_span)
        # root_logger.info('text_format.editor_code_span: %s' % text_format.editor_code_span)
        # root_logger.info('text_format.editor_strikethrough_span: %s' % text_format.editor_strikethrough_span)
        # root_logger.info('text_format.editor_mark_span: %s' % text_format.editor_mark_span)
        # root_logger.info('text_format.editor_link_external_style: %s' % text_format.editor_link_external_style)




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

        root_logger.info('\nИсходник загружаемой заметки из файла %s:' % filename)
        root_logger.info('=' * 40)
        root_logger.info(self.textBrowser_Note.toHtml())
        # print('Получили для адаптации при вставке следующий html:\n' + html_source + '\n')
        root_logger.info('=' * 40)


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
                # print()
                snippet_name = snippet_lines[0]
                snippet_text = '\n'.join(snippet_lines[1:])
                if not snippet_name:
                    continue
                # print('Заголовок: %s' % snippet_name)
                # print('Текст: %s' % snippet_text)

                # exitAction = QAction(QIcon('exit.png'), 'snippet_name', self)
                # exitAction.setShortcut('Ctrl+Q')
                # exitAction.setStatusTip('Exit application')
                # exitAction.triggered.connect(qApp.quit)

                snippet_ndx += 1  # Увеличиваем индекс текущего сниппета
                # print('snippet_ndx: %s' % snippet_ndx)
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