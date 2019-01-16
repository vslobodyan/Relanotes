#!/usr/bin/python3
# -*- coding: utf-8 -*-

#from PyQt4 import QtCore, QtGui
#from PyQt4.QtCore import *
#from PyQt4.QtGui import *

from PyQt5 import QtWidgets
# from PyQt5.QtCore import *
# from PyQt5.QtGui import *

from relacalc.qtdesign_ui import calculator_window


class CalculatorWindow(QtWidgets.QDialog, calculator_window.Ui_Dialog):  # src.ui.
    rn_app = None

    def __init__(self, rn_app=None, parent=None):
        self.rn_app = rn_app

        QtWidgets.QDialog.__init__(self, parent)
        self.setupUi(self)

        # self.connect(self.lineEdit, SIGNAL("textEdited ( const QString& )"), self.update_ui)
        self.lineEdit.textEdited.connect(self.update_ui)
        # self.connect(self.lineEdit, SIGNAL("returnPressed()"), self.add_to_history)
        self.lineEdit.returnPressed.connect(self.add_to_history)
        # self.connect(self.labelClearHistory, SIGNAL("linkActivated( const QString& )"), self.clear_history)
        self.labelClearHistory.linkActivated.connect(self.clear_history)
        
        self.buttonAdd_to_note.clicked.connect(self.add_result_to_note)
        self.clear_result_field()
        self.lineEdit.setFocus()

    def clear_result_field(self):
        self.labelResult.setText('0')
        self.labelFormula.setText('')


    def purge_eval_text(self, text):
        text = text.replace(' ', '')
        return text

    def update_ui(self, text):
        try:
            #text = unicode(self.lineEdit.toPlainText())
            # text = self.lineEdit.text()
            # text = self.lineEdit.text()
            print('We have input text: "%s"' % text)
            tmp_text = ''
            # Чистим текст от букв
            for symbol in text:
                if not symbol.isalpha():
                    tmp_text += symbol
            # Табуляции и переносы строк меняем на +
            tmp_text = tmp_text.replace('\t', '+')
            tmp_text = tmp_text.replace('\n', '+')
            # Удаляем пустышки
            what_delete = []
            # what_delete = ['+, ', ]
            for one in what_delete:
                tmp_text = tmp_text.replace(one, '')
            print('tmp_text before final cornering cleaning: "%s"' % tmp_text)
            # Обрезаем с обоих краев лишние символы, которые не цифры. Формула должна начинаться и заканчиваться цифрой.
            first_digit = -1
            last_digit = -1
            pos = -1
            # Ищем последнюю цифру
            for symbol in tmp_text:
                pos += 1
                if symbol.isdigit():
                    if first_digit<0:
                        first_digit = pos
                    last_digit = pos
            print('first_digit pos: %s, last_digit pos: %s' % (first_digit, last_digit))
            # Обрезка по последнюю цифру
            tmp_text = tmp_text[first_digit:len(tmp_text)-(len(tmp_text)-last_digit-1)]
            print('tmp_text="%s"' % tmp_text)
            # Очистка для безопасного расчета
            text = self.purge_eval_text(tmp_text)

            self.labelFormula.setText(text)
            # text = str(text)
            eval_result = eval(text)
            self.labelResult.setText(str(eval_result))
        except:
            self.labelResult.setText('Err')

    def add_to_history(self):
        try:
            # text = unicode(self.lineEdit.text())
            text = self.lineEdit.text()
            eval_result = eval(self.purge_eval_text(text))
            self.textBrowser.append("%s = <b>%s</b>" % (text, eval_result))
            self.lineEdit.setText('')
            self.clear_result_field()
        except:
            self.textBrowser.append("<font color=red>%s is invalid!</font>" % text)
    
    def add_result_to_note(self):
        # Проверяем видимость панели с текстом заметки
        #if Note.is_visible(self):
            ## Видимость есть. Вставляем текст результата.
            #cursor = main_window.textBrowser.textCursor()
            #cursor.insertText(self.labelResult.text())
        pass

    def clear_history(self, text):
        self.textBrowser.setHtml("")




