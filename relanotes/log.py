import logging


class Loggers():
    """Класс логеров программы. С конструктором."""

    root = ''

    def create(self, level, filename):
        # Включаем логирование
        new_logger = logging.getLogger()
        new_logger.setLevel(level)
        handler = logging.FileHandler(filename, 'w', 'utf-8')  # or whatever
        # formatter = logging.Formatter('%(name)s %(message)s') # or whatever
        # handler.setFormatter(formatter) # Pass handler as a parameter, not assign
        new_logger.addHandler(handler)
        return new_logger

    def __init__(self):
        pass
