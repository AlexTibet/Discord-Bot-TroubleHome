import requests
import config
import discord
import re
import io
from finde_and_download import download_server_log
from trouble_admins_dict import trouble_server_admins


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


async def check_admin_online() -> discord.Embed:
    """
    Выясняем кто из администраторов онлайн на сервере.
    Для этого скачиваем логи сервера, парсим, в созданые объекты админов записываем заходы/выходы/убийства смерти
    Тех админов статус которых остался онлайн вписываем в объект Embed и возвращаем для дальнейшей отправки в чат
    """
    await download_server_log()
    admins = {}
    for steam_id in trouble_server_admins.keys():
        admins[steam_id] = Admin(steam_id)

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
    emb = discord.Embed(title=f"Админы на сервере:",
                        color=0xf6ff00)
    emb.add_field(name=f'{count} онлайн', value=online)
    return emb if len(online) > 0 else discord.Embed(title=f"На сервере нет админов", color=0xf6ff00)


async def bermuda_server_info() -> dict or None:
    """
    Информация о сервере
    Делаем запрос на панель управления сервером, логинимся, получаем ответ
    возвращаем словарь с информацией о онлайне сервера или None если не получили ответ
    """
    session = requests.Session()
    data = {
        'action': 'signin',
        'email': config.login,
        'password': config.password
    }
    auth = session.post(config.auth, data)
    bermuda_info = session.post(config.bermuda_info, data={'ugid': config.bermuda_port})
    if bermuda_info.status_code == 200:
        return bermuda_info.json()
    else:
        return None


def bermuda_test_server_info():
    """
    Информация о тестовом сервере (В РАЗРАБОТКЕ, пока не работает)
    Делаем запрос на панель управления тестовым сервером, логинимся, получаем ответ
    возвращаем словарь с информацией о онлайне тестового сервера или None если не получили ответ
    """
    session = requests.Session()
    data = {
        'email': config.g_portal_login,
        'password': config.g_portal_password
    }
    session.post(config.auth_test_server, data)
    bermuda_info = session.get(config.bermuda_test_server_info)
    if bermuda_info.status_code == 200:
        print(bermuda_info)
        return bermuda_info.json()
    else:
        return None


def bermuda_test_server_start():
    """
    Команда на включение тестового сервере (В РАЗРАБОТКЕ, пока не работает)
    """
    session = requests.Session()
    data = {
        'email': config.g_portal_login,
        'password': config.g_portal_password
    }
    auth = session.post(config.auth_test_server, data)
    cookies = {}
    for el in auth.cookies.items():
        cookies[el[0]] = el[1]
    print(auth)
    print(auth.cookies)
    print(cookies)
    bermuda_start = session.get(config.bermuda_test_server_start, cookies=cookies)
    print(bermuda_start)
    if bermuda_start.status_code == 200:
        print(bermuda_start)
        return bermuda_start.json()
    else:
        print(bermuda_start)
        return None
