import re
from datetime import datetime
import gen_embedded_reply
import game_logic
import discord
from server_info import check_admin_online
import config
from server_config_editor import editing_configuration
from finde_and_download import download_server_saves, upload_server_saves


def role_access(ctx: discord.Message, access_list: list) -> True or False:
    """
    Проверяем имеет ли пользователь доступ к команде
    ctx: контекст из которого выделяем "роли" автора сообщения
    access_list: список ролей которые дают доступ к команде
    """
    for i in ctx.author.roles:
        if i.id in access_list:
            return True
    else:
        return False


def command_handler(fn):
    """
    Сообщение обычно не является командой, в таких случаях при его обработке вылетит IndexError
    Ловим его и продолжаем ждать команды
    """
    async def wrapper(*args, **kwargs):
        try:
            await fn(*args, **kwargs)
        except IndexError:
            pass
    return wrapper


async def ban_handler(ctx: discord.Message, channel: discord.TextChannel):
    if ctx.author.id in config.BAN_LIST.keys():
        await channel.send(embed=await gen_embedded_reply.banned_user(ctx.author.id))
        raise IndexError
    for i in ctx.raw_mentions:
        if i in config.BAN_LIST.keys():
            await channel.send(embed=await gen_embedded_reply.banned_user(i))
            raise IndexError


async def message_logging(ctx: discord.Message):
    """
    Логгирование (вывод в консоль и запись в файл message_history.txt)
    всех сообщений со всех чатов к которым у бота есть доступ
    Включая "embeds" и ссылки на вложеные файлы
    """
    time = str(datetime.now().time())
    message_history = f"{time[0:8]}|{ctx.guild}| {ctx.channel} | {ctx.author} |{ctx.content}\n"
    if len(ctx.embeds) > 0:
        for emb in ctx.embeds:
            message_history += f"EMBED\nTitle:{emb.title}\nDescription:{emb.description}\nurl:{emb.url}\n"
            for field in emb.fields:
                message_history += f"field:{field}\n"
    if len(ctx.attachments) > 0:
        for attachment in ctx.attachments:
            message_history += f"\tВложение:{attachment.url}\n"
    # print(message_history)
    with open('message_history.txt', 'a', encoding='utf-8') as file:
        file.write(message_history)


@command_handler
async def moderators_message(ctx: discord.Message, channel: discord.TextChannel):
    """
    Обработка сообщения на наличие команд модератора
    Доступные комманды:
        !Мут ТэгПользователя
            С пользователя снимаются все роли, добавляется роль "Токсика"
            запрещающая писать в чаты. В канал в котором использована команда
            отпровляется сообщение о снятых ролях и ссылка на канал с правилами дискорда.
    """
    if re.search(r'^![Мм]ут', ctx.content.split()[0]):
        if role_access(ctx, config.MODERATOR_ROLES):
            toxic = ctx.author.guild.get_member(ctx.raw_mentions[0])
            if toxic.bot:   # Невозможно снять роли с бота, поэтому выдать мут боту не получится
                await channel.send('**Нельзя дать мут боту**')
                raise IndexError
            old_roles = [f'<@&{i.id}>' for i in toxic.roles[1:]]
            toxic_role = discord.utils.get(ctx.author.guild.roles, id=config.TOXIC_ROLE)
            for i in toxic.roles[1:]:
                role = discord.utils.get(ctx.author.guild.roles, id=i.id)
                try:
                    await toxic.remove_roles(role)
                except (discord.Forbidden, discord.HTTPException):
                    continue
            await toxic.add_roles(toxic_role)
            emb = discord.Embed(title=f"{toxic} получает мут в дискорде {ctx.author.guild.name}", color=0xf6ff00)
            emb.add_field(
                name='Сняты роли:',
                value='\n'.join(old_roles))
            await channel.send(f'<@{toxic.id}> `Вы получите роль`<@&{toxic_role.id}>\n'
                               f'`которая не позволит Вам пользоваться чатами.\n'
                               f'Пожалуйста ознакомьтесь с`<#{config.RULES_CHANNEL}>', embed=emb)
        else:
            await channel.send(embed=await gen_embedded_reply.no_access())


