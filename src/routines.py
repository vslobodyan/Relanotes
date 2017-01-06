# -*- coding: utf-8 -*-

''' Модуль рутин  для основной программы '''

import os
import urllib.request


def give_correct_path_under_win_and_other(path_to_check):
    # Важная функция исправления внутреннего представления путей под Win

    correct_path = path_to_check
    # print ('DEBUG: os.path.sep: %s ' % os.path.sep )
    print ('DEBUG: path_to_check: %s' % path_to_check )

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
            print ('DEBUG: путь был исправлен с %s на %s' % (path_to_check, correct_path) )
    return correct_path



def get_correct_filename_from_url(filename):
    return urllib.request.unquote(filename)
