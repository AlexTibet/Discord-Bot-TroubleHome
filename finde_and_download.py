from ftplib import FTP, error_perm
import datetime
from os import path, mkdir


async def download_server_log(server: tuple) -> bool:
    """Скачиваем  файл текущих логов игрового сервера (основного)"""
    bob_host, bob_port, bob_login, bob_password, bob_directory = server
    with FTP() as ftp:
        ftp.connect(bob_host, bob_port)
        ftp.login(bob_login, bob_password)
        ftp.cwd(bob_directory)
        try:
            with open(f'download_logs.log', 'wb') as f:
                ftp.retrbinary('RETR ' + 'BeastsOfBermuda.log', f.write)
                return True
        except FileNotFoundError:
            return False


async def download_server_config(server: tuple) -> bool:
    """Скачиваем  конфигурационный файл с игрового сервера server"""
    bob_host, bob_port, bob_login, bob_password, bob_directory = server
    with FTP() as ftp:
        ftp.connect(bob_host, bob_port)
        ftp.login(bob_login, bob_password)
        ftp.cwd(bob_directory)
        try:
            with open('download_Game.ini', 'wb') as f:
                ftp.retrbinary('RETR ' + 'Game.ini', f.write)
                return True
        except FileNotFoundError:
            return False


async def upload_server_config(server: tuple) -> bool:
    """Загружаем обновлённый конфигурационный файл на сервер server"""
    try:
        bob_host, bob_port, bob_login, bob_password, bob_directory = server
        with FTP() as ftp:
            ftp.connect(bob_host, bob_port)
            ftp.login(bob_login, bob_password)
            ftp.cwd(bob_directory)
            ftp.storbinary('STOR ' + "Game.ini", open('Game.ini', "rb"))
            return True
    except Exception:
        return False


def download_server_saves(server: tuple) -> bool:
    """Скачиваем сохранения игрового сервера server"""
    name, host, port, login, password, directory = server
    with FTP() as ftp:
        ftp.connect(host, port)
        ftp.login(login, password)
        ftp.cwd(directory)
        try:
            with open(f'{path.dirname(__file__)}/server_saves/DeathHistory.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + f'SERVER_{name}_DeathHistory.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/DynamicWorld.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + f'SERVER_{name}_DynamicWorld.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/Entities.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + f'SERVER_{name}_Entities.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/PlayerPunishments.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + f'SERVER_{name}_PlayerPunishments.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/UserProfiles.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + f'SERVER_{name}_UserProfiles.sav', f.write)

            with open(f'{path.dirname(__file__)}/server_saves/WorldItems.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + f'SERVER_{name}_WorldItems.sav', f.write)

            return True
        except FileNotFoundError:
            return False


def delete_server_saves(server: tuple) -> bool:
    """Удаляем сохранения игрового сервера server"""
    name, host, port, login, password, directory = server
    with FTP() as ftp:
        ftp.connect(host, port)
        ftp.login(login, password)
        ftp.cwd(directory)
        filenames = ['DeathHistory', 'DynamicWorld', 'Entities', 'PlayerPunishments', 'UserProfiles', 'WorldItems']
        for filename in filenames:
            try:
                ftp.delete(f"SERVER_{name}_{filename}.sav")
            except (error_perm, FileNotFoundError):
                continue
        return True



def backup_server_data(server: tuple) -> bool:
    """

    :param server:
    :return:
    """
    host, port, login, password, directory = server
    with FTP() as ftp:
        ftp.connect(host, port)
        ftp.login(login, password)
        ftp.cwd(directory)
        time = datetime.datetime.now()
        backup_dir = f"{path.dirname(__file__)}/server_saves/backups/{time.date()}_{time.hour}-{time.minute}"
        try:
            mkdir(backup_dir)
        except OSError:
            print(f'Не удалось создать дирректорию {backup_dir}')
            return False
        try:
            with open(f'{backup_dir}/SERVER_Rival_Shores_DeathHistory.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_DeathHistory.sav', f.write)

            with open(f'{backup_dir}/SERVER_Rival_Shores_Entities.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_Entities.sav', f.write)

            with open(f'{backup_dir}/SERVER_Rival_Shores_PlayerPunishments.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_PlayerPunishments.sav', f.write)

            with open(f'{backup_dir}/SERVER_Rival_Shores_UserProfiles.sav', 'wb') as f:
                ftp.retrbinary('RETR ' + 'SERVER_Rival_Shores_UserProfiles.sav', f.write)

            return True

        except FileNotFoundError:
            return False


def upload_server_saves(server: tuple) -> bool:
    """Загружаем сохранения на игровой сервер server"""
    try:
        name, bob_host, bob_port, bob_login, bob_password, bob_directory = server
        with FTP() as ftp:
            ftp.connect(bob_host, bob_port)
            ftp.login(bob_login, bob_password)
            ftp.cwd(bob_directory)
            ftp.storbinary(
                'STOR ' + f'SERVER_{name}_DeathHistory.sav',
                open(f'{path.dirname(__file__)}/server_saves/DeathHistory.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + f'SERVER_{name}_DynamicWorld.sav',
                open(f'{path.dirname(__file__)}/server_saves/DynamicWorld.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + f'SERVER_{name}_Entities.sav',
                open(f'{path.dirname(__file__)}/server_saves/Entities.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + f'SERVER_{name}_PlayerPunishments.sav',
                open(f'{path.dirname(__file__)}/server_saves/PlayerPunishments.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + f'SERVER_{name}_UserProfiles.sav',
                open(f'{path.dirname(__file__)}/server_saves/UserProfiles.sav', "rb")
            )
            ftp.storbinary(
                'STOR ' + f'SERVER_{name}_WorldItems.sav',
                open(f'{path.dirname(__file__)}/server_saves/WorldItems.sav', "rb")
            )
            return True
    except Exception as error:
        print("Ошибка загрузки", error, error.__doc__, error.__module__)
        return False
