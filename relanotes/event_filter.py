# from relanotes.relanotes import main_window, text_format, notelist
# from relanotes.main_window import Window
from PyQt5 import QtCore

from relanotes.note import Note
# from relanotes.rn_app import main_window, text_format, notelist
# from relanotes.main import main_window, text_format, notelist

from relanotes.rn import rn_app

main_window = rn_app.main_window
text_format = rn_app.text_format
notelist = rn_app.notelist


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