@command_handler
async def game_message(bot: discord.Client, ctx: discord.Message, channel: discord.TextChannel):
    """
    Обработка сообщения на наличие игровых команд бота
    (доступны в игровых каналах, список id каналов в config.GAME_CHANNEL)

    Доступные комманды:
        Кусь @user
            Игра "Кусь", команды пытается укусить упомянутого пользователя.
            Случайно выбирается цель укуса (голову, руку, ногу), есть вероятность провала,
            и случайно выбирается подходящее под цель gif изображение
            Настройки: цели в game_config.TARGET, gif в game_config.GIF_KUS

        Кто я
            Игра "кто я?", случайный ответ из списка заготовленных ответов с локальными приколами
            Настройки: game_config.WHOAMI

        Шипперить @user1 @user2
            Игра "Шипперство", упоминаются два пользователя, случайно вычисляется их "совместимость"
            Случайно выбирается изображение с "шипперством", и любовные эмодзи

        Обнять @user / Покормить @user / Поцеловать @user / Любить @user / Ударить @user / @user Лежать / Шлёпнуть @user
        / Тыкнуть @user / Взять за руку @user / Погладить @user / Лизнуть @user
            Случайно выбирается подходящее под действие gif изображение
            И в чат отправляется сообщение с упоминанием что действие производится над @user

        Грусть / Злость
            Случайно выбирается подходящее под действие gif изображение
            И в чат отправляется сообщение с упоминанием автора команды

        Курить / Бухать / Кальян / Танцевать / Спать (@user) (@user) (@user)...
            Случайно выбирается подходящее под действие gif изображение
            И в чат отправляется сообщение с упоминанием автора команды и всех упомянутых им @user
            Так же может быть использована без упоминаний @user но с дополнительным словом (например курить сигареты)

        Брак @user
            Автор команды предлагает упомянутому @user вступить в брак.
            Создаётся сообщение с предложением @user на котором ему необходимо поставить реакцию
            При принятии предложения автор и @user заносятся в базу данных как супруги
            Также дата брака и идентификатор супруга заносятся в колонку истории браков
            Выбирается подходящее gif изображение и отправляется сообщение с поздравлением или с отказом от брака

        Развод @user
            Если автор команды и @user в браке, то брак удаляется из базы данных, но остаётся в истории
            Отправляется сообщение о разрыве со случайным gif изображением и упоминанием бывшего супруга

        Секс @user
            Создаётся сообщение с предложением @user на котором ему необходимо поставить реакцию
            При принятии предложения автор и @user добавляются друг другу в историю как партнёры
            Количество раз тоже учитывается

        История браков (@user)
            Без упоминания @user отправляется сообщение с полным списком всех действующих браков пользователей
            В списке указаны супруги и количество дней которые они состоят в браке
            С упоминанием @user отправляется сообщение с историей браков упомянутого @user
            В списке будет текущий статус (в браке / не в браке), количество дней в браке, прошлые браки и их даты

        История сексов (@user)
            (не рекомендуется использовать без @user)
            Без упоминания @user отправляется на каждого пользователя отправляется сообщение со списком его партнёров
            С указанием количества раз.
            С @user отправляется сообщение со списком партнёров и количества раз только для @user

        На ком поиграть
            Отправляется сообщение со случайным эмодзи и картинка из словаря game_config.BOB_DINO_EMOJI
    """
    message = ctx.content.split()
    message.append('-')
    message.append('-')
    message.append('-')
    if re.search(r"^[Кк]усь\b", message[0]) and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.bite(ctx))

    elif re.search(r"^[Кк]то\b", message[0]) and re.search(r"^[Яя]\b", message[1]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.who_am_i(ctx))

    elif re.search(r"^[Шш]ипперить\b", message[0]) and len(ctx.raw_mentions) == 2:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.shipper(ctx))

    elif re.search(r"^[Оо]бнять\b", message[0]) and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.hug(ctx))

    elif re.search(r"^[Тт]ереться\b", message[0]) and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.cuddle(ctx))

    elif re.search(r"^[Пп]окормить\b", message[0]) and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.feed(ctx))

    elif (re.search(r"^[Пп]оцеловать\b", message[0]) or re.search(r"^[Зз]асосать\b", message[0]) or
            re.search(r"^[Цц]еловать\b", message[0])) and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.kiss(ctx))

    elif (re.search(r"^[Лл]юбить\b", message[0]) or re.search(r"^[Лл]юблю\b", message[0])) \
            and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.love(ctx))

    elif re.search(r"^[Уу]дарить\b", message[0]) and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.hit(ctx))

    elif re.search(r"^[Лл]ежать\b", message[1]) and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.rest(ctx))

    elif (re.search(r"^[Шш]л[её]п\b", message[0]) or re.search(r"^[Шш]л[её]пнуть\b", message[0])) \
            and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.slap(ctx))

    elif (re.search(r"^[Тт]ык\b", message[0]) or re.search(r"^[Тт]ыкнуть\b", message[0])) and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.poke(ctx))

    elif re.search(r"^[Вв]зять\b", message[0]) and re.search(r"за", message[1]) and re.search(
            r"руку", message[2]) and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.take_hand(ctx))

    elif (re.search(r"^[Гг]ладить\b", message[0]) or re.search(r"^[Пп]огладить\b", message[0])) \
            and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.stroke(ctx))

    elif (re.search(r"^[Лл]изь\b", message[0]) or re.search(r"^[Лл]изнуть\b", message[0])) \
            and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.lick(ctx))

    elif re.search(r"^[Гг]русть\b", message[0]) or re.search(r"^[Пп]ечаль\b", message[0]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.sad(ctx))

    elif re.search(r"^[Зз]лость\b", message[0]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.anger(ctx))

    elif re.search(r"^[Кк]урить\b", message[0]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.smoke(ctx))

    elif re.search(r"^[Бб]ухать\b", message[0]) or re.search(r"^[Пп]ить\b", message[0]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.drink(ctx))

    elif re.search(r"^[Кк]альян\b", message[0]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.hookah(ctx))

    elif re.search(r"^[Тт]анцевать\b", message[0]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.dance(ctx))
    if re.search(r"^[Сс]пать", message[0]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.player_sleep(ctx))

    elif re.search(r"^[Бб]рак\b", message[0]) and (re.search(r"[\d]{18}", message[1]) or re.search(r"[\d]{18}", message[2])):
        await ban_handler(ctx, channel)
        if await game_logic.marriage_check_self(ctx):
            await ctx.channel.send(embed=await gen_embedded_reply.marriage_self(ctx))
        elif await game_logic.marriage_check_husband(ctx):
            await ctx.channel.send(embed=await gen_embedded_reply.marriage_fail(ctx.author.id))
        elif await game_logic.marriage_check_wife(ctx):
            await ctx.channel.send(embed=await gen_embedded_reply.marriage_fail(ctx.raw_mentions[0]))
        else:
            await ctx.channel.send(embed=await game_logic.marriage_logic(ctx, bot))

    elif re.search(r"^[Рр]азвод\b", message[0]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await game_logic.divorce(ctx, bot))

    elif (re.search(r"^[Сс]екс\b", message[0]) or re.search(r"^[Тт]рахнуть\b", message[0])) \
            and len(ctx.raw_mentions) > 0:
        await ban_handler(ctx, channel)
        await channel.send(embed=await game_logic.sex_logic(ctx, bot))

    elif re.search(r"^[Ии]стория\b", message[0]) and re.search(r"браков\b", message[1]):
        await ban_handler(ctx, channel)
        if len(ctx.raw_mentions) == 1:
            await gen_embedded_reply.marriage_history(ctx, channel, target=ctx.raw_mentions[0])
        else:
            await channel.send(embed=await gen_embedded_reply.marriage_history(ctx, channel))

    elif re.search(r"^[Ии]стория\b", message[0]) and re.search(r"сексов\b", message[1]):
        await ban_handler(ctx, channel)
        if len(ctx.raw_mentions) == 1:
            await gen_embedded_reply.sex_history(ctx, channel, whore=ctx.raw_mentions[0])
        else:
            await gen_embedded_reply.sex_history(ctx, channel)

    elif re.search(r"^[Нн]а\b", message[0]) and re.search(r"ком", message[1]) and re.search(
            r"поиграть", message[2]):
        await ban_handler(ctx, channel)
        await channel.send(embed=await gen_embedded_reply.who_should_i_play(ctx))


