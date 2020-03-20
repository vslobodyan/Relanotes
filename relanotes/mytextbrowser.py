from PyQt5 import QtWidgets


class MyTextBrowser(QtWidgets.QTextBrowser):
    """ Переопределение класса текстового браузера, который используется как основной навигатор заметок """

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
            print('Insert as text')
            self.rn_app.note.paste_as_text_once = False
            self.insertPlainText(source.text())
        else:
            print('Insert as html')
            self.insertHtml(self.rn_app.text_format.adaptate_alien_html_styles(source_html))