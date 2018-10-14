import codecs
import os

from PyQt5 import QtWidgets

from relanotes.qtdesign_ui import note_multiaction


class NoteMultiactionWindow(QtWidgets.QDialog, note_multiaction.Ui_DialogNoteMultiaction):
    """ Окно выполнения операций над файлом заметки. """

    rn_app = None

    def __init__(self, rn_app, parent=None):

        self.rn_app = rn_app

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
        self.rn_app.main_window.open_file_in_editor(full_filename, line_number=3)
        self.rn_app.main_window.statusbar.showMessage('New note created: ' + full_filename)
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
        self.rn_app.main_window.open_file_in_editor(full_filename, line_number=3)
        self.rn_app.main_window.statusbar.showMessage('New note created: ' + full_filename)
        self.close()