@command_handler
async def admin_message(ctx: discord.Message, channel: discord.TextChannel):
    """
    Обработка сообщения на наличие команд администраторов
    (доступны в каналах администраторов список id каналов в config.ADMIN_CHANNEL)

    Доступные комманды:
        SteamID
            Обнаружив в первом сообщении набор цифр похожий на SteamID находим информацию о нём и отправляем

        Какой онлайн
            Подключаемся делаем запрос на сервер, и отвечаем какой онлайн

        Бустеры
            Отправляем сообщение со списком пользователей являющихся давших nitro boost нашему Discord серверу

        Сколько админов онлайн
            Скачиваем логи сервера, просматриваем активность администраторов
            Выводим список администраторов которые по логам зашли на сервер и не выходили (и количество убийств/смертей)
            Настройка: trouble_server_admins.trouble_admins_dict (Словарь формата {SteamID: DiscordID} администраторов)
    """
    message = ctx.content.split()
    if re.search(r"^[\d]{17}\b", message[0].split("/")[0].split("<")[0]):
        steam_id = message[0].strip()
        await channel.send(embed=await gen_embedded_reply.steam_id_info(steam_id))

    if re.search(r"^[Кк]ако[йв]\b", message[0]) and re.search(r"^[Оо]нлайн\b", message[1].replace('?', '')):
        await channel.send(embed=await gen_embedded_reply.online_info())

    if re.search(r'^[Бб]устеры', message[0]):
        boosters = []
        for buster in ctx.author.guild.premium_subscribers:
            boosters.append(f"<@{buster.id}>\n")
        emb = discord.Embed()
        emb.add_field(
            name='Имя:',
            value=f"Сейчас бустят сервер:\n{''.join(boosters)}")
        await channel.send(embed=emb)
    if re.search(r'[Сс]колько', message[0]) and re.search(r'админов', message[1]) and re.search('онлайн', message[2]):
        await channel.send(embed=await check_admin_online())

    if channel.id == config.ADMIN_CHANNEL[3] or channel.id == config.ADMIN_CHANNEL[6]:
        if re.search(r'[Сс]писок', message[0]) and re.search(r'прошмандовок', message[1]):
            await channel.send('**Топ-5**:')
            await gen_embedded_reply.whore_list(ctx, channel)


