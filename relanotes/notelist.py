import codecs
import os
import re
from datetime import datetime, date, timedelta

from PyQt5 import QtGui, QtCore

# from relanotes.relanotes import main_window, note, table_of_note_contents, notelist, app_settings
from relanotes.theme import Theme
from relanotes.routines import hbytes


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

    note_contents_source = '' # QtGui.QTextDocument()

    # file_recs = []

    timer_update = '' # QtCore.QTimer()
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


        # print('Делаем исходник для списка заметок')
        #root_logger.info('\nДелаем исходник для списка заметок:')
        # print('=' * 40)
        #root_logger.info('=' * 40)
        # print(html_string)
        #root_logger.info(html_string)
        # print('=' * 40)
        #root_logger.info('=' * 40)
        #root_logger.warning
        main_window.notelist_source.setHtml(html_string)
        # print('Делаем документ для списка заметок')
        main_window.textBrowser_Listnotes.setDocument(main_window.notelist_source)
        # print('Закончили со списком заметок')
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
        self.note_contents_source = QtGui.QTextDocument()
        self.timer_update = QtCore.QTimer()
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