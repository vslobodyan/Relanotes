﻿# RelaNotes

Система для ведения объёмных заметок, структурированных разделами и многоуровневым содержанием, а также работы с накопленными знаниями.
Обладает чистым минималистичным интерфейсом и поиском по содержимому в реальном времени.

Создана как развитие [Zim](https://www.zim-wiki.org/) на другом стеке (Python 3 / Qt5) и с инновациями в интерфейсе, удобности и лаконичности.

Кроме прочего в интерфейс внедрены особые функции, такие как сниппеты текстов для быстрой вставки и защита от случайных действий в интерфейсе программы.

Программа тестировалась на Windows 7-10, MacOS, Linux (Fedora, Ubuntu, Manjaro и другие)

![Скрин окна программы](https://raw.githubusercontent.com/vslobodyan/Relanotes/master/screenshots/format.png "Скрин окна программы")


## Специальный калькулятор **RelaCalc**

Предназначен для работы с сырыми текстовыми данными. Позволяет вычислять любые выражения, введённые или вставленные простым смешанным текстом, который сразу очищается и интерпретируется.
Например, вы можете вставить скопированную в интернете таблицу или строку с различными текстовыми и числовыми данными. По умолчанию над очищенными числами будет сразу проведена операция сложения. В результате вы получите мгновенный результат без необходимости приведения данных для вычисления к нужному виду вручную.
Результат будет вычисляться в режиме реального времени, когда вы вводите или меняете текст.
 ![Скрин окна программы](https://raw.githubusercontent.com/vslobodyan/Relanotes/master/screenshots/relacalc_1.png "Скрин окна программы")



## Живой поиск по списку заметок

Мгновенный поиск по имени и содержимому заметки из одного поля.
Перейти в поиск из заметки: ```Ctrl+J```, и Вы сразу окажетесь в поле поиска.
Затем наберите слово с пробелом в начале для поиска по содержимому заметок:
 * `␠ninja` найдет все заметки, в которых есть упоминание ninja.
   ![Скрин окна программы](https://raw.githubusercontent.com/vslobodyan/Relanotes/master/screenshots/search_2.png "Скрин окна программы")
 * `␠␠ninja` если поставить 2 пробела в начале, то произойдет поиск по всем заметкам, в которых указанному слову предшествует пробел.
 
 * `projects ninja` найдет все заметки, в пути или названии которых есть projects, и в которых есть упоминание ninja.
  ![Скрин окна программы](https://raw.githubusercontent.com/vslobodyan/Relanotes/master/screenshots/search_3.png "Скрин окна программы")
   
Или слово без пробела для поиска по названию (или пути) заметки:
 * `proj` найдет все заметки с именами projects, proj. и т.д.
  ![Скрин окна программы](https://raw.githubusercontent.com/vslobodyan/Relanotes/master/screenshots/search_1.png "Скрин окна программы")
 
## Заготовки текста (сниппеты) для быстрой вставки

Сниппеты хранятся в отдельном файле, из которого формируется специальное меню в интерфейсе программы с их списком. Досточно щёлкнуть по пункту этого меню, и в вашу заметку будет вставлен заранее сохранённый текст любого объёма. Удобно использовать при подготовке рабочих ответов и в других ситуациях, где требуется быстро вставить свои контакты, готовые скрипты сообщений или ответов, и т.д. 

## Блокировка интерфейса - защита от детей и питомцев

 Часто в семьях присутствует проблема - компьютер нельзя оставить без присмотра ни на минуту!
 На его клавиатуре и мышке тут-же потопает или щенок, или маленький ребенок, и все написанное может быть безнадежно потеряно или испорчено.

 В Relanotes есть специальный режим быстрой блокировки интерфейса если в программе ничего не делают 60 секунд (или 30, или как захотите)!
 Вы включаете этот режим, и работаете спокойно, отвлекаясь на домашние дела, на детей и на всё что захотите!
 Программа надежно защитит вашу информацию от изменения. При этом вы легко продолжите работать, нажав быструю секретную комбинацию клавиш!
 И не надо волноваться - сохранила ли программа ваши изменения. Конечно да!


## Установка зависимостей в Linux

### Fedora
`sudo dnf in python3-qt5`


## Формат файлов заметок

Просто текстовый UTF-8.
Окончание строк в UNIX-like.
Позволяет синхронизировать заметки через облачные дисковые сервисы с другими устройствами и открывать их на **любом** устройстве в текстовом редакторе или схожих по назначению программах.
