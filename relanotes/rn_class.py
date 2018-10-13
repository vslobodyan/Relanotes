"""Модуль, в котором обозначены все основные глобальные переменные-классы, которые используются во всей программе"""

class RN_App:
    """Основной класс приложения RelaNotes"""

    profiler = None

    loggers = None

    settings = None

    main_window = None

    table_of_note_contents = None

    notelist = None

    text_format = None

    note = None

    opened_notes = None

    notemultiaction_win = None

    clear_history_win = None

    calculator_win = None

    preferences_win = None

    themes = None

    tests = None

    def __init__(self):

        from relanotes.clear_history_dialog import ClearHistoryDialog
        from relanotes.main_window import Main_Window
        from relanotes.note import Note
        from relanotes.note_multiaction_window import NoteMultiactionWindow
        from relanotes.notelist import Notelist
        from relanotes.preferences_window import PreferencesWindow
        from relacalc import main as relacalc_main

        from relanotes.settings import Settings
        from relanotes.table_of_note_contents import Table_of_note_contents
        from relanotes.text_format import Text_Format

        # from relanotes.event_filter import MyEventFilter
        # from relanotes.mytextbrowser import MyTextBrowser
        from relanotes.profiler import Profiler
        from relanotes.tests import App_Tests
        from relanotes.log import Loggers

        from relanotes.themes import Themes

        self.profiler = Profiler()

        self.loggers = Loggers()

        self.settings = Settings()

        self.main_window = Main_Window(self)

        self.table_of_note_contents = Table_of_note_contents(self)

        self.notelist = Notelist(self)

        self.text_format = Text_Format(self)

        self.note = Note(self)

        self.opened_notes = []

        self.notemultiaction_win = NoteMultiactionWindow(self)

        self.clear_history_win = ClearHistoryDialog(self)

        self.calculator_win = relacalc_main.CalculatorWindow(self)

        self.preferences_win = PreferencesWindow(self)

        self.themes = Themes(self)

        self.tests = App_Tests(self)


