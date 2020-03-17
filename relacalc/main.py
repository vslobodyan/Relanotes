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
        # self.lineEdit.textEdited.connect(self.update_ui)
        self.textEdit.textChanged.connect(self.update_ui)
        # self.connect(self.lineEdit, SIGNAL("returnPressed()"), self.add_to_history)
        # self.lineEdit.returnPressed.connect(self.add_to_history)
        # self.textEdit.returnPressed.connect(self.add_to_history)
        # self.connect(self.labelClearHistory, SIGNAL("linkActivated( const QString& )"), self.clear_history)
        self.labelClearHistory.linkActivated.connect(self.clear_history)

        self.chbTabToPlus.stateChanged.connect(self.update_ui)
        self.chbNewlineToPlus.stateChanged.connect(self.update_ui)
        self.chbSpaceToPlus.stateChanged.connect(self.update_ui)
        self.chbRemoveText.stateChanged.connect(self.update_ui)

        self.rbDontChangeDecimalPoint.toggled.connect(self.update_ui)
        self.rbRemoveDecimalPoint.toggled.connect(self.update_ui)
        self.rbDecimalPointMakeDot.toggled.connect(self.update_ui)


        self.buttonAdd_to_note.clicked.connect(self.add_result_to_note)
        self.clear_result_field()
        # self.lineEdit.setFocus()
        self.textEdit.setFocus()

    def clear_result_field(self):
        self.labelResult.setText('0')
        self.labelFormula.setText('')


    def purge_eval_text(self, text):
        text = text.replace(' ', '')
        return text

    def update_ui(self):
        try:
            #text = unicode(self.lineEdit.toPlainText())
            # text = self.lineEdit.text()
            # text = self.lineEdit.text()
            text = self.textEdit.toPlainText()
            print('We have input text: "%s"' % text)
            tmp_text = text

            if self.chbRemoveText.isChecked():
                tmp_text = ''
                # Чистим текст от букв
                for symbol in text:
                    if not symbol.isalpha():
                        tmp_text += symbol

            if self.chbTabToPlus.isChecked():
                # Табуляции меняем на +
                tmp_text = tmp_text.replace('\t', '+')

            if self.chbNewlineToPlus.isChecked():
                # Переносы строк меняем на +
                tmp_text = tmp_text.replace('\n', '+')

            if self.chbSpaceToPlus.isChecked():
                # Пробелы меняем на +
                tmp_text = tmp_text.replace(' ', '+')

            # Удаляем пустышки
            # what_delete = []
            # # what_delete = ['+, ', ]
            # for one in what_delete:
            #     tmp_text = tmp_text.replace(one, '')

            if self.rbRemoveDecimalPoint.isChecked():
                # Удаляем запятые
                tmp_text = tmp_text.replace(',', '')

            if self.rbDecimalPointMakeDot.isChecked():
                # Запятые меняем на точки (знак десятичных в данном случае)
                tmp_text = tmp_text.replace(',', '.')

            print('Before remove continuous pluses: %s' % tmp_text)
            # Удаляем лишние '+' идущие друг за другом
            text_new = ''
            last_was_plus = False
            for char in tmp_text:
                if char == '+':
                    if last_was_plus:
                        continue
                    else:
                        last_was_plus = True
                        text_new += char
                else:
                    last_was_plus = False
                    text_new += char
            tmp_text = text_new
            print('After remove continuous pluses: %s' % tmp_text)

            #if self.chbRemoveText.isChecked():
                #print('tmp_text before final cornering cleaning: "%s"' % tmp_text)
                ## Обрезаем с обоих краев лишние символы, которые не цифры. Формула должна начинаться и заканчиваться цифрой.
                #first_digit = -1
                #last_digit = -1
                #pos = -1
                ## Ищем последнюю цифру
                #for symbol in tmp_text:
                    #pos += 1
                    #if symbol.isdigit():
                        #if first_digit<0:
                            #first_digit = pos
                        #last_digit = pos
                #print('first_digit pos: %s, last_digit pos: %s' % (first_digit, last_digit))
                ## Обрезка по последнюю цифру
                #tmp_text = tmp_text[first_digit:len(tmp_text)-(len(tmp_text)-last_digit-1)]
                #print('tmp_text="%s"' % tmp_text)


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
            # text = self.lineEdit.text()
            text = self.textEdit.toPlainText()
            eval_result = eval(self.purge_eval_text(text))
            self.textBrowser.append("%s = <b>%s</b>" % (text, eval_result))
            # self.lineEdit.setText('')
            self.textEdit.setText('')
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




