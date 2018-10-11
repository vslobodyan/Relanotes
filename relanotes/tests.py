import codecs
import os

from PyQt5 import QtWidgets

# from relanotes.relanotes import notelist, main_window, app_settings, note
from relanotes.routines import give_correct_path_under_win_and_other, get_diff_text


class App_Tests():
    # Класс для внутренних тестов программы. В том числе вызываемых через меню.

    path_to_notes_convertation = ''  # Путь к каталогу, в котором надо проводить тесты
    items = []      # Массив элементов, для которого надо провести тесты

    def collect_items(self, from_directory=False, change_path = False, from_notelist=False):
        # Собираем элементы для последующего тестирования
        self.items = []
        if from_notelist:
            for one_item in notelist.items:
                self.items.append(one_item['filename'])
                #print('one_item %s' % one_item['filename'])

        if from_directory:
            # Диалог выбора пути для сканирования
            if change_path or not self.path_to_notes_convertation:
                print('Предлагаем смену каталога для теста')
                new_path = give_correct_path_under_win_and_other(QtWidgets.QFileDialog.getExistingDirectory(main_window, "Select Directory with your Notes for Test", '' , QtWidgets.QFileDialog.ShowDirsOnly))
                print('path_to_notes_convertation: ##%s##' % new_path)
                #return 0
                if not new_path:
                    print('Каталог не выбран.')
                    return 0
                else:
                    print('Выбран новый каталог для тестов: %s' % new_path)
                    self.update_path_info_for_notes_convertation(new_path, save=True)
            else:
                print('Готовим тест без смены каталога')
            #return 0
            #if not app_settings.path_to_notes:
            #    app_settings.path_to_notes = "D:\Test\\Notes"
            print('Пользователь выбрал для теста каталог %s' % self.path_to_notes_convertation)

            for root, dirs, files in os.walk(self.path_to_notes_convertation):
                for file in files:
                    if os.path.splitext(file)[-1] in notelist.allowed_note_files_extensions:
                    #if file.endswith('.txt'):
                        filename = os.path.join(root, file)
                        self.items.append(filename)
                        print('filename %s' % filename)




    def update_path_info_for_notes_convertation(self, new_path, save=False):
        # Обновляем информацию о новом каталоге для теста
        self.path_to_notes_convertation = give_correct_path_under_win_and_other(new_path)
        # Обновляем текст в действии с запуском в последнем каталоге, чтобы там отображался наш новый путь
        if self.path_to_notes_convertation:
            main_window.actionRun_test_for_notes_convertation_in_last_directory.setText('Run test for notes convertation in %s' % self.path_to_notes_convertation)
        else:
            main_window.actionRun_test_for_notes_convertation_in_last_directory.setText('Run test for notes convertation in last directory')
        if save:
            # Сохраняем переменную с новым каталогом
            app_settings.settings.setValue('path_to_notes_convertation_test', self.path_to_notes_convertation)
            app_settings.settings.sync()


    def test_notes_items_for_health_bad_link(self):
        # Тестовая функция, позволяющая проверить результативность функции исправления испорченных ранее ссылок
        print('Запускаем функцию тестирования лечения испорченных ссылок')

        for filename in self.items:
            fileObj = codecs.open(filename, "r", "utf-8")
            original_text = fileObj.read()
            fileObj.close()

            note.health_bad_links(filename, original_text)

        print()
        print('Тестирование завершено.')


    def test_notes_items_for_convertation(self):
        # Тестовая функция, позволяющая проверить корректность конвертации форматирования при открытии и сохранении заметок
        print('Запускаем функцию тестирования конвертации форматирования при открытии и сохранении заметок')

        for filename in self.items:
            fileObj = codecs.open(filename, "r", "utf-8")
            original_text = fileObj.read()
            fileObj.close()

            # Загружаем файл в окно редактора
            main_window.open_file_in_editor(filename, dont_save_in_history=True)

            # Конвертируем zim text в html для редактора
            html_source = note.convert_zim_text_to_html_source(original_text)
            # Устанавливаем html-исходник для редактора
            main_window.doc_source.setHtml(html_source)
            main_window.textBrowser_Note.setDocument(main_window.doc_source)


            # Конвертируем файл как-бы для сохранения на диск
            note_source = main_window.textBrowser_Note.toHtml()
            saved_text = note.convert_html_source_to_zim_text(note_source)

            # Сравниваем оригинал и "сохраненный" вариант
            diff_result = get_diff_text(original_text, saved_text, filename, filename + '-saved')
            if diff_result:
                print()
                # print('Результат сравнения:')
                print(diff_result)
                # for line in diff_result:
                #    print(line)
            else:
                print('.', end="", flush=True)

        print()
        print('Тестирование завершено.')

    def health_bad_links_for_notes_from_notelist(self):
        # Выполняем тест для текущего списка заметок
        self.collect_items(from_notelist=True)
        self.test_notes_items_for_health_bad_link()

    def notes_convertation_for_notelist(self):
        # Выполняем тест для текущего списка заметок
        self.collect_items(from_notelist=True)
        self.test_notes_items_for_convertation()

    def notes_convertation_for_directory(self, change_path=False):
        # Выполняем тест для директории из настроек
        self.collect_items(from_directory=True, change_path=change_path)
        self.test_notes_items_for_convertation()

    def notes_convertation_change_path(self):
        self.notes_convertation_for_directory(change_path=True)


    def __init__(self):
        print('Инициализация класса тестов')

        # Получение из настроек пути к каталогу тестов
        new_path = app_settings.settings.value('path_to_notes_convertation_test')
        self.update_path_info_for_notes_convertation(new_path)

        main_window.actionRun_test_for_notes_convertation_in_last_directory.triggered.connect(self.notes_convertation_for_directory)
        main_window.actionRun_test_notes_convertation_for_notelist.triggered.connect(self.notes_convertation_for_notelist)

        main_window.actionSelect_another_directory_and_run_test_for_notes_convertation.triggered.connect(self.notes_convertation_change_path)

        main_window.actionRun_test_health_bad_links_for_notes_from_notelist.triggered.connect(self.health_bad_links_for_notes_from_notelist)