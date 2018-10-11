from PyQt5 import QtWidgets

# from relanotes.relanotes import note, text_format


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