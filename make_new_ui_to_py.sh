#!/bin/bash


# Старый вариант строки для QT4
# pyrcc4 -py3 resources/resources.qrc -o resources/resources_rc.py

# Для работы команды в Opensuse должен стоять пакет python3-qt5-devel
# Новый вариант для QT5
pyrcc5 resources/resources.qrc -o resources/resources_rc.py

# Меняем путь импорта файла ресурсов
# find -type f -path ui -name \*.py -exec sed -i -r 's/import resources_rc/import resources.resources_rc/g' {} \;
#sed 's/<что_ищем>/<на_что_меняем>/' <входной файл> > <выходной файл>

echo "="*20
echo "WARNING! This is obsolete script for now - non-actual path to UI-files."
echo "Need to change this!"
echo "="*20

ui_files=("src/ui/main_window.py" "src/ui/preferences_window.py" "src/ui/calculator_window.py" "src/ui/note_multiaction.py" "src/ui/clear_history_dialog.py")

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
