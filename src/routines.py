# -*- coding: utf-8 -*-

''' Модуль рутин  для основной программы '''

import os
import sys
import urllib.request
import difflib


def give_correct_path_under_win_and_other(path_to_check):
    # Важная функция исправления внутреннего представления путей под Win

    correct_path = path_to_check
    #print ('DEBUG: path_to_check: %s' % path_to_check )

    # Рекомендуемый в некоторых местах путь решения:
    # path = QDir::fromNativeSeparators( path );
    # или
    # QDir::toNativeSeparators()
    # http://doc.qt.io/qt-5/qdir.html#toNativeSeparators

    if path_to_check and os.path.sep == '\\':
        # Работаем в случае если это сепаратор Windows и путь к заметкам не пустой
        if os.path.sep not in path_to_check:
            # Обнаружен признак отсутствия правильного разделителя в пути к заметкам
            # Разбиваем путь по обратному слешу и собираем обратно правильным образом
            correct_path = os.path.sep.join( path_to_check.split('/') )
            #print ('DEBUG: путь был исправлен с %s на %s' % (path_to_check, correct_path) )
    return correct_path


def get_path_to_app():
    # Получаем путь к основным выполняемым файлам приложения
    return os.path.split(os.path.abspath(sys.argv[0]))[0]

def get_correct_filename_from_url(filename):
    return urllib.request.unquote(filename)


#def get_diff_text(old, new, filename1, filename2):
#    """Return text of unified diff between old and new."""
#    newline = '\n'
#    diff = difflib.unified_diff(
#        old, new,
#        filename1,
#        filename2,
#        lineterm=newline)

#    text = ''
#    for line in diff:
#        text += line

#        # Work around missing newline (http://bugs.python.org/issue2142).
#        if text and not line.endswith(newline):
#            text += newline + r'\ No newline at end of file' + newline

#    return text

#def get_diff_text(old, new):
#        differ = difflib.Differ()
#        text = ''
#        for line in differ.compare(old, new):
#            if line.startswith(" "):
#                print(line[2:], end="")
#                text += line[2:]
#        return text

#def get_diff_text(old, new, filename1, filename2):
#    #text = ''
#    #diff = difflib.ndiff(old,new)
#    #for i,line in enumerate(diff):
#    #    if line.startswith(' '):
#    #        continue
#    #    #sys.stdout.write('My count: {}, text: {}'.format(i,line))
#    #    text += 'My count: {}, text: {}'.format(i,line)

#    #for line in diff:
#    #    if line.startswith('-'):
#    #        text += line
#    #    elif line.startswith('+'):
#    #        text += '\t\t'+line

#    text = difflib.unified_diff(old, new, filename1, filename2)
#    sys.stdout.writelines(text)

#    return text


def get_diff_text(old_text, new_text, old_filename, new_filename):
    # Функция сравнения текста.

    # Поскольку unified_diff требует листы, то производим предварительное разбиение текста на листы построчные.
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()

    #d = difflib.Differ()
    #diff = d.compare(old, new)

    #diff = difflib.ndiff(old, new)
    #print( '\n'.join(diff) )


    #diff = difflib.unified_diff(old, new, lineterm='')
    #print('\n'.join(list(diff)) )

    #print (os.linesep.join(difflib.unified_diff(old,new)) )

    #print ( '\n'.join(list(diff)) )

    #for line in diff:
    #        if line.startswith(" "):
    #            print(line[2:], end="")


    diff_generator = difflib.unified_diff(old_lines, new_lines, old_filename, new_filename, n = 0)
    diff = [line for line in diff_generator]
    #processedDiff = self._processOutputText(diff, wcThreshold)
    processedDiff = '\n'.join(diff)

    return processedDiff
