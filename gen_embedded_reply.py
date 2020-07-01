import discord
import random

import game_config
import finde_and_download
import dino_list


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
    victim = message[1].replace('<', '').replace('!', '').replace('@', '').replace('>', '').replace(',', '')
    targets = random.choice(game_config.TARGET)
    gif_id = targets[1]
    target = targets[0]
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
