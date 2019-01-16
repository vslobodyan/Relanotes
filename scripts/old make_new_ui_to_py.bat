@echo off
REM Выключение "эха" (вывода выполняющихся строк на экран).

chcp 65001
REM Делаем консоль юникодной

cls
REM Очистка экрана
title Compile new UI for Relanotes
REM Задаем новый заголовок окну

REM Переходим в папку, в которой находится скрипт и основной запускаемый Питон-файл.
REM Также включен флаг смены диска, если надо.
cd /d %~dp0


echo ===========================
echo WARNING! This is obsolete script for now - non-actual path to UI-files.
echo Need to change this!
echo ===========================


echo We will compile new UI for RelaNotes..

pyrcc5 resources/resources.qrc -o resources/resources_rc.py

set UI_FILE="main_window"
pyuic5 "src/ui/%UI_FILE%.ui" --import-from "resources" -o "src/ui/%UI_FILE%.py"

set UI_FILE="preferences_window"
pyuic5 "src/ui/%UI_FILE%.ui" --import-from "resources" -o "src/ui/%UI_FILE%.py"

set UI_FILE="calculator_window"
pyuic5 "src/ui/%UI_FILE%.ui" --import-from "resources" -o "src/ui/%UI_FILE%.py"

set UI_FILE="note_multiaction"
pyuic5 "src/ui/%UI_FILE%.ui" --import-from "resources" -o "src/ui/%UI_FILE%.py"

set UI_FILE="clear_history_dialog"
pyuic5 "src/ui/%UI_FILE%.ui" --import-from "resources" -o "src/ui/%UI_FILE%.py"

pause