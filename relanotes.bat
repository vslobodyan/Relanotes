
REM Скрипт можно запускать откуда угодно.
REM Он сам перейдет в свою папку и запустит нужный файл.

REM Папка, из которой запустили скрипт
REM @echo cd = %cd%

REM Папка, в которой находится скрипт
REM @echo dp0 = %~dp0

REM Переходим в папку, в которой находится скрипт и основной запускаемый Питон-файл.
REM Также включен флаг смены диска, если надо.
cd /d %~dp0
REM Запускаем основной исполняемый файл
python relanotes.py
REM c:\python35\python.exe D:\Dropbox\Projects\Relanotes\Relanotes-qt5-0.03\relanotes.py
pause
