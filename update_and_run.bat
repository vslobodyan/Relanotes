@echo off
REM �몫�祭�� "��" (�뢮�� �믮�������� ��ப �� �࠭).
REM ����஢�� 䠩�� ������ ���� cp866 (��ਫ��� DOS), �⮡� � ���������� ��ப� �� ����� �ࠪ�����.
cls
REM ���⪠ �࠭�
title Relanotes - update and run
REM ������ ���� ��������� ����

REM ���室�� � �����, � ���ன ��室���� �ਯ� � �᭮���� ����᪠��� ��⮭-䠩�.
REM ����� ����祭 䫠� ᬥ�� ��᪠, �᫨ ����.
cd /d %~dp0

echo We will update source code of RelaNotes. Please, wait..
git pull https://digitect.visualstudio.com/Relanotes/Relanotes%20Team/_git/Relanotes
echo.
echo The upgrade is complete. The program is run.
echo.
python relanotes.py
pause