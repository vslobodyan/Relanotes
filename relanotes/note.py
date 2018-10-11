import codecs
import html
import os
import re
from datetime import datetime

from PyQt5 import QtGui

# from relanotes.relanotes import main_window, table_of_note_contents, notelist, text_format, root_logger, \
#     app_settings, note, notemultiaction_win
from relanotes.theme import Theme
from relanotes.routines import get_correct_filename_from_url


class Note():
    """ Все что определяет работу с заметкой:
    загрузка, форматирование, редактирование, сохранение, UI

    *UI* (main_window):
    frameSearchInNote, lineTextToFind
    textBrowser
    doc_source  (исходник документа)
    """
    # cursor_format = QTextCharFormat
    # cursor = QtGui.QTextCursor(main_window.doc_source)

    paste_as_text_once = False

    filename = ''        # Ссылка на файл открытой заметки. Внутренняя тема для класса Notes. Повсеместно для определения урла открытой заметки используется main_window.current_open_note_link
    format_type = 'zim'  # zim, md, ...
    metadata_lines_before_note = ''  # Специальные поля заметки, например, от Zim, которые надо сохранить и записать при сохранении

    # Символ пробела для замены и сохранения пробелов в исходнике для редактора
    #space_symbol = '&ensp;'
    #space_symbol = '&emsp;'
    #space_symbol = '&nbsp;'
    #space_symbol = '&#32;'
    #space_symbol = ' '




    def set_visible(self, visible=True):
        # Переключение видимости все что связано с непосредственным редактирование заметки
        if visible:
            # Отображаем все виджеты, связанные Note
            main_window.stackedWidget.setCurrentIndex(1)
            # Скрываем конкурирующие виджеты
            # note.setVisible(False)
            table_of_note_contents.setVisible(False)
            notelist.set_visible(False)

        # Переключаем все действия, связанные с форматирование и редактирование заметки
        # note_actions = [
            # main_window.actionAdd_Link, main_window.actionAdd_Image,
            # main_window.actionBold, main_window.actionItalic,
            # main_window.actionStrikethrough, main_window.actionMark,
            # main_window.actionBullet_List, main_window.actionNumber_List,
            # main_window.actionHeading_1, main_window.actionHeading_2,
            # main_window.actionHeading_3, main_window.actionHeading_4,
            # main_window.actionHeading_5, main_window.actionHeading_6,
            # main_window.actionUndo, main_window.actionRedo,
            # main_window.actionClear, main_window.actionFind_in_current_note,
            # main_window.actionFind_next_in_cur_note,
            # main_window.actionShow_content_collapse_all_H,
            # main_window.actionCollapse_all_H_exclude_cur,
            # main_window.actionCollapse_cur_H, main_window.actionExpand_all_H,
            # main_window.actionSave_note, main_window.action_ClearFormat,
            # main_window.actionCode]
        # main_window.actionNote_multiaction,
        # main_window.actionShow_note_contents
        # for action in note_actions:
        for action in main_window.note_editor_actions:
            # action.setEnabled(visible)
            action.setVisible(visible)
        for menu in main_window.note_editor_root_menus:
            # action.setEnabled(visible)
            menu.menuAction().setVisible(visible)

                # Переключаем соотстветствующее отображению действие
        # main_window.actionFast_jump_to_file_or_section.setChecked(visible)

    def is_visible(self):
        if main_window.stackedWidget.currentIndex() == 1:
            return True
        else:
            return False

    def get_span_under_cursor(self, cursor, only_style=False):
        # Функция извлечения очищенного html-кода под курсором
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor)
        html_under_cursor = cursor.selection().toHtml()
        clear_html_under_cursor = self.clear_selection_html_cover(html_under_cursor)
        #print('clear_html_under_cursor ##%s##' % clear_html_under_cursor)
        html_span = clear_html_under_cursor.partition('<span')[2]
        #print('part <span  ###%s###' % html_span)
        if only_style:
            #print('Only style!')
            html_span = html_span.partition('>')[0].lstrip()
        else:
            html_span = '<span' + html_span.partition('>')[0] + '>'
        #print('html_span ##%s##' % html_span)
        #print()
        return html_span

    #def get_style_from_span_under_cursor(self, cursor):
    #    html_span = self.get_span_under_cursor(cursor)
    #    print('STYLE html_span  ###%s###' % html_span)
    #    html_style = html_span.partition('style="')[2]
    #    print('html_style 1  ###%s###' % html_style)
    #    html_style = html_span.rpartition('">')[0]
    #    print('html_style 2  ###%s###' % html_style)
    #    return html_style



    def union_concat_ident_span(self, note_source):
        # Найти и склеить все одинаковые по стилю span в строчках ( разделение по <p> и <br> ), включая
        # <span> разделенные пробелами
        # str.find(sub[, start[, end]])

        pos = 0
        span_end = '</span>'
        span_begin = '<span '
        str_sign_concat = span_end + span_begin

        while note_source.find(str_sign_concat, pos) >= 0:
            # Позиция обнаруженного сочленения двух span
            pos_concat = note_source.find(str_sign_concat, pos)
            # Ищем конец правого span
            pos_rspan_begin = pos_concat + len(span_end)
            pos_rspan_end = note_source.find('>', pos_rspan_begin + len(span_begin)) + 1
            # Ищем начало левого span
            pos_lspan_begin = note_source.rfind(span_begin, 0, pos_concat)
            pos_lspan_end = note_source.find('>', pos_lspan_begin) + 1

            lspan = note_source[pos_lspan_begin: pos_lspan_end]
            rspan = note_source[pos_rspan_begin: pos_rspan_end]

            # print ('Найдено сочленение на позиции',pos_concat,', span-позиции:', pos_lspan_begin, '-', pos_lspan_end,
            # ', ', pos_rspan_begin, '-', pos_rspan_end)
            # print ('Результата вырезки 1: '+lspan)
            # print ('Результата вырезки 2: '+rspan)

            if lspan == rspan:
                # Делаем склейку двух одинаковых span
                note_source_result = note_source[:pos_concat] + note_source[pos_rspan_end:]
                note_source = note_source_result
                pos = pos_concat
            else:
                pos = pos_concat + 1

        return note_source

    def make_all_links_to_wiki_format(self, note_source):
        # Проанализировать и заменить все ссылки <a> на ссылки вики-формата или чистый текст

        pos = 0
        str_a_begin = '<a href="'
        str_a_middle = '">'
        str_a_end = '</a>'
        # FIXME: .. не работает сохранение и восстановление ссылок где текст и ссылка различаются

        while note_source.find(str_a_begin, pos) >= 0:
            # Позиция обнаруженного линка
            pos_a_begin = note_source.find(str_a_begin, pos)
            # Ищем середину линка
            pos_a_middle = note_source.find(str_a_middle, pos_a_begin)
            # Ищем конец линка
            pos_a_end = note_source.find(str_a_end, pos_a_middle)

            # Вынимаем href и текст ссылки
            a_href = note_source[pos_a_begin + len(str_a_begin): pos_a_middle]
            a_text = note_source[pos_a_middle + len(str_a_middle): pos_a_end]
            a_text = re.sub('<span .*?>(.*)</span>', '\\1', a_text)
            # print ('a: '+note_source[ pos_a_begin : pos_a_end+len(str_a_end) ])
            # print ('a_href: '+a_href)
            # print ('a_text: '+a_text)

            if a_href == a_text:
                # print ('У нас простая ссылка')
                # У нас простая ссылка на что-то.
                # Определяем - на что ссылается a_href
                if '://' in a_href and ' ' not in a_href:
                    # Внешний линк
                    # print ('Внешний линк: '+a_href)
                    note_source = note_source[: pos_a_begin] + a_href + note_source[pos_a_end + len(str_a_end):]
                else:
                    # Внутренний или на местные файлы линк
                    note_source = note_source[: pos_a_begin] + '[[' + a_href + ']]' + note_source[pos_a_end + len(str_a_end):]
            else:
                # print ('У нас ссылка с подмененным текстом!')
                # У нас ссылка с подмененным текстом
                # [[1234|text]]
                # Обрабатывается нормально на сохранение в блоке выше, но открытие пока не обрабатывается.
                print ('У нас текст ссылки отличается от текста:')
                print( note_source[pos_a_begin: pos_a_end] )
                print ('a_href: '+a_href)
                print ('a_text: '+a_text)

                note_source = note_source[: pos_a_begin] + '[[' + a_href + '|' + a_text + ']]' + note_source[pos_a_end +
                                                   len(str_a_end):]

            pos = pos_a_begin

        return note_source

    def clear_selection_html_cover(self, html_source):
        # Удаляем html-обертку кода выделенного фрагмента заметки
        # Удаляем лишние переносы строк \n
        html_source = html_source.replace('\n', '')
        start_str = '<!--StartFragment-->'
        end_str = '<!--EndFragment-->'
        if start_str in html_source:
            html_source = html_source.split(start_str)[1]
        if end_str in html_source:
            html_source = html_source.split(end_str)[0]
        return html_source

    def clear_note_html_cover(self, note_source):
        # Удаляем html-обертку основного кода заметки
        # profiler.checkpoint('Начинаем очистку исходника html заметки')
        # Удаляем лишние переносы строк \n
        note_source = note_source.replace('\n', '')
        # Удаляем окантовку контента, включая <body> и крайний <p>
        pos_cut1 = note_source.find('<p ')
        pos_cut1 = note_source.find('>', pos_cut1)
        # print ('Начало html после удаления начала обертки: \n'+note_source[pos_cut1+1:pos_cut1+40]+'\n')

        pos_cut2 = note_source.rfind('</p>')
        # print ('Конец html после удаления конца обертки: \n'+note_source[pos_cut2-40:pos_cut2-1]+'\n')

        note_source = note_source[pos_cut1 + 1:pos_cut2]
        return note_source


    def health_bad_links(self, filename, html_source):
        # Лечение ссылок, испорченных ранее в самых первых версиях RelaNotes
        # [[http://webcast.emg.fm:55655/keks128.mp3.m3u|http://webcast.emg.fm:55655/]]keks128.mp3.m3u

        # html_source = re.sub('[[(.*?)|(.*?)]](.*?)', '\\1', html_source)
        # re.sub('\[\[(?!\[)(.+?)\]\]', '\\1', html_source)

        #html_source = re.sub('\[\[(.+?)\|(.+?)\]\](.+?)', '\\2', html_source)

        #AllLinksRegex = re.compile(r'\[\[(?!\[)(.*?)\]\]')
        #NoteSelectedLinks = AllLinksRegex.search(html_source)
        #if NoteSelectedLinks:
            #print('В файле %s найдены ссылки:' % filename)
            # html_source = html_source + ' ### ' + NoteSelectedText.group(1)
            #print(NoteSelectedLinks)
            #health_link = NoteSelectedText.group(1)
            #print('Исправленный линк: ##%s##' % health_link)


        #def normalize_orders(matchobj):
        #    if matchobj.group(1) == '-': return "A"
        #    else: return "B"
        #re.sub('([-|A-Z])', normalize_orders, '-1234⇢A193⇢ B123')

        def hide_inline_url(matchobj):
            #print('  groups: %s' % matchobj.group(0))
            matching_string = ''
            result = ''
            matching_string = matchobj.group(0)
            if '://' in matching_string:
                print('  group(0): %s' % matching_string)
                print('  group(1): %s' % matchobj.group(1))
                #print('  group(2): %s' % matchobj.group(2))
                #print('  group(3): %s' % matchobj.group(3))
                result = matching_string.replace('://', ':/&#x2F;')
                print('  after replace: %s' % result)
            else:
                result = matching_string
            #if matchobj.group(1) == '-': return "A"
            #else: return "B"
            return result

        #re.sub('([-|A-Z])', normalize_orders, '-1234⇢A193⇢ B123')

        #StrikeRegex = re.compile(r'(~~)(?!~)(.+?)(~~)')
        StrikeRegex = re.compile(r'~~(?!~)(.+?)~~')

        NoteSelectedText = StrikeRegex.findall(html_source)
        if NoteSelectedText:
            print('\nВ файле %s \nнайден зачеркнутый текст: ' % filename)
            for one_text in NoteSelectedText:
                if '://' in one_text:
                    print(' %s' % one_text)

        html_source = StrikeRegex.sub(hide_inline_url, html_source)

        NoteSelectedText = StrikeRegex.findall(html_source)
        if NoteSelectedText:
            print('\nПосле изменения он выглядит так: ')
            for one_text in NoteSelectedText:
                if ':/' in one_text:
                    print(' %s' % one_text)

        return 0

        #pattern = re.compile(r'\*(.*?)\*')
        #>>> pattern.sub(r"<b>\g<1>1<\\b>", text)
        #'imagine⇢a⇢new⇢<b>world1<\\b>,⇢a⇢magic⇢<b>world1<\\b>'


        BadLinksRegex = re.compile('\[\[(.+?)\|(.+?)\]\](.+?)')
        #NoteSelectedText = BadLinksRegex.search(html_source)
        NoteSelectedText = BadLinksRegex.findall(html_source)
        if NoteSelectedText:
            print('\nВ файле %s \nопознаны плохие ссылки: ' % filename)
            for one_text in NoteSelectedText:
                #print(NoteSelectedText)
                print(one_text)
                # html_source = html_source + ' ### ' + NoteSelectedText.group(1)
                #health_link = NoteSelectedText.group(1)
                #health_link = one_text.group(1)
                #print('Исправленный линк: ##%s##' % health_link)

        BadLinksRegex2 = re.compile('&lt;s&gt;(.+?)&lt;/s&gt;')
        #NoteSelectedText = BadLinksRegex2.search(html_source)
        NoteSelectedText = BadLinksRegex2.findall(html_source)
        if NoteSelectedText:
            print('\nВ файле %s \nопознаны плохие ссылки второго типа:' % filename)
            #print(NoteSelectedText)
            for one_text in NoteSelectedText:
                #print(NoteSelectedText)
                print(one_text)




    def convert_zim_text_to_html_source(self, text):
        # Конвертируем текст заметок Zim в формат для редактора заметки

        # Оригинальный код был из функции open_file_in_editor

        # print()
        # print('1 ### convert_zim_text_to_html_source:')
        # print(text)
        # make_initiative_html

        html_source = text
        # html_source = self.textBrowser_Note.toHtml()
        # set header, include css style

        # 'blockstart': re.compile("^(\t*''')\s*?\n", re.M),
        # 'pre':        re.compile("^(?P<escape>\t*''')\s*?(?P<content>^.*?)^(?P=escape)\s*\n", re.M | re.S),
        # 'splithead':  re.compile('^(==+[ \t]+\S.*?\n)', re.M),
        # 'heading':    re.compile("\A((==+)[ \t]+(.*?)([ \t]+==+)?[ \t]*\n?)\Z"),
        # 'splitlist':  re.compile("((?:^[ \t]*(?:%s)[ \t]+.*\n?)+)" % bullet_re, re.M),
        # 'listitem':   re.compile("^([ \t]*)(%s)[ \t]+(.*\n?)" % bullet_re),
        # 'unindented_line': re.compile('^\S', re.M),
        # 'indent':     re.compile('^(\t+)'),


        # Remove ZIM wiki tags from first strings of note:
        # Content-Type:
        # Wiki-Format:
        # Creation-Date:
        zim_wiki_tags = ['Content-Type', 'Wiki-Format', 'Creation-Date']
        self.metadata_lines_before_note = []

        # 1. Режем контент заметки на строки
        text_source_lines = html_source.splitlines()  # ('\n')
        # Проверяем на наличие двух линукс-переносов строк вида \n подряд в конце файла заметки. Из таких переносов один теряется при использовании splitlines. Надо исправить этот баг вручную.
        # if text.endswith(os.linesep+os.linesep):
        # if text.endswith('\n\n'):
        #    # У нас именно такой случай. Добавляем к массиву строк ещё одну пустую
        #    #print('Обнаружили, что текст оканчивается на 2 переноса строк')
        #    text_source_lines.append('')
        # print('### text_source_lines: %s' % text_source_lines)


        first_part1 = first_part2 = first_part3 = ''
        # 2. Проверяем наличие ключевых слов в первых 3 строчках
        if len(text_source_lines) > 0:
            first_part1 = text_source_lines[0].split(':')[0]
        if len(text_source_lines) > 1:
            first_part2 = text_source_lines[1].split(':')[0]
        if len(text_source_lines) > 2:
            first_part3 = text_source_lines[2].split(':')[0]

        # 3. Удаляем строки, в которых обнаружены служебные слова
        if first_part1 in zim_wiki_tags and first_part2 in zim_wiki_tags and first_part3 in zim_wiki_tags:
            # Удаляем первые 3 строчки
            # print('Найдены 3 строки метаданных Zim')
            # print(text_source_lines[0:3])
            self.metadata_lines_before_note = text_source_lines[0:3]
            del text_source_lines[0:3]

        if first_part1 in zim_wiki_tags and first_part2 in zim_wiki_tags and first_part3 not in zim_wiki_tags:
            # Удаляем первые 2 строчки
            # print('Найденые 2 строки метаданных Zim')
            # print(text_source_lines[0:2])
            self.metadata_lines_before_note = text_source_lines[0:2]
            del text_source_lines[0:2]

        if first_part1 in zim_wiki_tags and first_part2 not in zim_wiki_tags and first_part3 not in zim_wiki_tags:
            # Удаляем первую строчку
            # print('Найдена 1 строка метаданных Zim')
            # print(text_source_lines[0:1])
            self.metadata_lines_before_note = text_source_lines[0:1]
            del text_source_lines[0:1]

        # 4. Если осталась первая пустая строка - удаляем и её (она обычно остается после служебных)
        if len(text_source_lines) > 0 and not text_source_lines[0].strip():
            # Удаляем первую строчку
            # print('А ещё найдена пустая строка после метаданных Zim.')
            self.metadata_lines_before_note.append(text_source_lines[0])
            del text_source_lines[0:1]


        # print('self.metadata_lines_before_note:')
        # print(self.metadata_lines_before_note)

        # print('2 ### convert_zim_text_to_html_source:')
        # print(text)


        # x. Собираем контент заметки обратно в строки

        new_text_source_lines = []
        for one_line in text_source_lines:
            #new_text_source_lines.append(html.escape(one_line).replace(' ', self.space_symbol))
            new_text_source_lines.append(html.escape(one_line))

        # html_source = '\n'.join(new_text_source_lines)
        html_source = ''
        for one_line in new_text_source_lines:
            html_source += one_line + '\n'

        # А тут надо использовать системный перенос строк: os.linesep

        # html_source = '\n'.join(text_source_lines)

        # print('3 ### convert_zim_text_to_html_source:')
        # print('###'+html_source+'###')

        # html_source = urllib.request.quote(html_source)

        #self.health_bad_links(html_source)

     #   _classes = {'c': r'[^\s"<>\']'} # limit the character class a bit
     #   url_re = Re(r'''(
	    #    \b \w[\w\+\-\.]+:// %(c)s* \[ %(c)s+ \] (?: %(c)s+ [\w/] )?  |
	    #    \b \w[\w\+\-\.]+:// %(c)s+ [\w/]                             |
	    #    \b mailto: %(c)s+ \@ %(c)s* \[ %(c)s+ \] (?: %(c)s+ [\w/] )? |
	    #    \b mailto: %(c)s+ \@ %(c)s+ [\w/]                            |
	    #    \b %(c)s+ \@ %(c)s+ \. \w+ \b
     #   )''' % _classes, re.X | re.U)
	    ## Full url regex - much more strict then the is_url_re
	    ## The host name in an uri can be "[hex:hex:..]" for ipv6
	    ## but we do not want to match "[http://foo.org]"
	    ## See rfc/3986 for the official -but unpractical- regex

        # html_source = re.sub('(Created [^\n]*)', '<font id="created">\\1</font>', html_source)
        # Информация после заголовка о времени создания заметки.
        # Наследство Zim.
        html_source = re.sub('=\n(Created [^\n]*[\d]{4})', '=\n<font id="created">\\1</font>', html_source, re.M)


        # print()
        # print('После удаления служебных полей Zim:')
        # print(html_source)

        # html_source = re.sub('(Content-Type: text/x-zim-wiki)', '<!--', html_source)
        # html_source = re.sub('(======) (.*?) (======)\n', '--><font id=hide>\\1</font> <font id=head1>\\2</font>
        #  <font id=hide>\\3</font><br>', html_source)
        # html_source = re.sub('====== (.*?) ======\n', '--><h1>\\1</h1>', html_source)
        # html_source = re.sub('===== (.*?) =====', '<h2>\\1</h2>', html_source)
        # html_source = re.sub('==== (.*?) ====', '<h3>\\1</h3>', html_source)
        # html_source = re.sub('=== (.*?) ===', '<h4>\\1</h4>', html_source)
        # html_source = re.sub('== (.*?) ==', '<h5>\\1</h5>', html_source)
        # html_source = re.sub('= (.*?) =', '<h6>\\1</h6>', html_source)

        # FIXME: скрытие служебных полей начала контента вики сделано неправильно, рассчитано только на 1 H1
        # html_source = re.sub('====== (.*?) ======', '--><font id=head1>\\1</font>', html_source)



        # html_source = re.sub('====== (.*?) ======', '<font id=head1>\\1</font>', html_source)
        # html_source = re.sub('===== (.*?) =====', '<font id=head2>\\1</font>', html_source)
        # html_source = re.sub('==== (.*?) ====', '<font id=head3>\\1</font>', html_source)
        # html_source = re.sub('=== (.*?) ===', '<font id=head4>\\1</font>', html_source)
        # html_source = re.sub('== (.*?) ==', '<font id=head5>\\1</font>', html_source)
        # html_source = re.sub('= (.*?) =', '<font id=head6>\\1</font>', html_source)

        #html_source = re.sub('====== (.*?) ======', '<font id=head1>\\1</font>', html_source)
        #html_source = re.sub('===== (.*?) =====', '<font id=head2>\\1</font>', html_source)
        #html_source = re.sub('==== (.*?) ====', '<font id=head3>\\1</font>', html_source)
        #html_source = re.sub('=== (.*?) ===', '<font id=head4>\\1</font>', html_source)
        #html_source = re.sub('== (.*?) ==', '<font id=head5>\\1</font>', html_source)
        #html_source = re.sub('= (.*?) =', '<font id=head6>\\1</font>', html_source)

        # Заголовки после переноса строки
        html_source = re.sub('\n====== (.*?) ======', '<div id=head1>\\1</div>', html_source)
        html_source = re.sub('\n===== (.*?) =====', '<div id=head2>\\1</div>', html_source)
        html_source = re.sub('\n==== (.*?) ====', '<div id=head3>\\1</div>', html_source)
        html_source = re.sub('\n=== (.*?) ===', '<div id=head4>\\1</div>', html_source)
        html_source = re.sub('\n== (.*?) ==', '<div id=head5>\\1</div>', html_source)
        html_source = re.sub('\n= (.*?) =', '<div id=head6>\\1</div>', html_source)

        # Те-же заголовки но в самом начале заметки
        html_source = re.sub('^====== (.*?) ======', '<div id=head1>\\1</div>', html_source)
        html_source = re.sub('^===== (.*?) =====', '<div id=head2>\\1</div>', html_source)
        html_source = re.sub('^==== (.*?) ====', '<div id=head3>\\1</div>', html_source)
        html_source = re.sub('^=== (.*?) ===', '<div id=head4>\\1</div>', html_source)
        html_source = re.sub('^== (.*?) ==', '<div id=head5>\\1</div>', html_source)
        html_source = re.sub('^= (.*?) =', '<div id=head6>\\1</div>', html_source)


        # html_source = re.sub('====== (.*?) ======', '--><p id=head1>\\1</p>', html_source)
        # html_source = re.sub('===== (.*?) =====', '<p id=head2>\\1</p>', html_source)
        # html_source = re.sub('==== (.*?) ====', '<p id=head3>\\1</p>', html_source)
        # html_source = re.sub('=== (.*?) ===', '<p id=head4>\\1</p>', html_source)
        # html_source = re.sub('== (.*?) ==', '<p id=head5>\\1</p>', html_source)
        # html_source = re.sub('= (.*?) =', '<p id=head6>\\1</p>', html_source)

        # print()
        # print('После замены заголовков:')
        # print(html_source)

        # TODO: re.search, groups - обнаружение и сохранение позиций вики-форматирования

        # 'strong':   Re('\*\*(?!\*)(.+?)\*\*'),
        #html_source = re.sub('\*\*(.*?)\*\*', '<strong>\\1</strong>', html_source)
        html_source = re.sub(r'\*\*(?!\*)(.*?)\*\*', '<strong>\\1</strong>', html_source)

        #html_source = re.sub('//(.*?)//', '<i>\\1</i>', html_source)
        html_source = re.sub(r'//(?!/)(.*?)//', '<i>\\1</i>', html_source)

        # 'strike':   Re('~~(?!~)(.+?)~~'),


        # Замена / на альтернативное его обозначение для редактора, чтобы замаскировать ссылку внутри другого форматирования
        #html_source = re.sub('~~(.*?)://(.*?)~~', '<s>\\1:&#x2F;&#x2F;\\2</s>', html_source)

        #html_source = re.sub('~~(.*?)~~', '<s>\\1</s>', html_source)
        html_source = re.sub(r'~~(?!~)(.+?)~~', '<s>\\1</s>', html_source)

        # 'emphasis': Re('//(?!/)(.+?)//'),

        # html_source = re.sub('\n\* ([^\n]*)', '<ul><li>\\1</li></ul>', html_source)
        #html_source = re.sub('\n\* ([^\n]*)', '<ul><li>\\1</li></ul>', html_source)

        # Меняем астериски в начале строки на li
        html_source = re.sub('\n\* ([^\n]*)', '\n<ul><li>\\1</li></ul>', html_source)
        # Объединяем соседние ul
        #print('</ul><ul>: %s' % html_source.find('</ul>\n<ul>') )
        html_source = html_source.replace('</ul>\n<ul>', '')
        # Финальная очистка вокруг ul
        # Удаляем перенос строки перед ul
        #print('\n<ul>: %s' % html_source.find('\n<ul>') )
        html_source = html_source.replace('\n<ul>', '<ul>')
        # Удаляем перенос строки после ul
        #print('</ul>\n: %s' % html_source.find('</ul>\n') )
        html_source = html_source.replace('</ul>\n', '</ul>')

        # Замена переноса строк в конце ul
        #html_source = re.sub('</ul>\n\n', '</ul>\n', html_source)



        # 'code':     Re("''(?!')(.+?)''"),
        # html_source = re.sub("''(?!')(.+?)''", '<font id="code">\\1</font>', html_source)
        # html_source = re.sub("''(?!')(.+?)''", '<font id="code">\\1</font>', html_source)

        # Замена / на альтернативное его обозначение для редактора, чтобы замаскировать ссылку внутри другого форматирования
        #html_source = re.sub('&#x27;&#x27;(.*?)://(.*?)&#x27;&#x27;', '<font id="code">\\1:&#x2F;&#x2F;\\2</font>', html_source)

        html_source = re.sub("&#x27;&#x27;(?!')(.+?)&#x27;&#x27;", '<font id="code">\\1</font>', html_source)
        #html_source = re.sub(r"''(?!')(.+?)''", '<font id="code">\\1</font>', html_source)

        # 'mark':     Re('__(?!_)(.+?)__'),
        #html_source = re.sub('__(?!_)(.+?)__', '<font id="mark">\\1</font>', html_source)
        html_source = re.sub(r'__(?!_)(.*?)__', '<font id="mark">\\1</font>', html_source)

        # Внутренний линк
        # 'link':     Re('\[\[(?!\[)(.+?)\]\]'),
        #html_source = re.sub('\[\[(?!\[)(.+?)\]\]', '<a href="\\1">\\1</a>', html_source)
        html_source = re.sub(r'\[\[(?!\[)(.*?)\]\]', '<a href="\\1">\\1</a>', html_source)

        # Метка
        #TAG, r'(?<!\S)@\w+',

        # Rule(SUBSCRIPT, r'_\{(?!~)(.+?)\}')
		# Rule(SUPERSCRIPT, r'\^\{(?!~)(.+?)\}')


        # Внешний линк
        # html_source = re.sub('(http://[^ \n]*)','<a href="\\1">\\1</a>', html_source)
        html_source = re.sub('([^ \n]*://[^ \n]*)', '<a href="\\1">\\1</a>', html_source)

        # 'img':      Re('\{\{(?!\{)(.+?)\}\}'),
        #html_source = re.sub('\{\{(?!\{)(.+?)\}\}', '<img src="\\1">', html_source)
        html_source = re.sub(r'\{\{(?!\{)(.*?)\}\}', '<img src="\\1">', html_source)
        #html_source = re.sub('<img src="~', '<img src="' + path_to_home, html_source)

        # print()
        # print('После остальной замены:')
        # print(html_source)

        # TODO: . Сделать превращение в линк электронной почты и её сохранение

        # 'tag':        Re(r'(?<!\S)@(?P<name>\w+)\b', re.U),
        # 'sub':	    Re('_\{(?!~)(.+?)\}'),
        # 'sup':	    Re('\^\{(?!~)(.+?)\}'),
        # \n --> <br>

        html_source = html_source.replace('\n', '<br>')
        # html_source = html_source.replace('\n', '</p><p>')

        html_source = '<html>%s<body>%s</body></html>' % (Theme.html_theme_head, html_source,)

        # print('Итоговый вид html:')
        # print(html_source)

        return html_source









    def convert_html_source_to_zim_text(self, html_text):
        # Конвертируем текст из редактора заметки в формат zim
        text = html_text

        # Оригинальный код был из функции save_note

        # begin_of_zim_note = '\n'.join(self.metadata_lines_before_note)
        begin_of_zim_note = ''
        for one_data_line in self.metadata_lines_before_note:
            begin_of_zim_note += one_data_line + '\n'

        text = self.clear_note_html_cover(text)

        # Удаляем виртуальные начала строк
        text = re.sub('<p .*?>', '', text)
        # Удаляем последнее закрытие </p>

        # profiler.checkpoint('Проводим склейку соседних span')

        # Склеиваем одинаковые соседние span
        text = self.union_concat_ident_span(text)

        # Применяем вики-форматирование

        # profiler.checkpoint('Заменяем html-теги заголовков на вики-форматирование')

        # Заголовок
        text = re.sub(text_format.editor_h1_span + '(.*?)</span>', '====== \\1 ======', text)
        text = re.sub(text_format.editor_h2_span + '(.*?)</span>', '===== \\1 =====', text)
        text = re.sub(text_format.editor_h3_span + '(.*?)</span>', '==== \\1 ====', text)
        text = re.sub(text_format.editor_h4_span + '(.*?)</span>', '=== \\1 ===', text)
        text = re.sub(text_format.editor_h5_span + '(.*?)</span>', '== \\1 ==', text)
        text = re.sub(text_format.editor_h6_span + '(.*?)</span>', '= \\1 =', text)

        # Подчеркнутый (выделенный)
        text = re.sub(text_format.editor_mark_span + '(.*?)</span>', '__\\1__', text)

        # Код
        text = re.sub(text_format.editor_code_span + '(.*?)</span>', '\'\'\\1\'\'', text)


        root_logger.info('\nПредварительный исходник результата сохранения в формате Zim:')
        root_logger.info('=' * 40)
        root_logger.info(text)
        root_logger.info('=' * 40)

        # profiler.checkpoint('Заменяем html-теги ссылок на вики-форматирование')

        # Ссылка
        # <a href="...">
        text = self.make_all_links_to_wiki_format(text)

        # profiler.checkpoint('Заменяем html-теги основной разметки на вики-форматирование')

        # Нумерованный список
        #

        # Зачеркнутый текст
        # <span style=" font-family:'Sans'; font-size:15px; text-decoration: line-through; color:#aaaaaa;">
        # editor_strikethrough_span
        text = re.sub('<span [^>]*text-decoration: line-through;.*?>(.*?)</span>', '~~\\1~~', text)
        # Жирный
        # <span style=" font-family:'Sans'; font-size:15px; font-weight:600;">
        text = re.sub('<span [^>]*font-weight:600;.*?>(.*?)</span>', '**\\1**', text)
        # Наклонный
        # <span style=" font-family:'Sans'; font-size:15px; font-style:italic;">
        text = re.sub('<span [^>]*font-style:italic;.*?>(.*?)</span>', '//\\1//', text)

        # Картинка
        # <img src="/home/vyacheslav//Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png" />
        # -->
        # {{~/Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png}}
        # Закомментировал, не работает сейчас, выдает ошибку про незакрытый \U. Наверное, это в пути к картинке.
        # text = re.sub('<img src="'+path_to_home+'(.*?)" />', '{{~\\1}}', text)
        text = re.sub('<img src="(.*?)" />', '{{\\1}}', text)


        # Ненумерованный список
        # <ul style="..."><li style="..."><span style="..">Пункт 1</span></li></ul>
        # text = re.sub('<ul .*?><li .*?>(.*?)</li></ul>', '* \\1<br />', text)
        text = re.sub('<li .*?>(.*?)</li>', '* \\1<br />', text)
        #text = re.sub('<ul .*?>(.*?)</ul>', '\\1', text)

        text = re.sub('<ul .*?>(.*?)</ul>', '\\1', text, re.MULTILINE)

        # Чистим остатки
        # profiler.checkpoint('Чистим остатки html разметки')

        # Удаление оставшихся span
        text = re.sub('<span .*?>', '', text)
        text = text.replace('</span>', '')

        # Заменяем окончания на перенос строки
        text = text.replace('</p>', '\n')
        # Заменяем html переносы строк на обычные
        text = text.replace('<br />', '\n')

        # text = text.replace('<a name="created"></a>','')
        text = re.sub('<a name="(.*?)"></a>', '', text)

        # profiler.stop()

        # text = urllib.request.unquote(text)
        #text = text.replace(self.space_symbol, ' ')
        text = html.unescape(text)

        # Добавляем начало файла как у Zim
        text = begin_of_zim_note + text


        root_logger.info('\nОкончательный исходник результата сохранения в формате Zim:')
        root_logger.info('=' * 40)
        root_logger.info(text)
        root_logger.info('=' * 40)


        return text


    def save_note(self):
        # profiler.start('Начинаем сохранение заметки')

        filename = main_window.current_open_note_link

        print('Сохраняем файл %s' % filename)

        # Обновляем запись в базе
        app_settings.state_db_connection.execute("UPDATE file_recs SET last_change=?  WHERE filename=?",
                                    (datetime.now(), filename))
        app_settings.state_db.commit()

        # Добавляем суффикс к имени файла, при этом сохраняя оригинальное его расширение
        filename_wo_ext = os.path.splitext(filename)[0]
        filename_ext_only = os.path.splitext(filename)[-1]
        filename_suffix = '-saved'
        if not filename_suffix in filename_wo_ext:
            # Если суффикса ещё нет в имени файла- добавляем его. Иначе оставляем без изменений.
            filename = filename_wo_ext + filename_suffix + filename_ext_only

        # # Сохраняем текущую заметку с суффиксом -rt
        # tmp_str = main_window.current_open_note_link[:-len('.txt')]
        # # print ('tmp_str: '+tmp_str)
        # rt_suffix = '-rt'
        # if tmp_str[-len(rt_suffix):] == rt_suffix:
        #    filename = main_window.current_open_note_link
        # else:
        #    filename = tmp_str+rt_suffix+'.txt'
        # # print ('filename: '+filename)
        # # return 0
        # # filename = main_window.current_open_note_link+'2'

        note_source = main_window.textBrowser_Note.toHtml()
        note_source = self.convert_html_source_to_zim_text(note_source)

        # print('self.metadata_lines_before_note:')
        # print(self.metadata_lines_before_note)

        # begin_of_zim_note = '\n'.join(self.metadata_lines_before_note)
        # # Проверка бага с Линукс-переносом строки, когда последняя строка не сохраняется при конвертации из html
        # if self.metadata_lines_before_note[len(self.metadata_lines_before_note)-1]=='\n':
        #    begin_of_zim_note += '\n'
        # print('begin_of_zim_note: ###%s###' % begin_of_zim_note)


        if main_window.actionSave_also_note_HTML_source.isChecked():
            filename_html = main_window.current_open_note_link.replace('.txt', '.html')
            f = open(filename_html, "w")
            f.writelines(note_source)
            f.close()

        # note_source = self.clear_note_html_cover(note_source)

        # # Удаляем виртуальные начала строк
        # note_source = re.sub('<p .*?>', '', note_source)
        # # Удаляем последнее закрытие </p>

        # # profiler.checkpoint('Проводим склейку соседних span')

        # # Склеиваем одинаковые соседние span
        # note_source = self.union_concat_ident_span(note_source)

        # # Применяем вики-форматирование

        # # profiler.checkpoint('Заменяем html-теги заголовков на вики-форматирование')

        # # Заголовок
        # note_source = re.sub(text_format.editor_h1_span+'(.*?)</span>', '====== \\1 ======', note_source)
        # note_source = re.sub(text_format.editor_h2_span+'(.*?)</span>', '===== \\1 =====', note_source)
        # note_source = re.sub(text_format.editor_h3_span+'(.*?)</span>', '==== \\1 ====', note_source)
        # note_source = re.sub(text_format.editor_h4_span+'(.*?)</span>', '=== \\1 ===', note_source)
        # note_source = re.sub(text_format.editor_h5_span+'(.*?)</span>', '== \\1 ==', note_source)
        # note_source = re.sub(text_format.editor_h6_span+'(.*?)</span>', '= \\1 =', note_source)

        # # Подчеркнутый (выделенный)
        # note_source = re.sub(text_format.editor_mark_span+'(.*?)</span>', '__\\1__', note_source)

        # # Код
        # note_source = re.sub(text_format.editor_code_span+'(.*?)</span>', '\'\'\\1\'\'', note_source)

        # # profiler.checkpoint('Заменяем html-теги ссылок на вики-форматирование')

        # # Ссылка
        # # <a href="...">
        # note_source = self.make_all_links_to_wiki_format(note_source)

        # # profiler.checkpoint('Заменяем html-теги основной разметки на вики-форматирование')

        # # Нумерованный список
        # #

        # # Зачеркнутый текст
        # # <span style=" font-family:'Sans'; font-size:15px; text-decoration: line-through; color:#aaaaaa;">
        # # editor_strikethrough_span
        # note_source = re.sub('<span [^>]*text-decoration: line-through;.*?>(.*?)</span>', '~~\\1~~', note_source)
        # # Жирный
        # # <span style=" font-family:'Sans'; font-size:15px; font-weight:600;">
        # note_source = re.sub('<span [^>]*font-weight:600;.*?>(.*?)</span>', '**\\1**', note_source)
        # # Наклонный
        # # <span style=" font-family:'Sans'; font-size:15px; font-style:italic;">
        # note_source = re.sub('<span [^>]*font-style:italic;.*?>(.*?)</span>', '//\\1//', note_source)

        # # Картинка
        # # <img src="/home/vyacheslav//Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png" />
        # # -->
        # # {{~/Dropbox/Projects/Relanotes/relanotes-0.02/mclaren.png}}
        # # Закомментировал, не работает сейчас, выдает ошибку про незакрытый \U. Наверное, это в пути к картинке.
        # # note_source = re.sub('<img src="'+path_to_home+'(.*?)" />', '{{~\\1}}', note_source)
        # note_source = re.sub('<img src="(.*?)" />', '{{\\1}}', note_source)


        # # Ненумерованный список
        # # <ul style="..."><li style="..."><span style="..">Пункт 1</span></li></ul>
        # # note_source = re.sub('<ul .*?><li .*?>(.*?)</li></ul>', '* \\1<br />', note_source)
        # note_source = re.sub('<li .*?>(.*?)</li>', '* \\1<br />', note_source)
        # note_source = re.sub('<ul .*?>(.*?)</ul>', '\\1', note_source)

        # # Чистим остатки
        # # profiler.checkpoint('Чистим остатки html разметки')

        # # Удаление оставшихся span
        # note_source = re.sub('<span .*?>', '', note_source)
        # note_source = note_source.replace('</span>', '')

        # # Заменяем окончания на перенос строки
        # note_source = note_source.replace('</p>', '\n')
        # # Заменяем html переносы строк на обычные
        # note_source = note_source.replace('<br />', '\n')

        # # note_source = note_source.replace('<a name="created"></a>','')
        # note_source = re.sub('<a name="(.*?)"></a>', '', note_source)

        # # profiler.stop()

        # # Добавляем начало файла как у Zim
        # note_source = begin_of_zim_note+note_source

        # Записываем результат преобразования исходника заметки в файл

        # f = open(filename, "w", "utf-8")
        # f.writelines(note_source)
        # f.close()

        #print("We will save notes to %s" % filename)

        # Новое сохранение с использование кодировки UTF8
        fileObj = codecs.open(filename, "w", "utf-8")
        for one_line in note_source:
            fileObj.write(one_line)
        fileObj.close()


        # Код обновления специального меню сниппетов, если сохранен
        # такой специальный файл
        if filename == app_settings.snippets_filename:
            main_window.show_snippets()

        main_window.statusbar.showMessage('Note saved as ' + filename)

        # TODO: Запуск перебора всех заметок и сохранения их в альтернативный каталог
        # TODO: Diff всех файлов заметок - оригиналов и сохраненных, и коррекция сохранения.

        # TODO: ... А если форматирование на несколько строк?

    def show_note_multiaction_win_button(self):
        # if main_window.textBrowser_Note.isVisible():
        if note.is_visible():
            self.show_note_multiaction_win(main_window.current_open_note_link)
        else:
            self.show_note_multiaction_win(notelist.items_cursor_url.split('?')[1])

    def show_note_multiaction_win(self, note_filename=''):
        # if note_filename == '':
        #    note_filename =

        # Получаем корректный путь к файлу из линка со всякими %2U
        note_filename = get_correct_filename_from_url(note_filename)

        notemultiaction_win.labelNoteFileName.setText(note_filename)
        notemultiaction_win.lineEdit.setText('')
        notemultiaction_win.lineEdit.setFocus()
        notemultiaction_win.show()

    def paste_as_text(self):
        self.paste_as_text_once = True
        main_window.textBrowser_Note.paste()

    def __init__(self):  # Note class
        # Прописываем реакцию на сигналы
        # QtCore.QObject.connect(main_window.textBrowser_Note, QtCore.SIGNAL("textChanged()"), text_format.update_ui)
        main_window.textBrowser_Note.textChanged.connect(text_format.update_ui)
        # QtCore.QObject.connect(main_window.textBrowser_Note, QtCore.SIGNAL("cursorPositionChanged()"), text_format.update_ui)
        main_window.textBrowser_Note.cursorPositionChanged.connect(text_format.update_ui)

        # QtCore.QObject.connect(main_window.doc_source, QtCore.SIGNAL("textChanged()"), text_format.updateUI)
        # QtCore.QObject.connect(main_window.doc_source, QtCore.SIGNAL("cursorPositionChanged()"), text_format.updateUI)

        # Прописываем реакцию на действия
        main_window.actionBold.triggered.connect(text_format.bold)
        main_window.actionItalic.triggered.connect(text_format.italic)
        main_window.actionStrikethrough.triggered.connect(text_format.strikethrough)
        main_window.actionCode.triggered.connect(text_format.code)
        main_window.actionMark.triggered.connect(text_format.mark)

        main_window.action_ClearFormat.triggered.connect(text_format.clear_format)
        main_window.actionHeading_1.triggered.connect(text_format.h1)
        main_window.actionHeading_2.triggered.connect(text_format.h2)
        main_window.actionHeading_3.triggered.connect(text_format.h3)
        main_window.actionHeading_4.triggered.connect(text_format.h4)
        main_window.actionHeading_5.triggered.connect(text_format.h5)
        main_window.actionHeading_6.triggered.connect(text_format.h6)

        main_window.actionSave_note.triggered.connect(self.save_note)
        main_window.actionNote_multiaction.triggered.connect(self.show_note_multiaction_win_button)

        main_window.actionPaste_as_text.triggered.connect(self.paste_as_text)

        # Скрываем дополнительные фреймы
        main_window.frameSearchInNote.setVisible(False)