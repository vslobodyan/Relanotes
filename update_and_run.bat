
@echo off
REM Выключение "эха" (вывода выполняющихся строк на экран).

chcp 65001
REM Делаем консоль юникодной

REM Кодировка файла должна быть cp866 (кириллица DOS), чтобы в коммандной строке не лезли кракозябры.
cls
REM Очистка экрана
title Relanotes - update and run
REM Задаем новый заголовок окну

REM Переходим в папку, в которой находится скрипт и основной запускаемый Питон-файл.
REM Также включен флаг смены диска, если надо.
cd /d %~dp0

echo We will update source code of RelaNotes. Please, wait..
git pull https://digitect.visualstudio.com/Relanotes/Relanotes%20Team/_git/Relanotes
echo.
echo The upgrade is complete. The program is run.
echo.
python relanotes.py
pause