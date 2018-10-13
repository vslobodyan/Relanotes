from PyQt5 import QtWidgets

# from relanotes.rn_class import note, text_format
# from relanotes.main import note, text_format


class MyTextBrowser(QtWidgets.QTextBrowser):
    # Класс, переопределяющий работу основного навигатора заметок
    rn_app = None

    def __init__(self, rn_app, parent=None):
        self.rn_app = rn_app
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

        if source_html == '' or self.rn_app.note.paste_as_text_once :
            self.rn_app.note.paste_as_text_once = False
            self.insertPlainText(source.text())
        else:
            self.insertHtml(self.rn_app.text_format.adaptate_alien_html_styles(source_html))