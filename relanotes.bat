@echo off

REM ��ਯ� ����� ����᪠�� ��㤠 㣮���.
REM �� ᠬ ��३��� � ᢮� ����� � ������� �㦭� 䠩�.

REM �����, �� ���ன �����⨫� �ਯ�
REM @echo cd = %cd%

REM �����, � ���ன ��室���� �ਯ�
REM @echo dp0 = %~dp0

REM ���室�� � �����, � ���ன ��室���� �ਯ� � �᭮���� ����᪠��� ��⮭-䠩�.
REM ����� ����祭 䫠� ᬥ�� ��᪠, �᫨ ����.
cd /d %~dp0
REM ����᪠�� �᭮���� �ᯮ��塞� 䠩�
python relanotes.py
REM c:\python35\python.exe D:\Dropbox\Projects\Relanotes\Relanotes-qt5-0.03\relanotes.py
pause
