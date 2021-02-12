import re

import config
from finde_and_download import download_server_config, upload_server_config


async def editing_configuration(channel, message):
    try:
        await channel.send('```fix\nСкачиваю файл конфигурации сервера\n```')
        await editing_preparation(channel, message)
    except FileNotFoundError:
        await channel.send('> **Ошибка, файл не найден**')


async def role_access(ctx, access_list) -> bool:
    """Checking access member to command"""
    for i in ctx.author.roles:
        if i.id in access_list:
            return True
    else:
        return False


def hex_to_rgba(color):
    color = color.replace('#', '')
    red = int(color[:2], 16)/255
    green = int(color[2:4], 16)/255
    blue = int(color[4:6], 16)/255
    alpha = 1.00
    return str(round(red, 2)), str(round(green, 2)), str(round(blue, 2)), str(alpha)


async def editing_preparation(channel, message):
    if channel.id == config.TEST_SERVER_CONFIG_CHANNEL:
        server = (config.test_host, config.test_port,
                  config.test_login, config.test_password,
                  config.test_config_directory)
    elif channel.id == config.SERVER_CONFIG_CHANNEL:
        server = (config.main_host, config.main_port,
                  config.main_login, config.main_password,
                  config.main_config_directory)
        # ap_server = (config.ap_host, config.ap_port,
        #              config.ap_login, config.ap_password,
        #              config.ap_config_directory)
    else:
        raise ValueError
    if await download_server_config(server):
        await channel.send('☑ *Файл конфигурации сервера скачан*')
        data = read_server_config('download_Game.ini')
        if data is not None:
            await channel.send('☑ *Файл конфигурации сервера прочитан*')
            await task_handler(channel, message, data)
            if await get_new_config(*data):
                await channel.send('☑ *Новый файл конфигурации сервера готов*')
                if await upload_server_config(server):
                    await channel.send('```fix\nФайл конфигурации загружен на сервер```')
                else:
                    await channel.send('```diff\nНе удалось загрузить файл конфигурации на сервер\nПопробуйте снова```')
                # if channel.id == config.SERVER_CONFIG_CHANNEL:
                    # if await upload_server_config(ap_server):
                    #     await channel.send('```fix\nФайл конфигурации загружен на сервер AP```')
                    # else:
                    #     await channel.send('```diff\nНе удалось загрузить файл конфигурации на сервер\nПопробуйте снова```')
            else:
                await channel.send('❌ *Ошибка. Не удалось создать новый файл конфигурации сервера*')
        else:
            await channel.send('❌ *Ошибка. Файл конфигурации сервера не прочитан*')
    else:
        await channel.send('❌ *Ошибка. Файл конфигурации сервера не скачан*')


def read_server_config(filename: str) -> (dict, dict, dict,):
    server_admins, player_colors, players_tags = {}, {}, {}
    with open(filename, 'r', encoding='utf-8') as server_config_file:
        with open('Game.ini', 'w', encoding='utf-8') as out_file:
            for line in server_config_file:
                if re.search(r'ServerAdmins', line):
                    steam_id = line.split('=')[2].split(',')[0].strip()
                    rank = line.split('=')[-1].replace('"', '').replace(')', '').strip()
                    server_admins[steam_id] = rank
                    print('Admin -', line.split('=')[2].split(',')[0].strip())
                elif re.search(r'PlayerChatColors=\(SteamID=', line):
                    steam_id = line.split(',')[0].split('=')[-1].strip()
                    color = line.split('(')[-1].split(',')
                    red = color[0].split('=')[1]
                    green = color[1].split('=')[1]
                    blue = color[2].split('=')[1]
                    alpha = color[3].split('=')[1].replace(')', '').strip()
                    color = (red, green, blue, alpha)
                    player_colors[steam_id] = color
                    print(steam_id, color)
                elif re.search(r'PlayerChatTags=\(SteamID=', line):
                    steam_id = line.split('=')[2].split(',')[0].strip()
                    tag = line.split(',')[-1].split('=')[-1].replace('"', '').replace(')', '').strip()
                    players_tags[steam_id] = tag
                    print(steam_id, tag)
                else:
                    if line not in [
                        '-[Tag][PlayerName]> Text body\n',
                        '!PlayerChatTags=ClearArray\n',
                        '!PlayerChatColors=ClearArray\n',
                        '\n',
                        ' '
                    ]:
                        out_file.writelines(line)
    return server_admins, player_colors, players_tags


