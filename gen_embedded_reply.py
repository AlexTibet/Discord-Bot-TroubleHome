import discord
import random
import requests

import game_config
import finde_and_download
import dino_list
import server_info
import game_logic


async def database_check(message: list) -> discord.embeds:
    """Проверяем наличия файла с данными об игроке на удалённом сервере"""
    try:
        int(message[2])
    except Exception as Error:
        print(Error)
        emb = discord.Embed(title=f'Ошибка ввода данных', color=0xFF0000)
        return emb
    emb = discord.Embed(title=f'🔍', color=0x20B2AA)
    emb.set_author(name=f"Запрос информации о {message[2]}")
    emb.set_footer(text='Проверяю базу данных 📚')
    return emb


async def player_not_found() -> discord.embeds:
    emb = discord.Embed(title=f'❌ Нет данных ❌', color=0xFF0000)
    emb.set_footer(text='Игрок не найден в базе данных')
    return emb


async def bite(ctx, message: str) -> discord.embeds:
    """Игра 'Кусь', случайно выбирается результат и цель укуса, каждому соответствует свой набор gif"""
    target, victim, gif_id = await game_logic.bite_logic(message)
    emb = discord.Embed()
    gif_url = random.choice(game_config.GIF_KUS[gif_id])
    if target is not None:
        emb.add_field(
            name='Кусь!',
            value=f"<@{ctx.author.id}> откусил {target} у <@{victim}>")
        emb.set_image(url=gif_url)
        return emb
    else:
        emb.add_field(
            name='Провал!',
            value=f"<@{ctx.author.id}> обломал зубы об <@{victim}>")
        emb.set_image(url=gif_url)
        return emb


async def who_am_i(ctx) -> discord.embeds:
    """Игра 'Кто я?', случайно выбирается результат ответ"""
    emb = discord.Embed()
    emb.add_field(
        name='Кто ты?!',
        value=f"<@{ctx.author.id}> ты {random.choice(game_config.WHOAMI)}!")
    return emb


async def shipper(message: str) -> discord.embeds:
    """Игра 'Шипперинг', случайно выбирается результат и gif"""
    heart = random.choice(game_config.SHIPPER_HEART)
    gif_url = random.choice(game_config.GIF_SHIPPER)
    victim_one, victim_two, compatibility, title = await game_logic.shipper_logic(message)
    emb = discord.Embed(color=0xF08080)
    emb.add_field(
        name=f'{heart} {compatibility}% {heart}',
        value=f"{victim_one} и {victim_two} {title}")
    emb.set_image(url=gif_url)
    return emb


