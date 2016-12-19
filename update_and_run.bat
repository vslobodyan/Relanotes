REM get path
REM cd path
echo "Обновляется исходный код RelaNotes. Пожалуйста, подождите.."
git fetch https://digitect.visualstudio.com/Relanotes/Relanotes%20Team/_git/Relanotes
echo "Обновление выполнено. Запускается программа."
python3 relanotes.py
pause