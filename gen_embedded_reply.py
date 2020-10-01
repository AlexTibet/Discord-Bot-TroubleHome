import discord
import random
import requests
import datetime

import game_config
import game_logic
from datastorage import SqliteDataStorage as sql_db
import config
import server_info


async def no_access() -> discord.embeds:
    emb = discord.Embed(title=f'❌ Нет доступа ❌', color=0xFF0000)
    emb.set_footer(text='Данная команда вам недоступна')
    return emb


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
    responses = game_config.WHOAMI
    random.shuffle(responses)
    emb = discord.Embed()
    emb.add_field(
        name='Кто ты?!',
        value=f"<@{ctx.author.id}> ты {random.choice(responses)}!")
    return emb


async def who_should_i_play(ctx) -> discord.embeds:
    emb = discord.Embed(color=0x2F4F4F)
    play_list = [i for i in game_config.BOB_DINO_EMOJI.keys()]
    random.shuffle(play_list)
    play = random.choice(play_list)
    emb.add_field(
        name='На ком поиграть?',
        value=f"<@{ctx.author.id}> поиграй на {play}")
    emb.set_image(url=game_config.BOB_DINO_EMOJI[play])
    return emb


async def shipper(message: str) -> discord.embeds:
    """Игра 'Шипперинг', случайно выбирается результат и gif"""
    heart = random.choice(game_config.SHIPPER_HEART)
    gif_list = game_config.GIF_SHIPPER
    random.shuffle(gif_list)
    gif_url = random.choice(gif_list)
    victim_one, victim_two, compatibility, title = await game_logic.shipper_logic(message)
    emb = discord.Embed(color=0xF08080)
    emb.add_field(
        name=f'{heart} {compatibility}% {heart}',
        value=f"{victim_one} и {victim_two} {title}")
    emb.set_image(url=gif_url)
    return emb


