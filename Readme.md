# Discord-бот "TroubleHome"
============================================================================
## Бот для игр и помощи администраторам информационно-развлекательного ресурса "Trouble Home"
- Игры 
- Мониторинг состояния серверов
- Настройки конфигурационных файлов
- Помощь администраторам
- Резервное копирование и перенос баз данных между серверами
----------------------------------------------------------------------------

Название файла  		| Содержание файла
------------------------|----------------------
datastorage.py 		    | Класс работающий с базой данных бота (Sqlite)
finde_and_download.py   | Функции поиска/скачивания/изменения данных с игровых серверов
game_config.py          | Настройки для игровых команд, ссылки на прикрепляемые .gif
game_logic.py           | Логика игровых команд
gen_embedded_reply.py   | Функции генерации встраиваемых сообщений Discord (embed)
main.py       			| Основной модуль содержащий инициализацию бота, и начальную обработку событий
message_handlers.py     | Функции обработчики команд
server_config_editor.py | Функционал изменений конфигураций игровых серверов
server_info.py          | Классы и функции мониторинга состояния серверов