async def get_new_config(server_admins_id: dict, players_colors: dict, players_tags: dict) -> bool:
    try:
        server_admins = ['\n']
        server_colors = ['\n\n!PlayerChatColors=ClearArray']
        server_tags = ['\n\n-[Tag][PlayerName]> Text body\n!PlayerChatTags=ClearArray']
        for steam_id, rank in server_admins_id.items():
            server_admins.append(
                f'ServerAdmins=(UserSteamId64={steam_id},AdminRank="{rank}")\n'
            )
        for steam_id, color in players_colors.items():
            server_colors.append(
                f'PlayerChatColors=(SteamID={steam_id},'
                f' ChatColor=(R={color[0]},G={color[1]},B={color[2]},A={color[3]}))'
            )
        for steam_id, tag in players_tags.items():
            server_tags.append(
                f'PlayerChatTags=(SteamID={steam_id}, ChatTag="{tag}")'
            )
        new_config = ''.join(server_admins) + '\n'.join(server_colors) + '\n'.join(server_tags)
        with open('Game.ini', 'a', encoding='utf-8') as f:
            f.write(new_config)
        return True
    except Exception:
        return False


async def task_handler(channel, message, data):
    if re.search(r'[Пп]рописать', message[0]):
        if re.search(r'админку', message[1]):
            for answer in add_server_admin(message, data):
                await channel.send(answer)
        elif re.search(r'цвет', message[1]):
            for answer in add_server_color(message, data):
                await channel.send(answer)
        elif re.search(r'т[еэ]г', message[1]):
            for answer in add_server_tag(message, data):
                await channel.send(answer)
        else:
            raise IndexError

    elif re.search(r'[Сс]нять', message[0]):
        if re.search(r'админку', message[1]):
            for answer in remove_server_admin(message, data):
                await channel.send(answer)
        elif re.search(r'цвет', message[1]):
            for answer in remove_server_color(message, data):
                await channel.send(answer)
        elif re.search(r'т[еэ]г', message[1]):
            for answer in remove_server_tag(message, data):
                await channel.send(answer)
        else:
            raise IndexError


def add_server_admin(message, data):
    for steam_id in message[3:]:
        try:
            int(steam_id.strip())
            data[0][steam_id.strip()] = message[2].strip()
            yield f'> ☑ Добавлены права администратора `{steam_id}`=`{message[2].strip()}`'
        except ValueError:
            yield f'> ❌ Ошибка с id={steam_id}'


def remove_server_admin(message, data):
    for steam_id in message[3:]:
        try:
            int(steam_id.strip())
            data[0].pop(steam_id.strip())
            yield f'> ☑ У `{steam_id}` сняты права администратора'
        except (ValueError, KeyError):
            yield f'> ❌ Ошибка с id=`{steam_id}` (ошибка в самом ID, либо он отсутствует в кофигурационном файле)'


def add_server_color(message, data):
    for steam_id in message[3:]:
        try:
            int(steam_id.strip())
            data[1][steam_id.strip()] = hex_to_rgba(message[2].strip())
            yield f'> ☑ Игроку `{steam_id}` установлен цвет ника = `{message[2].strip()}`'
        except ValueError:
            yield f'> ❌ Ошибка с id=`{steam_id}`'


def remove_server_color(message, data):
    for steam_id in message[3:]:
        try:
            int(steam_id.strip())
            data[1].pop(steam_id.strip())
            yield f'> ☑ У `{steam_id}` снят цвет ника'
        except (ValueError, KeyError):
            yield f'> ❌ Ошибка с id=`{steam_id}` (ошибка в самом ID, либо он отсутствует в кофигурационном файле)'


def add_server_tag(message, data):
    for steam_id in message[3:]:
        try:
            int(steam_id.strip())
            data[2][steam_id.strip()] = str(message[2].strip())
            yield f'> ☑ Игроку `{steam_id}` добавлен тэг `[{message[2].strip()}]`'
        except ValueError:
            yield f'> ❌ Ошибка с id=`{steam_id}`'


def remove_server_tag(message, data):
    for steam_id in message[3:]:
        try:
            int(steam_id.strip())
            data[2].pop(steam_id.strip())
            yield f'> ☑ У `{steam_id}` удалён тэг'
        except (ValueError, KeyError):
            yield f'> ❌ Ошибка с id=`{steam_id}` (ошибка в самом ID, либо он отсутствует в кофигурационном файле)'
