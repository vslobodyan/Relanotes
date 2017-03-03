# -*- coding: utf-8 -*-

# Модуль для компиляции файлов UI, вместо старых .bat и .sh

from src.routines import *
import subprocess

# Получаем и переходим в каталог программы
path_to_app = get_path_to_app()
os.chdir(path_to_app)
path_to_ui_files = os.path.join(path_to_app, 'src/ui/')
path_to_ui_files = give_correct_path_under_win_and_other(path_to_ui_files)
allowed_note_ui_files_extensions = ['.ui']

ui_files = []

print('We will compile all UI files with %s extensions under %s path' % (allowed_note_ui_files_extensions, path_to_ui_files) )

def run_proc(cmd):
    subprocess.run(cmd, shell=True, check=True)

print('Compiling Resources file')
run_proc("pyrcc5 resources/resources.qrc -o resources/resources_rc.py")

# Обходим указанный каталог и собираем все ui файлы

for root, dirs, files in os.walk(path_to_ui_files):
    for file in files:
        # print('Найдено во время обхода: %s' % os.path.join(root, file))
        if os.path.splitext(file)[-1] in allowed_note_ui_files_extensions:
            #print('Найдено во время обхода: %s' % file)
            filename_wo_ext = os.path.splitext(file)[0]
            #print('Имя файла без расширения: %s' % filename_wo_ext)
            #print('Найден файл UI для %s' % filename_wo_ext)
            ui_files.append(filename_wo_ext)

for ui_file in ui_files:
    print('Compiling UI file for %s' % ui_file)
    cmd = 'pyuic5 "src/ui/%s.ui" --import-from "resources" -o "src/ui/%s.py"'% (ui_file, ui_file)
    run_proc(cmd)


#print('Done.\n\nPress any key to exit..')
#input()