async def hug(ctx, message):
    gif_list = game_config.GIF_HUG
    random.shuffle(gif_list)
    gif_url = random.choice(gif_list)
    emb = discord.Embed()
    emb.add_field(
        name=f'Обнимашки',
        value=f"<@{ctx.author.id}> обнимает {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def feed(ctx):
    gif_list = game_config.GIF_FEED
    random.shuffle(gif_list)
    gif_url = random.choice(gif_list)
    emb = discord.Embed()
    emb.add_field(
        name=f'Ням ням',
        value=f"<@{ctx.author.id}> кормит <@{ctx.raw_mentions[0]}>")
    emb.set_image(url=gif_url)
    return emb


async def kiss(ctx, message):
    gif_list = game_config.GIF_KISS
    random.shuffle(gif_list)
    gif_url = random.choice(game_config.GIF_KISS)
    emb = discord.Embed()
    emb.add_field(
        name=f'Поцелуй',
        value=f"<@{ctx.author.id}> целует {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def love(ctx, message):
    random.shuffle(game_config.GIF_LOVE)
    gif_url = random.choice(game_config.GIF_LOVE)
    emb = discord.Embed()
    emb.add_field(
        name=f'Любовь',
        value=f"<@{ctx.author.id}> любит {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def hit(ctx, message):
    random.shuffle(game_config.GIF_HIT)
    gif_url = random.choice(game_config.GIF_HIT)
    emb = discord.Embed()
    emb.add_field(
        name=f'Удар!',
        value=f"<@{ctx.author.id}> бьёт {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def rest(ctx):
    random.shuffle(game_config.GIF_REST)
    gif_url = random.choice(game_config.GIF_REST)
    emb = discord.Embed()
    emb.add_field(
        name=f'Лежать!',
        value=f"<@{ctx.raw_mentions[0]}> Лёг!")
    emb.set_image(url=gif_url)
    return emb


async def slap(ctx, message):
    random.shuffle(game_config.GIF_SLAP)
    gif_url = random.choice(game_config.GIF_SLAP)
    emb = discord.Embed()
    emb.add_field(
        name=f'Шлёп!',
        value=f"<@{ctx.author.id}> шлёпает {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def poke(ctx, message):
    random.shuffle(game_config.GIF_POKE)
    gif_url = random.choice(game_config.GIF_POKE)
    emb = discord.Embed()
    emb.add_field(
        name=f'Тык',
        value=f"<@{ctx.author.id}> тыкает {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def take_hand(ctx, message):
    random.shuffle(game_config.GIF_TAKEHAND)
    gif_url = random.choice(game_config.GIF_TAKEHAND)
    emb = discord.Embed()
    emb.add_field(
        name=f'Взять за руку',
        value=f"<@{ctx.author.id}> берёт за руку {message[3]}")
    emb.set_image(url=gif_url)
    return emb


async def stroke(ctx, message):
    random.shuffle(game_config.GIF_STROKE)
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


async def lick(ctx, message):
    random.shuffle(game_config.GIF_LICK)
    gif_url = random.choice(game_config.GIF_LICK)
    emb = discord.Embed()
    emb.add_field(
        name=f'Лизь',
        value=f"<@{ctx.author.id}> облизывает {message[1]}")
    emb.set_image(url=gif_url)
    return emb


async def sex(ctx):
    emb = discord.Embed()
    emb.add_field(
        name=f':white_check_mark: = Да.  :negative_squared_cross_mark: = Нет ',
        value=f'<@{ctx.raw_mentions[0]}> даёшь ли ты своё согласие на секс c <@{ctx.author.id}>?')
    return emb


async def sex_accept(husband, wife):
    gif_url = random.choice(game_config.GIF_SEX)
    emb = discord.Embed()
    description = f"<@{husband}> занимается сексом с <@{wife}>" if husband != wife else f"<@{husband}> дрочит."
    emb.add_field(
        name=f'Секс',
        value=description)
    emb.set_image(url=gif_url)
    return emb


async def sex_history(ctx, channel, whore=None):
    db = sql_db(config.db_name)
    if whore is None:
        if channel.id in [726050381481902080, 718840575238864956]:
            history = db.get_marriage_accounts(f"marriage_{ctx.guild.name.strip().replace(' ', '_')}")
            if history is not None:
                sex_count = {}
                sex_historyes = {}
                for member in history:
                    if member['sex_count'] is not None and member['sex_history'] is not None:
                        sex_count[member['discord_id']] = member['sex_count']
                        sex_historyes[member['discord_id']] = member['sex_history'].split()
                text = ''
                count = 0
                for member, history in sex_historyes.items():
                    count += 1
                    partners = ''
                    for partner in sex_historyes[member]:
                        name = f"<@{partner.split(':')[0]}>" if int(partner.split(':')[0]) != int(
                            member) else "``Дрочит``"
                        partners += f"\n\t\t{name} - {' '.join(game_logic.ending_check(partner.split(':')[1]))}"
                    text += f"\n\n💞 <@{member}> ``-> {sex_count[member]}``\nПартнёры:{partners}"

                    if count == 5:
                        emb = discord.Embed(description=text, color=0xFA8072)
                        emb.set_footer(text=f"История сексов {ctx.guild.name}", icon_url=ctx.guild.icon_url)
                        await channel.send(embed=emb)
                        emb.clear_fields()
                        text = ''
                        count = 0
                if len(text) > 1:
                    emb = discord.Embed(description=text, color=0xFA8072)
                    emb.set_footer(text=f"История сексов {ctx.guild.name}", icon_url=ctx.guild.icon_url)
                    await channel.send(embed=emb)
                    emb.clear_fields()
    else:
        history = db.get_marriage_account(f"marriage_{ctx.guild.name.strip().replace(' ', '_')}", int(whore))
        if history is None:
            await channel.send("Ничего не найдено")
        else:
            partners = ''
            if history['sex_count'] is not None and history['sex_history'] is not None:
                sex_count = history['sex_count']
                sex_historyes = history['sex_history'].split()
                for partner in sex_historyes:
                    name = f"<@{partner.split(':')[0]}>" if int(partner.split(':')[0]) != int(whore) else "``Дрочит``"
                    partners += f"\n{name} - {' '.join(game_logic.ending_check(partner.split(':')[1]))}"
                emb = discord.Embed(description=f"💞 <@{whore}> ``-> {sex_count}``\n", color=0xFA8072)
                emb.add_field(
                    name='Партнёры:',
                    value=f"{partners}")
                emb.set_footer(text=f"История сексов {ctx.guild.name}", icon_url=ctx.guild.icon_url)
                await channel.send(embed=emb)
            else:
                await channel.send("*Ничего не найдено*")


async def marriage_history(ctx, channel):
    db = sql_db(config.db_name)
    history = db.get_marriage_accounts(f"marriage_{ctx.guild.name.strip().replace(' ', '_')}")
    date_now = datetime.date.today()
    marriages = {}
    marriages_date = {}
    marriages_history = {}
    marriages_count = {}
    for member in history:
        if member['spouse'] is not None and member['spouse'] not in marriages.keys():
            marriages[member['discord_id']] = member['spouse']
            year, month, day = member["date_of_marriage"].split(':')
            marriage_date = datetime.date(int(year), int(month), int(day))
            marriage_days = date_now - marriage_date
            marriages_date[member['discord_id']] = marriage_days.days
        if member['marriage_count'] is not None and member['marriage_history'] is not None:
            marriages_count[member['discord_id']] = member['marriage_count']
            marriages_history[member['discord_id']] = member['marriage_history'].split()
    text = ''
    count = 0
    for i in marriages.keys():
        if int(i) == int(marriages[i]):
            continue
        else:
            text += f"<@{i}> и <@{marriages[i]}> вместе уже **{marriages_date[i]}** дней :cupid:\n\n"
            count += 1
        if count == 10:
            emb = discord.Embed(
                description=text,
                color=0xFA8072)
            # if len(marriages_history[i]) > 1:
            #     partners = ''
            #     for partner in marriages_history[i]:
            #         partners += f"<@{partner.split('_')[1]}> "
            #     emb.add_field(
            #         name='💔 Бывшие:',
            #         value=f"{partners}")
            emb.set_footer(text=f"Люди нашедшие друг друга на {ctx.guild.name}", icon_url=ctx.guild.icon_url)
            await channel.send(embed=emb)
            emb.clear_fields()
            text = ''
            count = 0
    if len(text) > 1:
        emb = discord.Embed(
            description=text,
            color=0xFA8072)
        emb.set_footer(text=f"Люди нашедшие друг друга на {ctx.guild.name}", icon_url=ctx.guild.icon_url)
        await channel.send(embed=emb)
        emb.clear_fields()


async def anger(ctx):
    gif_list = game_config.GIF_ANGER
    random.shuffle(gif_list)
    gif_url = random.choice(gif_list)
    emb = discord.Embed()
    emb.add_field(
        name=f'Злость',
        value=f"<@{ctx.author.id}> злится")
    emb.set_image(url=gif_url)
    return emb


async def smoke(ctx):
    if ctx.author.id == 514780826085621771:
        gif_url = random.choice(game_config.OLIVIA_SMOKE)
    else:
        random.shuffle(game_config.GIF_SMOKE)
        gif_url = random.choice(game_config.GIF_SMOKE)
    emb = discord.Embed()
    if len(ctx.raw_mentions) > 0:
        paty = ''
        for i in ctx.raw_mentions:
            paty += f' <@{i}>'
        emb.add_field(
            name=f'Курить',
            value=f"<@{ctx.author.id}>{paty} курят 🚬")
    else:
        emb.add_field(
            name=f'Курить',
            value=f"<@{ctx.author.id}> курит 🚬")
    emb.set_image(url=gif_url)
    return emb


async def hookah(ctx):
    print("КАЛЬЯН")
    random.shuffle(game_config.GIF_HOOKAH)
    gif_url = random.choice(game_config.GIF_HOOKAH)
    emb = discord.Embed()
    if len(ctx.raw_mentions) > 0:
        paty = ''
        for i in ctx.raw_mentions:
            paty += f' <@{i}>'
        emb.add_field(
            name=f'Курить',
            value=f"<@{ctx.author.id}>{paty} курят кальян")
    else:
        emb.add_field(
            name=f'Кальян',
            value=f"<@{ctx.author.id}> курит кальян")
    emb.set_image(url=gif_url)
    return emb


async def dance(ctx):
    random.shuffle(game_config.GIF_DANCE)
    gif_url = random.choice(game_config.GIF_DANCE)
    emb = discord.Embed()
    if len(ctx.raw_mentions) > 0:
        paty = ''
        for i in ctx.raw_mentions:
            paty += f' <@{i}>'
        emb.add_field(
            name=f'Танцы',
            value=f"<@{ctx.author.id}>{paty} танцуют вместе <a:4325_MeMeMe:593485738004316190><a:4325_MeMeMe:593485738004316190><a:4325_MeMeMe:593485738004316190>")
    else:
        emb.add_field(
            name=f'Танцы',
            value=f"<@{ctx.author.id}> танцует <a:4325_MeMeMe:593485738004316190>")
    emb.set_image(url=gif_url)
    return emb


async def drink(ctx):
    if ctx.author.id == 514780826085621771:
        gif_url = random.choice(game_config.OLIVIA_DRINK)
    else:
        random.shuffle(game_config.GIF_DRINK)
        gif_url = random.choice(game_config.GIF_DRINK)
    drink_emoji = random.choice(game_config.DRINK_EMOJI)
    emb = discord.Embed()
    if len(ctx.raw_mentions) > 0:
        paty = ''
        for i in ctx.raw_mentions:
            paty += f' <@{i}>'
        emb.add_field(
            name=f'Бухать! <a:red_dance:593485736305623096>',
            value=f"<@{ctx.author.id}>{paty} бухают вместе  {drink_emoji}")
    else:
        emb.add_field(
            name=f'Бухать! <a:red_dance:593485736305623096>',
            value=f"<@{ctx.author.id}> бухает {drink_emoji}")
    emb.set_image(url=gif_url)
    return emb


async def marriage(ctx):
    emb = discord.Embed(title='``Новое предложение руки и сердца!`` :couple_with_heart:', color=0xF08080)
    emb.add_field(
        name=f':white_check_mark: = Да.  :negative_squared_cross_mark: = Нет ',
        value=f'<@{ctx.raw_mentions[0]}> даёшь ли ты своё согласие на брак c <@{ctx.author.id}>?')
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


async def marriage_fail(discord_id):
    emb = discord.Embed(color=0xF08080)
    emb.add_field(
        name=f'Есть одна проблемка',
        value=f"<@{discord_id}> уже в браке")
    return emb


async def marriage_self(ctx):
    emb = discord.Embed(color=0xF08080)
    emb.add_field(
        name=f'Есть одна проблемка',
        value=f"<@{ctx.author.id}> сочувствую твоему одиночеству, но тебе нужен кто-то другой.")
    return emb


async def divorce_complete(ctx, date):
    date_now = datetime.date.today()
    year, month, day = date.split(':')
    marriage_date = datetime.date(int(year), int(month), int(day))
    days = date_now - marriage_date
    gif_url = random.choice(game_config.GIF_SAD)
    emb = discord.Embed(color=0xF08080)
    emb.add_field(
        name=f'Разрыв брачных уз',
        value=f"<@{ctx.author.id}> разрывает брак с <@{ctx.raw_mentions[0]}> длившийся {days.days} дней")
    emb.set_image(url=gif_url)
    return emb


async def divorce_fail(ctx):
    emb = discord.Embed(color=0xF08080)
    emb.add_field(
        name=f'Есть одна проблемка',
        value=f"<@{ctx.raw_mentions[0]}> не в браке с <@{ctx.author.id}>")
    return emb


async def steam_id_info(steam_id):
    session = requests.Session()
    try:
        info_from_steam = session.get(
            f'http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={config.steam_api_key}'
            f'&steamids={steam_id}')
        if info_from_steam.ok:
            player_info = info_from_steam.json()['response']['players'][0]
            emb = discord.Embed(title='Информация об аккаунте **Steam**:',
                                color=0x000000)
            emb.add_field(
                name='Никнейм:',
                value=f"**{player_info['personaname']}**")
            if player_info['personastate'] == 1:
                stat = 'Онлайн'
            elif player_info['personastate'] == 2:
                stat = 'Занят'
            elif player_info['personastate'] == 3:
                stat = 'Нет на месте'
            elif player_info['personastate'] == 4:
                stat = 'Наелся и спит'
            else:
                stat = 'Не в сети'
            emb.add_field(
                name='Статус:',
                value=stat)
            info_about_old_nikname = session.post(f'https://steamcommunity.com/profiles/{steam_id}/ajaxaliases/')
            if info_about_old_nikname.ok:
                nik_history = ''
                for nik in info_about_old_nikname.json():
                    nik_history += f"`{nik['newname']}` *({nik['timechanged']})*\n"
                emb.add_field(
                    name='Другие имена:',
                    value=nik_history if len(nik_history) > 0 else 'Нет',
                    inline=False)
            emb.add_field(
                name='Ссылка на профиль:',
                value=player_info['profileurl'])
            emb.set_thumbnail(url=player_info['avatarfull'])
            emb.set_footer(text=f"SteamID:{steam_id}")
            return emb

    except requests.exceptions.ConnectionError:
        return 'Нельзя проверять слишком часто. Попробуйте через минутку.'


async def user_info(target, user):
    emb = discord.Embed(title='Информация о пользователе:',
                        color=target.color)
    emb.add_field(
        name='Имя:',
        value=target)
    emb.add_field(
        name='Имя на сервере:',
        value=target.nick if not 'None' else target.name)
    status = []
    if str(target.mobile_status) != 'offline':
        status.append('Mobile')
    if str(target.desktop_status) != 'offline':
        status.append('Desktop')
    if str(target.web_status) != 'offline':
        status.append('Web')
    emb.add_field(
        name='Активность:',
        value=f"{target.status} {' & '.join(status)}\n{target.activity}" if len(status) >= 1 else 'Offline',
        inline=False)
    emb.add_field(
        name=f'Подключился к {target.guild.name}:',
        value=f"{target.joined_at.day}.{target.joined_at.month}.{target.joined_at.year}")
    old = datetime.datetime.now() - target.created_at
    emb.add_field(
        name='Возраст аккаунта:',
        value=f"{old.days} дней",
        inline=False)
    roles = []
    for role in target.roles:
        roles.append(f"<@&{role.id}>\n")
    roles.reverse()
    emb.add_field(
        name='Роли',
        value=''.join(roles[:-1]) if len(roles) > 1 else 'Нет ролей')
    emb.set_thumbnail(url=target.avatar_url)
    return emb
