from ftplib import FTP
from config import \
    host, port, login, password, directory,\
    main_host, main_port, main_login, main_password, main_logs_directory
import datetime
import json
from os import path
import config


async def download_server_log() -> bool:
    with FTP() as ftp:
        ftp.connect(main_host, main_port)
        ftp.login(main_login, main_password)
        print(ftp)
        print(ftp.retrlines('LIST'))
        ftp.cwd(main_logs_directory)
        print(ftp.retrlines('LIST'))
        try:
            with open('download_logs.log', 'wb') as f:
                ftp.retrbinary('RETR ' + 'BeastsOfBermuda.log', f.write)
                return True
        except FileNotFoundError:
            print("File BeastsOfBermuda.log not found!")
            return False


async def download_server_config(server: tuple) -> bool:
    bob_host, bob_port, bob_login, bob_password, bob_directory = server
    with FTP() as ftp:
        ftp.connect(bob_host, bob_port)
        ftp.login(bob_login, bob_password)
        print(ftp)
        print(ftp.retrlines('LIST'))
        ftp.cwd(bob_directory)
        print(ftp.retrlines('LIST'))
        try:
            with open('download_Game.ini', 'wb') as f:
                ftp.retrbinary('RETR ' + 'Game.ini', f.write)
                return True
        except FileNotFoundError:
            print("File Game.ini not found!")
            return False


async def upload_server_config(server: tuple) -> bool:
    """Загружает обновлённый конфиг на сервер"""
    try:
        bob_host, bob_port, bob_login, bob_password, bob_directory = server
        with FTP() as ftp:
            ftp.connect(bob_host, bob_port)
            ftp.login(bob_login, bob_password)
            ftp.cwd(bob_directory)
            ftp.storbinary('STOR ' + "Game.ini", open('Game.ini', "rb"))
            print("Файл загружен на сервер")
            return True
    except Exception as error:
        print("Ошибка загрузки", error, error.__doc__, error.__module__)
        return False


def download_server_saves(server: tuple) -> bool:
    host, port, login, password, directory = server
    print(host, port)
    print(login, password)
    print(directory)
    with FTP() as ftp:
        ftp.connect(host, port)
        ftp.login(login, password)
        print(ftp)
        print(ftp.retrlines('LIST'))
        ftp.cwd(directory)
        print(ftp.retrlines('LIST'))
        try:
            with open(f'{path.dirname(__file__)}/server_saves/DeathHistory.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_DeathHistory.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/DynamicWorld.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_DynamicWorld.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/Entities.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_Entities.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/PlayerPunishments.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_PlayerPunishments.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/UserProfiles.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_UserProfiles.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/WorldItems.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_WorldItems.sav', f.write)

            return True
        except FileNotFoundError:
            print("File not found!")
            return False


def upload_server_saves(server: tuple) -> bool:
    """Загружает обновлённый конфиг на сервер"""
    try:
        bob_host, bob_port, bob_login, bob_password, bob_directory = server
        with FTP() as ftp:
            ftp.connect(bob_host, bob_port)
            ftp.login(bob_login, bob_password)
            print(ftp.retrlines('LIST'))
            ftp.cwd(bob_directory)
            print(ftp.retrlines('LIST'))
            ftp.storbinary(
                'STOR ' + 'SERVER_Rival_Shores_DeathHistory.sav',
                open(f'{path.dirname(__file__)}/server_saves/DeathHistory.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + 'SERVER_Rival_Shores_DynamicWorld.sav',
                open(f'{path.dirname(__file__)}/server_saves/DynamicWorld.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + 'SERVER_Rival_Shores_Entities.sav',
                open(f'{path.dirname(__file__)}/server_saves/Entities.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + 'SERVER_Rival_Shores_PlayerPunishments.sav',
                open(f'{path.dirname(__file__)}/server_saves/PlayerPunishments.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + 'SERVER_Rival_Shores_UserProfiles.sav',
                open(f'{path.dirname(__file__)}/server_saves/UserProfiles.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + 'SERVER_Rival_Shores_WorldItems.sav',
                open(f'{path.dirname(__file__)}/server_saves/WorldItems.sav', "rb")
            )
            print("Файл загружен на сервер")
            return True
    except Exception as error:
        print("Ошибка загрузки", error, error.__doc__, error.__module__)
        return False


async def download_log(steam_id: int) -> str:
    """Скачивает json файл с данными игрока, и сохраняет с именем в которое включено время скачивания"""
    with FTP() as ftp:
        ftp.connect(host, port)
        ftp.login(login, password)
        ftp.cwd(directory)
        player_list = ftp.nlst()
        download_filename = await download_filename_creation(steam_id)
        if f"{steam_id}.json" in player_list:
            with open(download_filename, 'wb') as f:
                ftp.retrbinary('RETR ' + f"{steam_id}.json", f.write)
                return download_filename
        else:
            print(f"Игрока {steam_id} нет в базе данных")


async def upload_log(filename: str, steam_id: int) -> bool:
    """Загружает новый файл с данными игрока на сервер"""
    try:
        with FTP() as ftp:
            ftp.connect(host, port)
            ftp.login(login, password)
            ftp.cwd(directory)
            ftp.storbinary('STOR ' + f"{steam_id}.json", open(filename, "rb"))
            print("Файл загружен на сервер")
            return True
    except Exception as error:
        print("Ошибка загрузки", error, error.__doc__, error.__module__)
        return False


async def data_modification(steam_id: int, new_dino: str) -> str or False:
    """Изменяет данные игрока в .json"""
    file = await download_log(steam_id)
    if file is None:
        print(f"Игрока {steam_id} нет в базе данных")
        return False
    print(f"Модифицируем файл {file}")
    with open(file, 'r') as read_file:
        print(f"Файл {file} готов к модификации")
        data = json.load(read_file)
        if data is None:
            return False
        data['CharacterClass'] = new_dino
        data['UnlockedCharacters'] = new_dino
        data['Growth'] = "1.0"
        data['Hunger'] = "20000"
        data['Thirst'] = "20000"
        data['Stamina'] = "20000"
        data['Health'] = "20000"
        print(f"Изменения внесены")
        with open(f"{path.dirname(__file__)}/history/{steam_id}.json", "w") as output_file:
            json.dump(data, output_file, indent=4)
            print(f"Изменённый файл ({steam_id}.json) готов к загрузке на сервер")
        return f"{path.dirname(__file__)}/history/{steam_id}.json"


async def data_info(file: str) -> json or False:
    """Считывает данные о игроке из .json файла"""
    if file is None:
        return False
    with open(file, 'r') as read_file:
        data = json.load(read_file)
        return data


async def download_filename_creation(steam_id: int) -> str:
    """Генерирует имя файла содержащее дату и время загрузки"""
    date = datetime.datetime.now()
    day, month, year = date.day, date.month, date.year
    time = date.time()
    seconds, minutes, hours = time.second, time.minute, time.hour
    return fr"{path.dirname(__file__)}/history/{steam_id}__{month}-{day}-{year}_{hours}-{minutes}-{seconds}.json"
