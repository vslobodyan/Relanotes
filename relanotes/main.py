# -*- coding: utf-8 -*-

# __author__ = 'vyacheslav'
# __version__ = '0.06'

import sys
from PyQt5 import QtWidgets

# from relanotes.routines import *


"""
Список заметок и статус работы с ними - реализовано в классе Notelist, переменная file_recs
rec = [ id, filename, cute_name, parent_id, subnotes_count, size, favorite, hidden, 
        last_change, last_open, count_opens, opened ]

file_recs = [ rec1, rec2, rec3, .. ]
file_recs = []
"""



def main():
    """Основная функция запуска главного окна программы, инициализации настроек приложения и т.д."""

    print('== 0000')

    app = QtWidgets.QApplication(sys.argv)

    print('== 000')

    from relanotes.rn import rn_app

    print('== 11')

    rn_app.settings.initial_setup()

    print('== 12')

    # Включаем логирование
    rn_app.loggers.root = rn_app.loggers.create(rn_app.settings.log_level, rn_app.settings.logfile)

    print('loggers.root: ', rn_app.loggers.root, type(rn_app.loggers.root))

    print('== 6')

    rn_app.main_window.initial_setup()


    print('== 101')

    from relanotes.event_filter import MyEventFilter

    print('== 102')

    myFilter = MyEventFilter()

    print('== 103')

    app.installEventFilter(myFilter)


    print('== 7')

    rn_app.main_window.redefine_textbrowser_class()

    # # Переопределяем класс редактора заметок
    # new_textBrowser = MyTextBrowser(rn_app.main_window.textBrowser_Note)
    # rn_app.main_window.textBrowser_Note.setVisible(False)  # Скрываем старый класс редактора заметки
    # rn_app.main_window.textBrowser_Note = new_textBrowser
    # rn_app.main_window.horizontalLayout_Note.layout().addWidget(rn_app.main_window.textBrowser_Note)
    # rn_app.main_window.horizontalLayout_Note.layout().addWidget(rn_app.main_window.frame_NoteMinimap)

    print('== 8')

    rn_app.note.window_triggers_connect()
    print('== 9')

    rn_app.notelist.initial_setup()
    print('== 10')

    rn_app.table_of_note_contents.initial_setup()

    print('== 11')

    # Запускаем инициализирующую проверку пути к заметкам
    rn_app.main_window.check_path_to_notes_or_select_new()

    print('== 12')

    rn_app.tests.initial_setup()

    print('== 13')

    # history.setVisible()
    rn_app.notelist.set_visible()  # По-умолчанию встречаем пользователя списком заметок

    print('== 14')

    rn_app.main_window.show()

    rn_app.main_window.statusbar.showMessage('Application initializing..')
    # self.open_file_in_editor(path_to_notes + 'компьютерное.txt')

    print('== 15')

    rn_app.main_window.initial_db()

    print('== 16')

    rn_app.notelist.update()

    print('== 17')

    rn_app.main_window.renew_history_lists('')
    # Делаем инициализацию текста в поле фильтра списка заметок

    print('== 18')
    rn_app.main_window.notelist_filter_changed('')

    print('loggers.root: ', rn_app.loggers.root, type(rn_app.loggers.root))


    print('== 19')

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

