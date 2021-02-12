import time
import re
import io
from socket import timeout

import discord
import a2s

from finde_and_download import download_server_log, backup_server_data
from trouble_admins_dict import trouble_server_admins
import config


class Admin:
    """
    Администратор
    Имеет идентификатор (SteamID), статус (онлайн/оффлайн), количество убийств и смертей
    """
    def __init__(self, steam_id):
        self.steam_id = int(steam_id)
        self.activity = False
        self.kills = 0
        self.death = 0

    def connect(self):
        self.activity = True

    def disconnect(self):
        self.activity = False

    def get_admin_name(self):
        return f"<@{trouble_server_admins[self.steam_id]}>"

    def get_activity(self):
        return self.activity

    def add_kills(self):
        self.kills += 1

    def get_kills_count(self):
        return self.kills

    def add_death(self):
        self.death += 1

    def get_death_count(self):
        return self.death


class AutoBackup:
    """
    Класс автоматического резервного копирования базы данных игрового сервера
    """
    def __init__(self):
        self._server = (
            config.main_host,
            config.main_port,
            config.main_login,
            config.main_password,
            config.main_saves_directory
        )

    def _auto_backup_server_data(self):
        return backup_server_data(self._server)

    def run(self):
        while True:
            try:
                if self._auto_backup_server_data():
                    time.sleep(7200)
                else:
                    raise Exception('Не удалось скачать файлы')
            except Exception as error:
                print(error)
                time.sleep(600)
                continue


def check_admin_parser(admins: dict) -> int and str:
    with io.open('download_logs.log', 'r', encoding='utf-8') as log:
        for line in log:
            # ловим попытки подключения
            if re.search(r'LogOnline: STEAM: Adding P2P connection information with user', line):
                # time = time_detect(line)
                steam_id = int(line[re.search(r'LogOnline: STEAM: Adding P2P connection information with user',
                                              line).end():].split()[0].strip())
                if int(steam_id) in trouble_server_admins.keys():
                    admins[steam_id].connect()
            elif re.search(r'LogBeastsOfBermuda: Display: New player [\d]{17} successfully registered to the game server!', line):
                steam_id = int(line.split(':')[-1].split()[2])
                if int(steam_id) in trouble_server_admins.keys():
                    admins[steam_id].connect()
            elif re.search(r'LogBeastsOfBermuda: Display: Starting post login streaming process for player', line):
                nik_name, steam_id = line[re.search(
                    r'LogBeastsOfBermuda: Display: Starting post login streaming process for player',
                    line).end():].strip().split('with ID')
                steam_id = int(steam_id.strip())
                if int(steam_id) in trouble_server_admins.keys():
                    admins[steam_id].connect()
            elif re.search(r'LogOnline: STEAM: [\d]{17} has been removed.', line):
                steam_id = int(line.split(':')[-1].split()[0])
                if steam_id in trouble_server_admins.keys():
                    admins[steam_id].disconnect()
            elif re.search(r'Killing Player ID', line):
                steam_id = int(line[re.search(r'Killing Player ID', line).end():].split(',')[0])
                if steam_id in trouble_server_admins.keys():
                    admins[steam_id].add_kills()
            elif re.search(r'PLAYER DEATH::Reason:', line):
                steam_id = int(line.split(',')[-3].split(':')[-1].strip())
                if steam_id in trouble_server_admins.keys():
                    admins[steam_id].add_death()
    online, count = '', 0
    for admin in admins.values():
        if admin.get_activity():
            count += 1
            online += f'{admin.get_admin_name()} {admin.get_kills_count()}:{admin.get_death_count()}\n'
    return count, online


async def check_admin_online() -> discord.Embed:
    """
    Выясняем кто из администраторов онлайн на сервере.
    Для этого скачиваем логи сервера, парсим, в созданые объекты админов записываем заходы/выходы/убийства смерти
    Тех админов статус которых остался онлайн вписываем в объект Embed и возвращаем для дальнейшей отправки в чат
    """
    await download_server_log(
        (config.main_host, config.main_port, config.main_login, config.main_password, config.main_logs_directory)
    )
    admins_rs = {}
    for steam_id in trouble_server_admins.keys():
        admins_rs[steam_id] = Admin(steam_id)
    count, online = check_admin_parser(admins_rs)
    emb = discord.Embed(title=f"Админы на сервере:",
                        color=0xf6ff00)
    emb.add_field(name=f'Rival `{count}` ', value=online if len(online) > 0 else "На сервере нет админов")
    #
    # await download_server_log(
    #     (config.ap_host, config.ap_port, config.ap_login, config.ap_password, config.ap_logs_directory)
    # )
    # admins_ap = {}
    # for steam_id in trouble_server_admins.keys():
    #     admins_ap[steam_id] = Admin(steam_id)
    # count, online = check_admin_parser(admins_ap)
    # emb.add_field(name=f'Ancestral `{count}` ', value=online if len(online) > 0 else "На сервере нет админов")
    return emb


async def bermuda_server_info(server_query):
    """
    Информация о сервере
    server_query: tuple[IP, query PORT]
    Делаем запрос Steam api с помощью библиотеки a2s
    возвращаем словарь с информацией о онлайне сервера или None если не получили ответ
    """
    try:
        server_response = a2s.info(server_query, encoding='utf-8')
    except timeout:
        return None
    server_info = {}
    for item in server_response:
        server_info[item[0]] = item[1]
    return server_info