async def hug(ctx, message):
    gif_url = random.choice(game_config.GIF_HUG)
    emb = discord.Embed()
    emb.add_field(
        name=f'Обнимашки',
        value=f"<@{ctx.author.id}> обнимает {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def feed(ctx, message):
    gif_url = random.choice(game_config.GIF_FEED)
    emb = discord.Embed()
    emb.add_field(
        name=f'Ням ням',
        value=f"<@{ctx.author.id}> кормит {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def kiss(ctx, message):
    gif_url = random.choice(game_config.GIF_KISS)
    emb = discord.Embed()
    emb.add_field(
        name=f'Поцелуй',
        value=f"<@{ctx.author.id}> целует {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def love(ctx, message):
    gif_url = random.choice(game_config.GIF_LOVE)
    emb = discord.Embed()
    emb.add_field(
        name=f'Любовь',
        value=f"<@{ctx.author.id}> любит {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def hit(ctx, message):
    gif_url = random.choice(game_config.GIF_HIT)
    emb = discord.Embed()
    emb.add_field(
        name=f'Удар!',
        value=f"<@{ctx.author.id}> бьёт {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def slap(ctx, message):
    gif_url = random.choice(game_config.GIF_SLAP)
    emb = discord.Embed()
    emb.add_field(
        name=f'Шлёп!',
        value=f"<@{ctx.author.id}> шлёпает {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def poke(ctx, message):
    gif_url = random.choice(game_config.GIF_POKE)
    emb = discord.Embed()
    emb.add_field(
        name=f'Тык',
        value=f"<@{ctx.author.id}> тыкает {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def take_hand(ctx, message):
    gif_url = random.choice(game_config.GIF_TAKEHAND)
    emb = discord.Embed()
    emb.add_field(
        name=f'Взять за руку',
        value=f"<@{ctx.author.id}> берёт за руку {message[3]}")
    emb.set_image(url=gif_url)
    return emb


async def stroke(ctx, message):
    gif_url = random.choice(game_config.GIF_STROKE)
    emb = discord.Embed()
    emb.add_field(
        name=f'Погладить',
        value=f"<@{ctx.author.id}> гладит {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def sad(ctx):
    gif_url = random.choice(game_config.GIF_SAD)
    emb = discord.Embed()
    emb.add_field(
        name=f'Печаль',
        value=f"<@{ctx.author.id}> грустит...")
    emb.set_image(url=gif_url)
    return emb


# В разработке
async def marriage(ctx, message):
    emb = discord.Embed(title='``Новое предложение руки и сердца!`` :couple_with_heart:', color=0xF08080)
    emb.add_field(
        name=f':white_check_mark: = Да.  :negative_squared_cross_mark: = Нет ',
        value=f'{message[1]} даёшь ли ты своё согласие на брак c <@{ctx.author.id}>?')
    return emb


async def marriage_accept(husband_id, wife_id):
    gif_url = random.choice(game_config.GIF_MARRIAGE)
    emb = discord.Embed(title='💝:tada:💖', color=0xF08080)
    emb.add_field(
        name=f'Новый союз двух любящих сердец :ring:',
        value=f"С этого дня <@{husband_id}> и <@{wife_id}> в счастливом браке! :tada:")
    emb.set_image(url=gif_url)
    return emb


async def marriage_rejected(husband_id, wife_id):
    gif_url = random.choice(game_config.GIF_SAD)
    emb = discord.Embed(title='💔', color=0xF08080)
    emb.add_field(
        name=f'Отвергнут',
        value=f"<@{wife_id}> отвергает <@{husband_id}>")
    emb.set_image(url=gif_url)
    return emb


async def dino_info(ctx, message: str) -> discord.embeds:
    """Вытаскиваем данные о дино игрока"""
    steam_id = int(message[2])
    filename = await finde_and_download.download_log(steam_id)
    data = await finde_and_download.data_info(filename)

    if data is False:
        return await player_not_found()
    else:
        emb = discord.Embed(title=data['CharacterClass'],
                            color=0x20B2AA)
        emb.set_author(name=f"Информация о динозавре {steam_id}")
        emb.add_field(
            name='Рост:',
            value=data['Growth'])
        emb.add_field(
            name='Здоровье:',
            value=data['Health'])
        emb.add_field(
            name='Еда:',
            value=data['Hunger'])
        emb.add_field(
            name='Вода:',
            value=data['Thirst'])
        emb.add_field(
            name='Выносливость:',
            value=data['Stamina'])
        emb.add_field(
            name='Кровь:',
            value=data['BleedingRate'])
        emb.add_field(
            name='Пол:',
            value="Женский" if data['bGender'] else "Мужской")
        emb.add_field(
            name='Нога:',
            value="Сломана" if data['bBrokenLegs'] else "Не сломана")
        emb.add_field(
            name='Кислород:',
            value=data['Oxygen'])
        emb.set_footer(text=f'{ctx.author} запросил информацию о дино игрока {steam_id}',
                       icon_url=ctx.author.avatar_url
                       )
        return emb


async def give_dino(message: list, channel: discord.object) -> discord.embeds:
    """Прописывает необходимого дино игроку"""
    steam_id, dino = int(message[2]), message[3]
    status = None
    for catalog in dino_list.DINO_LIST:
        if dino in catalog:
            emb = discord.Embed(title=f'🔍', color=0x20B2AA)
            emb.set_footer(text='Проверяю базу данных 📚')
            await channel.send(embed=emb)
            emb.clear_fields()
            filename = await finde_and_download.data_modification(steam_id, dino)
            if filename is False:
                return await player_not_found()
            if await finde_and_download.upload_log(filename, steam_id):
                emb = discord.Embed(title=f'✅ Готово', color=0x20B2AA)
                emb.set_footer(text='Дино прописан, и загружен на сервер')
                return emb
            else:
                emb = discord.Embed(title=f'⛔ Не получилось загрузить файл на сервер ⛔', color=0xFF0000)
                return emb
    if status is None:
        emb = discord.Embed(title=f'❌ Ошибка ❌', color=0xFF0000)
        emb.set_footer(text='Такого дино нет')
        return emb


async def dino_catalog(channel: discord.object) -> None:
    """Выводит список дино доступных в игре"""
    emb = discord.Embed(title=f'Прогрессия.', color=0x20B2AA)
    emb.add_field(
        name='Травоядные:',
        value="\n".join(dino_list.OLD_HERBIVORES))
    emb.add_field(
        name='Хищники:',
        value="\n".join(dino_list.OLD_CARNIVORES))
    await channel.send(embed=emb)
    emb.clear_fields()

    emb = discord.Embed(title=f'Сурвайвл.', color=0x20B2AA)
    emb.add_field(
        name='Травоядные:',
        value="\n".join(dino_list.HERBIVORES))
    emb.add_field(
        name='Хищники:',
        value="\n".join(dino_list.CARNIVORES))
    await channel.send(embed=emb)


async def online_info():
    info = await server_info.bermuda_server_info()
    if info is not None:
        emb = discord.Embed(title=f"Игроков {info['players']['active']} из {info['players']['total']}",
                            color=0xf6ff00)
        emb.set_author(name="Онлайн" if info['is_online'] is True else "Оффлайн")
        emb.add_field(
            name='Название:',
            value=info['name'])
        emb.add_field(
            name='Карта:',
            value=info['map'])
    else:
        emb = discord.Embed(title=f'❌ Нет данных ❌', color=0xFF0000)
    return emb


async def steam_id_info(steam_id):
    session = requests.Session()
    bermuda_info = session.post(f'https://steamidfinder.com/lookup/{steam_id}/')
    if bermuda_info.status_code == 200:
        return bermuda_info.json()
    else:
        return None