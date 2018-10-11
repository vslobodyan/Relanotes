import time


class Profiler():
    start_time = 0
    start_time_overall = 0

    def start(self, text):
        self.start_time = time.time()
        self.start_time_overall = time.time()
        print(text)

    def checkpoint(self, text):
        print("Время выполнения: %.03f s" % (time.time() - self.start_time), '\n')
        print(text)
        self.start_time = time.time()

    def stop(self, text=''):
        print("Время выполнения: %.03f s" % (time.time() - self.start_time), '\n')
        print("Общее время работы профилируемого кода : %.03f s" % (time.time() - self.start_time_overall))
        print(text, '\n')