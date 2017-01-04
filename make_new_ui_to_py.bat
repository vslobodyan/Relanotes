
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

echo We will compile new UI for RelaNotes..

REM git pull https://digitect.visualstudio.com/Relanotes/Relanotes%20Team/_git/Relanotes
REM echo.
REM echo The upgrade is complete. The program is run.
REM echo.
REM python relanotes.py

pyrcc5 resources/resources.qrc -o resources/resources_rc.py

ui_files=("src/ui/main_window.py" "src/ui/preferences_window.py" "src/ui/calculator_window.py" "src/ui/note_multiaction.py") 

for afile in ${ui_files[@]} 
do
	aui=`echo $afile | sed 's/.py/.ui/'`
	#echo $aui
	# Старый вариант команды для QT4	
	# pyuic4 $aui -o $afile
	# Новый вариант команды для QT5
	pyuic5 $aui -o $afile
	
	sed -i -r 's/import resources_rc/import resources.resources_rc/' $afile
done





pause