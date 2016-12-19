REM Переходим в папку, в которой находится скрипт и основной запускаемый Питон-файл.
REM Также включен флаг смены диска, если надо.
cd /d %~dp0

echo "Обновляется исходный код RelaNotes. Пожалуйста, подождите.."
git fetch https://digitect.visualstudio.com/Relanotes/Relanotes%20Team/_git/Relanotes
echo "Обновление выполнено. Запускается программа."
python relanotes.py
pause