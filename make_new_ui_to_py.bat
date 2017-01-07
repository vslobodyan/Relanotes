@echo off
REM ���������� "���" (������ ������������� ����� �� �����).

chcp 65001
REM ������ ������� ���������

cls
REM ������� ������
title Compile new UI for Relanotes
REM ������ ����� ��������� ����

REM ��������� � �����, � ������� ��������� ������ � �������� ����������� �����-����.
REM ����� ������� ���� ����� �����, ���� ����.
cd /d %~dp0

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


pause