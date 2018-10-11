import re

from PyQt5 import QtGui

# from relanotes.relanotes import root_logger, text_format, main_window, note


class Text_Format():
        # Класс форматирования текста в редакторе и его преображение при копировании и т.д.
        # h_span_preformatting = '<span style=" font-family:\'%s\'; font-size:%spx; font-weight:%s; color:%s;">'

        editor_h1_span = ''
        editor_h2_span = ''
        editor_h3_span = ''
        editor_h4_span = ''
        editor_h5_span = ''
        editor_h6_span = ''
        editor_h_span = ['0-empty', editor_h1_span, editor_h2_span, editor_h3_span, editor_h4_span, editor_h5_span, editor_h6_span]

        # FIXME: Цвет текста подходит для светлой темы. Не подходит для темной.
        editor_default_font_span = '<span style=" font-family:\'Sans\'; font-size:17px; font-weight:0; color:#1a1a1a;">'
        # editor_default_font_span = '<span>'

        # editor_italic_span =
        editor_strikethrough_span = \
            '<span style=" font-family:\'Sans\'; font-size:17px; text-decoration: line-through; color:#aaaaaa;">'
        # editor_bold_span =
        # FIXME: Цвет кода подходит для светлой темы. Не подходит для темной.
        # editor_code_span = '<span style=" font-family:\'Mono\'; font-size:16px; color:#501616;">'
        editor_code_span = '<span style=" font-family:\'Mono\'; font-size:17px; color:#9c2b2b;">'

        editor_mark_span = \
            '<span style=" font-family:\'Sans\'; font-size:17px; color:#1a1a1a; background-color:#ffccaa;">'
        editor_li_span = \
            '<li style=" font-family:\'Sans\'; font-size:17px;" style=" margin-top:6px; margin-bottom:6px; ' \
            'margin-left:-20px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">'

        # FIXME: Цвет ссылок подходит для светлой темы. Не подходит для темной.
        # editor_link_external_style = 'style=" font-size:15px; color:#004455; text-decoration: none;"'
        editor_link_external_style = 'style=" font-size:17px; color:#0089ab; text-decoration: none;"'

        # editor_link_local_span =
        # editor_link_wiki_span =

        editor_default_font = QtGui.QFont('Sans', 17, QtGui.QFont.Normal)
        # editor_default_font.setStyle(QFont.Normal)
        # editor_default_font.setBold(False)
        # editor_default_font.setFamily('Sans')
        # editor_default_font.setPixelSize(17)

        editor_default_format = QtGui.QTextCharFormat()
        editor_default_format.setFont(editor_default_font)

        '''
        def remove_concat_empty_tags(self, html_source):
            # Удаляем пустые состыковывающиеся теги
            pos = 0
            while html_source.find('></', pos)>=0:
                pos = html_source.find('></', pos)
                pos11 = html_source.rfind('<', 0, pos)
                #if html_source[pos11+1]=='/':
                if html_source[pos11+1]==os.path.sep:
                    pos += 1
                    continue
                pos21 = pos + 3
                pos22 = html_source.find('>', pos21)
                print ('block1 '+str(pos11)+'-'+str(pos)+', block2 '+str(pos21)+'-'+str(pos22))
                print ('! : '+html_source[pos-10:pos+10] + ',  '+ html_source[pos11+1:pos] + ' ?? ' +
                html_source[pos21:pos22])
                if html_source[pos11+1:pos]==html_source[pos21:pos22]:
                    # Удаляем найденный тег с открытием и закрытием
                    html_source = html_source[:pos11]+html_source[pos22+1:]
                pos = pos22
    
            return html_source
        '''

        # FIXME: . набираемые и вставляемые текстом ссылки не подсвечиваются сразу-же


        def adaptate_alien_html_styles(self, html_source):
            # Адаптируем чужие стили html к стилям текущей темы span

            root_logger.info('\nПолучили для адаптации при вставке следующий html:')
            root_logger.info('=' * 40)
            root_logger.info(html_source)
            # print('Получили для адаптации при вставке следующий html:\n' + html_source + '\n')
            root_logger.info('=' * 40)

            max_size_of_html_source = len(html_source)
            # TODO: ... записать в преимущества функцию умного преобразования инородного html и вставки простого текста
            #  в свой html/wiki
            # TODO: ... сделать функцию иморта из любого html на основе преобразования инородного html в свой

            # Проверяем - не наш ли это собственный текст
            '<html><head><meta name="qrichtext"'
            "<!--StartFragment-->"
            "<!--EndFragment-->"

            # Удаляем все переносы строк \n
            html_source = html_source.replace('\n', '')
            html_source = html_source.replace('\r', '')

            # html_source = self.remove_concat_empty_tags(html_source)

            need_insert_p_at_end = False  # Исправляем багу с <li> - чтобы текст после вставки не съезжал вправо

                    #  Удаляем все div, заменяем </div> на переносы строк
                    # <h1> - <h6> в заголовки
                    # italic и <i> в италик
                    # strhroughout (?) и  <s> в зачеркнутый
                    # картинки в картинку
                    # ссылки разбиваются на линк и текст рядом
                    # принимаем списки

            # Исправляем баги оформления
            # Бага от Kinozal - h2 обрамляет весь текст названия и параметров фильма. Удаляем его
            # если внутри <h?> есть переносы строк
            str1 = html_source[:4]
            str2 = html_source[-5:]
            between = html_source[4:-5]
            if ((str1 == '<h1>' and str2 == '</h1>') or (str1 == '<h2>' and str2 == '</h2>') or (str1 == '<h3>' and
                str2 == '</h3>') or (str1 == '<h4>' and str2 == '</h4>') or (str1 == '<h5>' and str2 == '</h5>') or
                    (str1 == '<h6>' and str2 == '</h6>')) and '<br>' in between:
                # print ('str1='+str1, 'str2='+str2, 'between='+between)
                # print('Clear H wrong tag from paste html source')
                root_logger.info('Clear H wrong tag from paste html source')
                html_source = between

            # Удаляем все что связано с размером и цветом шрифта

            # Зачеркнутому, заголовкам, pre, ссылкам, подчернутому (mark) выставляем нужный стиль

            # Сначала корректируем стиль ссылок и переносим их "влево", удаляя окончания </a>
            if html_source.find('<a') >= 0:
                # print('\nКорректируем стиль ссылок')
                # html_source = re.sub('<a[^>]>([^<])</a>', self.editor_link_external_span_in_tag+'\\1</span>',
                # html_source)
                pos = 0

                # print('\n Оригинал с A, pos='+str(pos)+':\n'+html_source)
                html_source = html_source.replace('</a>', '')

                # html_source = re.sub('<a .*?href="(*.?)" .*?>', '<a '+self.editor_link_external_style+'
                # href="\\1">\\1</a>', html_source)
                while html_source.find('<a', pos) >= 0:
                    if pos>max_size_of_html_source:
                        # print("желаемый pos превысил размер текста")
                        root_logger.info('желаемый pos превысил размер текста')
                        break
                    # print("#1 pos=%s, html_source.find('<a', pos)=%s" % (pos, html_source.find('<a', pos)))
                    root_logger.info("#1 pos=%s, html_source.find('<a', pos)=%s" % (pos, html_source.find('<a', pos)))

                    pos1 = html_source.find('<a', pos)
                    pos_href_1 = html_source.find('href=', pos1)
                    pos_href_1 = html_source.find('"', pos_href_1)
                    pos_href_2 = html_source.find('"', pos_href_1 + 1)
                    pos2 = html_source.find('>', pos_href_2)
                    href = html_source[pos_href_1 + 1:pos_href_2]
                    new_link = ' <a ' + self.editor_link_external_style + ' href="' + href + '">' + href + '</a> '

                    html_source = html_source[:pos1] + new_link + html_source[pos2 + 1:]
                    pos = pos2

                # print('\n С заменой A:\n'+html_source)

            # Картинки заменяем ссылками на них
            if html_source.find('<img') >= 0:
                pos = 0
                while html_source.find('<img', pos) >= 0:
                    if pos>max_size_of_html_source:
                        # print("желаемый pos превысил размер текста")
                        root_logger.info('желаемый pos превысил размер текста')
                        break
                    # print("#2 pos=%s, html_source.find('<img', pos)=%s" % (pos, html_source.find('<a', pos)))
                    root_logger.info("#2 pos=%s, html_source.find('<img', pos)=%s" % (pos, html_source.find('<a', pos)))

                    pos1 = html_source.find('<img', pos)
                    pos2 = html_source.find('>', pos1)
                    pos_src_1 = html_source.find('src=', pos1)
                    pos_src_1 = html_source.find('"', pos_src_1)
                    pos_src_2 = html_source.find('"', pos_src_1 + 1)

                    pos = pos1
                    # print('\n Оригинал с IMG, pos='+str(pos)+':\n'+html_source)

                    href = html_source[pos_src_1 + 1:pos_src_2]
                    new_link = '<br><a ' + self.editor_link_external_style + ' href="' + href + '">' + href + '</a><br>'

                    html_source = html_source[:pos1] + ' ' + new_link + ' ' + html_source[pos2 + 1:]
                    # print('\n С заменой IMG:\n'+html_source)

            # Корректируем заголовки
            if html_source.find('<h') >= 0:
                # print('\nКорректируем стиль заголовков')
                # html_source = re.sub('<h1[.*?]>(.*?)</h1>', '<p>'+self.editor_h1_span+self.editor_h1
                # _span+'\\1</span></p>', html_source)
                h_begin = ['<h1', '<h2', '<h3', '<h4', '<h5', '<h6']
                h_end = ['</h1>', '</h2>', '</h3>', '</h4>', '</h5>', '</h6>']
                h_span = [self.editor_h1_span, self.editor_h2_span, self.editor_h3_span, self.editor_h4_span,
                          self.editor_h5_span, self.editor_h6_span]

                # print('\n Оригинал с H, pos='+str(pos)+':\n'+html_source)

                for i in range(0, 5):
                    pos = 0
                    while html_source.find(h_begin[i], pos) >= 0:
                        if pos > max_size_of_html_source:
                            # print("желаемый pos превысил размер текста")
                            root_logger.info('желаемый pos превысил размер текста')
                            break
                        # print("#3 pos=%s, html_source.find(h_begin[i], pos)=%s" % (pos, html_source.find(h_begin[i], pos)))
                        root_logger.info("#3 pos=%s, html_source.find(h_begin[i], pos)=%s" % (pos, html_source.find(h_begin[i], pos)))

                        pos = html_source.find(h_begin[i], pos)
                        pos2 = html_source.find('>', pos)
                        html_source = html_source[:pos] + '<p>' + h_span[i] + html_source[pos2 + 1:]

                    # pos = 0
                    html_source = html_source.replace(h_end[i], '</span></p>')
                # print('\n С заменой H:\n'+html_source)

            # Меняем стиль маркированному списку, удаляя <ul ..> и </ul>
            if html_source.find('<li') >= 0:
                html_source = re.sub('(<li.*?>)', self.editor_li_span, html_source)
                if html_source[-len('</ul>'):] == '</ul>':
                    need_insert_p_at_end = True

            # Добавляем в наш редактор, предварительно обернув в div стиля нашего шрифта по-умолчанию
            html_source = text_format.editor_default_font_span.replace('<span ', '<div ') + html_source + '</div>'
            if need_insert_p_at_end:
                html_source += '</p><p>'

            # print('\nИтоговый результат:\n' + html_source + '\n')

            root_logger.info('\nИтоговый результат:')
            root_logger.info('=' * 40)
            root_logger.info(html_source)
            root_logger.info('=' * 40)

            return html_source


        def switch_format_span(self, format_span, action):
            # Универсальная функция переключения или установки формата шрифта для выделенного фрагмента
            cursor = main_window.textBrowser_Note.textCursor()
            line_html = note.clear_selection_html_cover(cursor.selection().toHtml())
            text = cursor.selectedText()
            pos_cur = cursor.position()
            if pos_cur != cursor.selectionEnd():
                selection_begin = cursor.selectionEnd()
            else:
                selection_begin = cursor.selectionStart()
            # selection_end = cursor.selectionEnd()

            if format_span in line_html[:len(format_span) + 1]:
                # print('Форматирование уже стоит. Убираем  его..')
                # cursor.removeSelectedText()
                cursor.insertHtml(self.editor_default_font_span + text + '</span>')
                action.setChecked(False)
            else:
                # print('Форматирования нет или есть другое. Очищаем стиль выделение и ставим наш.')
                # cursor.removeSelectedText()
                cursor.insertHtml(format_span + text + '</span>')
                action.setChecked(True)
            # Восстанавливаем выделение пользователя
            cursor.setPosition(selection_begin)
            # cursor.setPosition(selection_end, QtGui.QTextCursor.KeepAnchor)
            cursor.setPosition(pos_cur, QtGui.QTextCursor.KeepAnchor)
            main_window.textBrowser_Note.setTextCursor(cursor)
            # cursor.select(QtGui.QTextCursor.BlockUnderCursor)

            # FIXME: .. при выделении строки с начала сложным форматирование с тегом <li> возникают проблемы

        def update_ui_with_cursor_span(self, result=False):
            # Универсальная проверка наличия определенного стиля в курсоре и обновлении связанного
            # элемента интерфейса action
            # result содержит признак присутствия ранее в строке более высокоуровневого форматирования,
            # например, заголовков

            # FIXME: .. Если курсор до выделения - не отображается ни сложное форматирование, ни жирн/италик
            # FIXME: .. Нажатие на форматирование без выделения не сбрасывает оформление набираемого затем текста

            actions = [main_window.actionStrikethrough, main_window.actionCode, main_window.actionMark]
            format_spans = [self.editor_strikethrough_span, self.editor_code_span, self.editor_mark_span]

            if result:
                # i = 0  # Снимаем выделение со всех действий
                for i in range(0, len(actions)):
                    actions[i].setChecked(False)
                return result

            cursor = main_window.textBrowser_Note.textCursor()
            pos_cur = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            pos_begin_line = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            # full_line_html = note.clear_selection_html_cover( cursor.selection().toHtml() )
            pos_end_line = cursor.position()
            cursor.setPosition(pos_cur)  # Возвращаем курсор на место

            if pos_begin_line == pos_end_line:
                # print('Позиция начала строки равна позиции конца: '+str(pos_begin_line))
                # i = 0  # Снимаем выделение со всех действий
                for i in range(0, len(actions)):
                    actions[i].setChecked(False)
                return result

            if pos_cur > pos_begin_line:
                new_pos_cur = pos_cur - 1
            else:
                new_pos_cur = pos_begin_line + 1

            cursor.setPosition(new_pos_cur, QtGui.QTextCursor.KeepAnchor)  # Делаем временное виртуальное выделение
            # if cursor.selection().isEmpty():
            #    print('Выбранный текст пустой')
            #    return result

            line_html = note.clear_selection_html_cover(cursor.selection().toHtml())
            # print('Выделение '+str(pos_cur)+'-'+str(new_pos_cur) + ', строка '+str(pos_begin_line)+'-'+
            # str(pos_end_line))
            # print('Полная строка: '+full_line_html)
            # print('Выделение: '+line_html)

            # Перебираем все сложные форматы, в поиске присутствующего.
            # У остальных снимаем выделение с действия.

            # i = 0
            for i in range(0, len(actions)):

                if not result and format_spans[i] in line_html:
                    # print('Форматирование найдено: '+actions[i].text())
                    actions[i].setChecked(True)
                    result = True  # Устанавливаем признак найденного формата в строке
                else:
                    # print('Форматирования '+actions[i].text()+' нет')
                    actions[i].setChecked(False)

            cursor.setPosition(pos_cur)
            return result

        def switch_h_line(self, h):
            editor_h_action = ['0-empty', main_window.actionHeading_1, main_window.actionHeading_2,
                               main_window.actionHeading_3, main_window.actionHeading_4, main_window.actionHeading_5,
                               main_window.actionHeading_6]

            cursor = main_window.textBrowser_Note.textCursor()
            pos_cur = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            cursor.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)
            line_html = note.clear_selection_html_cover(cursor.selection().toHtml())

            if self.editor_h_span[h] in line_html:
                # print('Заголовок уже стоит. Убираем форматирование заголовка.')
                text = cursor.selectedText()
                # cursor.removeSelectedText()
                cursor.insertHtml(self.editor_default_font_span + text + '</span>')
                editor_h_action[h].setChecked(False)
            else:
                # print('Заголовка нет или есть другой. Удаляем форматирование и ставим новый.')
                text = cursor.selectedText()
                # cursor.removeSelectedText()
                cursor.insertHtml(self.editor_h_span[h] + text + '</span>')
                editor_h_action[h].setChecked(True)

            cursor.movePosition(pos_cur)

        def h1(self):
            self.switch_h_line(1)

        def h2(self):
            self.switch_h_line(2)

        def h3(self):
            self.switch_h_line(3)

        def h4(self):
            self.switch_h_line(4)

        def h5(self):
            self.switch_h_line(5)

        def h6(self):
            self.switch_h_line(6)

        def bold(self):
            cursor = main_window.textBrowser_Note.textCursor()
            pos_cur = cursor.position()
            if pos_cur == cursor.selectionStart():
                # Исправляем ситуацию, когда курсор, стоя в начале, не видит выделенного текста после него
                cursor.setPosition(pos_cur + 1, QtGui.QTextCursor.KeepAnchor)
                fmt = cursor.charFormat()
                cursor.setPosition(pos_cur, QtGui.QTextCursor.KeepAnchor)
            else:
                fmt = cursor.charFormat()

            if fmt.fontWeight() == 75:
                # print ('Bold already. Need clear bold.')
                fmt.setFontWeight(0)
            else:
                # print ('Need set bold.')
                fmt.setFontWeight(75)

            cursor.setCharFormat(fmt)  # Устанавливаем стиль "с нуля", удаляя предыдущий

        def italic(self):
            cursor = main_window.textBrowser_Note.textCursor()
            pos_cur = cursor.position()
            if pos_cur == cursor.selectionStart():
                # Исправляем ситуацию, когда курсор, стоя в начале, не видит выделенного текста после него
                cursor.setPosition(pos_cur + 1, QtGui.QTextCursor.KeepAnchor)
                fmt = cursor.charFormat()
                cursor.setPosition(pos_cur, QtGui.QTextCursor.KeepAnchor)
            else:
                fmt = cursor.charFormat()

            if fmt.fontItalic():
                fmt.setFontItalic(False)
            else:
                fmt.setFontItalic(True)
            cursor.setCharFormat(fmt)  # Устанавливаем стиль "с нуля", удаляя предыдущий

        def strikethrough(self):
            self.switch_format_span(self.editor_strikethrough_span, main_window.actionStrikethrough)

        def code(self):
            self.switch_format_span(self.editor_code_span, main_window.actionCode)

        def mark(self):
            self.switch_format_span(self.editor_mark_span, main_window.actionMark)

        def clear_format(self):
            # Устанавливаем формат шрифта по-умолчанию
            # FIXME: как и другое форматирование - удаляет оформление ссылок
            cursor = main_window.textBrowser_Note.textCursor()
            cursor.setCharFormat(self.editor_default_format)

        def getLineAtPosition3(self, pos):
            # Моя собственная функция расчета количества строк до позиции

            # Показываем исходник выделенного текста, если надо
            self.getHtmlSourceOfSelectedPart()

            # Копируем курсор текстового редактора
            cursor = main_window.textBrowser_Note.textCursor()
            # Устанавливаем курсору указанное в параметрах положение
            cursor.setPosition(pos)
            #cur_pos = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            i = 1
            while not cursor.atStart():
                cursor.movePosition(QtGui.QTextCursor.Up)
                cursor.movePosition(QtGui.QTextCursor.StartOfLine)
                # Если не перемещаться на начало линии - зависнет, не достигнув начала первой строки
                i += 1
            #cursor.setPosition(cur_pos)
            return i

        def getLineAtPosition(self, pos):
            cursor = main_window.textBrowser_Note.textCursor()
            cursor.setPosition(pos)

            cursor.movePosition(QtGui.QTextCursor.StartOfLine)
            lines = 0

            lines_text = cursor.block().text().splitlines()
            lines_pos = 0
            for line_text in lines_text:
                lines_pos += len(line_text) + 1
                if lines_pos > cursor.position() - cursor.block().position():
                    break
                lines += 1

            block = cursor.block().previous()
            while block.isValid():
                lines += block.lineCount()
                block = block.previous()

            return lines

        def getLineAtPosition2(self, pos):
            cursor = main_window.textBrowser_Note.textCursor()
            # cursor.setPosition(pos)
            # cursor.movePosition(0)
            cursor.setPosition(0)
            cursor.setPosition(pos, QtGui.QTextCursor.KeepAnchor)
            # main_window.textBrowser_Note.setTextCursor(cursor);
            # tmp_string = cursor.selection().toHtml()
            html_source = cursor.selection().toHtml()

            # html_source = main_window.textBrowser_Note.toHtml()
            # html_source = re.sub('(/.*/gsm</head>)', '', html_source)
            html_source = re.sub('\n', '', html_source)
            # html_source = re.sub('.*<body.*?>', '', html_source, flags=re.MULTILINE|re.DOTALL)
            html_source = re.sub('.*<body.*?>', '', html_source)
            html_source = re.sub('(</body.*>)', '', html_source)
            html_source = re.sub('(<!--.*?-->)', '', html_source)
            html_source = re.sub('(<span.*?</span>)', '', html_source)
            # html_source = re.sub('(<p.*?>)', '', html_source)
            # html_source = re.sub('(<span.*?>)', '', html_source)
            # html_source = re.sub('(</span>)', '', html_source)
            # html_source = re.sub('(</p>)', '\n', html_source)
            # html_source = re.sub('(<br.*?>)', '\n', html_source)

            main_window.plainTextEdit_Note_Ntml_Source.setPlainText(html_source)
            # main_window.plainTextEdit_Note_Ntml_Source.textCursor().setPosition(pos)

        def getHtmlSourceOfSelectedPart(self):
            if main_window.actionShow_note_HTML_source.isChecked():
                cursor = main_window.textBrowser_Note.textCursor()
                # html_source = cursor.selection().toPlainText() + ' ### ' + cursor.selection().toHtml()
                html_source = cursor.selection().toHtml()
                NoteSelectedTextRegex = re.compile(r'.*?-->(.*)<!--.*?', re.DOTALL)
                NoteSelectedText = NoteSelectedTextRegex.search(html_source)
                if NoteSelectedText:
                    # html_source = html_source + ' ### ' + NoteSelectedText.group(1)
                    html_source = NoteSelectedText.group(1)
                # html_source = cursor.selection().toHtml()

                # # html_source = main_window.textBrowser_Note.toHtml()
                # # html_source = re.sub('(/.*/gsm</head>)', '', html_source)
                # html_source = re.sub('\n', '', html_source)
                # # html_source = re.sub('.*<body.*?>', '', html_source, flags=re.MULTILINE|re.DOTALL)
                # html_source = re.sub('.*<body.*?>', '', html_source)
                # html_source = re.sub('(</body.*>)', '', html_source)
                # html_source = re.sub('(<!--.*?-->)', '', html_source)
                # html_source = re.sub('(<span.*?</span>)', '', html_source)
                # # html_source = re.sub('(<p.*?>)', '', html_source)
                # # html_source = re.sub('(<span.*?>)', '', html_source)
                # # html_source = re.sub('(</span>)', '', html_source)
                # # html_source = re.sub('(</p>)', '\n', html_source)
                # # html_source = re.sub('(<br.*?>)', '\n', html_source)

                main_window.plainTextEdit_Note_Ntml_Source.setPlainText(html_source)


        def update_ui(self):
            # Обновляем интерфейс в соответствии с выделенным или написанным текстом

            cursor = main_window.textBrowser_Note.textCursor()

            # 'pos: '+str(cursor.position())
            # 'line2: '+str( self.getLineAtPosition2(cursor.position()) )+  \
            # 'line: '+str( self.getLineAtPosition(cursor.position()) )+  \

            #mess = 'line: ' + str(self.getLineAtPosition3(cursor.position())) + \
            #       '  column: ' + str(cursor.columnNumber())

            mess = 'line: %s  column: %s  pos: %s' % ( self.getLineAtPosition3(cursor.position()),
                                                     cursor.columnNumber(),
                                                     cursor.position(),
                                                     )

            # + \
            # ', block: '+str(cursor.blockNumber())+ \
            # ', sel.start: '+str(cursor.selectionStart())+', sel.end: '+str(cursor.selectionEnd())
            main_window.statusbar.showMessage(mess)

            # cursor =  QtGui.QTextCursor(main_window.doc_source)
            # cursor =  main_window.textBrowser_Note.textCursor()
            # cursor.movePosition(QtGui.QTextCursor.End)
            # tmp_string = cursor.selection().toHtml()
            # main_window.statusbar.showMessage(tmp_string.rpartition('StartFragment-->')[2])
            # main_window.plainTextEdit_Note_Ntml_Source.setPlainText(tmp_string.rpartition('StartFragment-->')[2])

            # Проверяем строку на наличие в ней заголовка
            complex_format_was_found = False  # Признак, чтобы в жирном заголовке ниже не искать жирный текст

            pos_cur = cursor.position()
            # print( 'Pos: '+str(cursor.position())+', sel.start: '+str(cursor.selectionStart())+', sel.end: '
            # +str(cursor.selectionEnd()) )
            cursor.movePosition(QtGui.QTextCursor.EndOfLine)
            # pos_end = cursor.position()
            cursor.movePosition(QtGui.QTextCursor.StartOfLine, QtGui.QTextCursor.KeepAnchor)
            # pos_begin = cursor.position()
            # print('pos line: '+ str(pos_begin)+'-'+ str(pos_end) +', NEW selection: '+str(cursor.selectionStart())+
            # '-'+str(cursor.selectionEnd()) )
            line_html1 = cursor.selection().toHtml()
            line_html = note.clear_selection_html_cover(cursor.selection().toHtml())
            # print('line_html: '+line_html)

            if self.editor_h1_span in line_html:
                main_window.actionHeading_1.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_1.setChecked(False)

            if self.editor_h2_span in line_html:
                main_window.actionHeading_2.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_2.setChecked(False)

            if self.editor_h3_span in line_html:
                main_window.actionHeading_3.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_3.setChecked(False)

            if self.editor_h4_span in line_html:
                main_window.actionHeading_4.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_4.setChecked(False)

            if self.editor_h5_span in line_html:
                main_window.actionHeading_5.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_5.setChecked(False)

            if self.editor_h6_span in line_html:
                main_window.actionHeading_6.setChecked(True)
                complex_format_was_found = True
            else:
                main_window.actionHeading_6.setChecked(False)

            # Особое форматирование, дополняющее обычный формат текста
            if self.editor_li_span in line_html:
                main_window.actionBullet_List.setChecked(True)
            else:
                main_window.actionBullet_List.setChecked(False)

            cursor.setPosition(pos_cur)

            # Определяем сложное оформление текста
            if self.update_ui_with_cursor_span(complex_format_was_found):
                complex_format_was_found = True

            if not complex_format_was_found:
                # Определяем простое форматирование текста
                cursor = main_window.textBrowser_Note.textCursor()
                fmt = cursor.charFormat()

                if fmt.fontItalic():
                    main_window.actionItalic.setChecked(True)
                else:
                    main_window.actionItalic.setChecked(False)

                if fmt.fontWeight() == 75:
                    main_window.actionBold.setChecked(True)
                else:
                    main_window.actionBold.setChecked(False)
            else:
                main_window.actionBold.setChecked(False)
                main_window.actionItalic.setChecked(False)
                # print('базовое форматирование не проверяем, снимем его отметки')

        def __init__(self):
            pass