@command_handler
async def user_info_message(ctx: discord.Message, channel: discord.TextChannel):
    """
    Обработка сообщения на наличие команд запроса информации о пользователе
    (Доступно в игровых и админских чатах)

    Доступные команды:
        Инфо @user
            Отправляет сообщение с информацией о пользователе, его ролях, статусе,
            датой присоединения к серверу и возрастом аккаунта.
    """
    message = ctx.content.split()
    if re.search(r"^[Ии]нфо", message[0]) and len(ctx.raw_mentions) == 1:
        target = ctx.author.guild.get_member(ctx.raw_mentions[0])
        emb = await gen_embedded_reply.user_info(target)
        await channel.send(embed=emb)


@command_handler
async def server_config_message(ctx: discord.Message, channel: discord.TextChannel):
    """
    Обработка сообщения на наличие команд настройки конфигурации игрового сервера Beasts of Bermuda
    (Доступно в специальных каналах config.SERVER_CONFIG_CHANNEL и config.TEST_SERVER_CONFIG_CHANNEL)

    Доступные команды:
        Прописать / Снять (админку / тэг / цвет) SteamID SteamID SteamID ...
            Добавляет или удаляет в конфигурационный файл права администратора / тэг перед никнеймом / цвет никнейма
            для игрока(ов) SteamID SteamID SteamID ...
        Перенести сейвы
            Копирует базу данных основного игрового сервера, и загружает на тестовый игровой сервер
    """
    message = ctx.content.split()
    if re.search(r'[Пп]рописать', message[0]) or re.search(r'[Сс]нять', message[0]):
        if role_access(ctx, config.TECHNIC_ROLE):
            await editing_configuration(channel, message)
        else:
            await channel.send(embed=await gen_embedded_reply.no_access())
    elif re.search(r'[Пп]еренести', message[0]) and re.search(r'с[еэ]йвы', message[1]):
        if role_access(ctx, config.TECHNIC_ROLE):
            if len(message) > 2 and re.search(r'[Аа]п', message[2]):
                server_name = 'Ancestral_Plains'
                main_server = (server_name, config.ap_host, config.ap_port, config.ap_login, config.ap_password,
                               config.ap_saves_directory)
            else:
                server_name = 'Rival_Shores'
                main_server = (server_name, config.main_host, config.main_port, config.main_login, config.main_password,
                               config.main_saves_directory)
            await channel.send(f'```fix\nНачинаю скачивание базы данных с сервера {server_name}\n```')
            test_server = (server_name, config.test_host, config.test_port, config.test_login, config.test_password,
                           config.test_saves_directory)
            if download_server_saves(main_server):
                await channel.send(f'☑ *База данных сервера {server_name} скопирована*')
            else:
                await channel.send(f'❌ *Ошибка. Не удалось скопировать базу данных сервера {server_name}*')
                raise IndexError    # Прерываем выполнение функции
            await channel.send('☑ *Загружаю базу данных на тестовый сервер*')
            if upload_server_saves(test_server):
                await channel.send(f'☑ *База данных сервера {server_name} загружена на тестовый сервер*')
                await channel.send('```fix\n'
                                   'Перенос базы данных завершен, можно запускать тест-сервер\n```')
            else:
                await channel.send('❌ *Ошибка. Не удалось загрузить базу данных на тестовый сервер*')
                await channel.send('```diff\nПеренос базы данных не удался\n```')
                raise IndexError    # Прерываем выполнение функции

