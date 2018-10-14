from PyQt5 import QtGui


class Table_of_note_contents():
    """ Класс таблицы содержания заметки. """

    rn_app = None

    def initial_setup(self):
        self.rn_app.main_window.actionShow_note_contents.triggered.connect(self.action_triggered)

    def __init__(self, rn_app):
        self.rn_app = rn_app

    def setVisible(self, visible=True):
        if visible:
            # print ('Make visible')
            # Отображаем все виджеты, связанные содержанием заметки
            self.rn_app.main_window.stackedWidget.setCurrentIndex(2)
            # Скрываем конкурирующие виджеты
            self.rn_app.note.set_visible(False)
            # table_of_note_contents.setVisible(False)
            self.rn_app.notelist.set_visible(False)

        # Переключаем все действия, связанные с содержанием
        # note_actions = [ main_window.actionNote_multiaction, main_window.actionShow_note_contents ]
        # for action in note_actions:
        #    action.setEnabled(visible)
        # Переключаем соотстветствующее отображению действие
        self.rn_app.main_window.actionShow_note_contents.setChecked(visible)

    def isVisible(self):
        if self.rn_app.main_window.stackedWidget.currentIndex() == 2:
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