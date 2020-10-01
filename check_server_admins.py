import discord
import re
import io
from finde_and_download import download_server_log
from trouble_admins_dict import trouble_server_admins


class Admin:
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


async def check_admin_online():
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