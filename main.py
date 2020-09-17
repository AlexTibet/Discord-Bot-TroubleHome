import asyncio
import discord
import datetime
import re
import websockets

from datastorage import SqliteDataStorage
import message_handlers
import gen_embedded_reply
import gen_emb_for_theisle
import server_info
from server_config_editor import editing_configuration
import config
from finde_and_download import download_server_saves, upload_server_saves


class MyClient(discord.Client):

    async def on_ready(self):
        """Действия при запуске бота (Отображение информации в консоль)"""
        print(f'Logged on as {self.user}!')
        for i in range(len(self.guilds)):
            print(f"Bot run on server '{self.guilds[i].name}' with serverID = {self.guilds[i].id},"
                  f" with {self.guilds[i].member_count} users")
        print(self.guilds)
        await MyClient.change_presence(self, status=discord.Status.online, activity=discord.Game('Кусь'))
        print(self.activity)
        print("Connecting to database...")
        sql_db = SqliteDataStorage(config.db_name)
        print("Connection to the database is complete.")
        # Добавление пользователей в базу данных
        for guild in self.guilds:  # для каждого сервера
            # создаём таблицы браков (для хранения данных о "браках" пользователей)
            sql_db.create_marriage_tabel(guild.name.strip().replace(' ', '_'))  # нельзя чтобы в названии был пробел
            table = None
            if re.search(config.BoB_server_name, guild.name):
                table = "BoB_Users"
            if re.search(config.TheIsle_server_name, guild.name):
                table = "TheIsle_Users"
            if table is not None:
                for member in guild.members:  # для каждого участника сервера
                    member_status = False
                    accounts = sql_db.get_accounts(table)
                    for account in accounts:
                        if account["discord_id"] == member.id:
                            print(f"{member} уже есть в базе данных (Таблица: {table} ID:{member.id})")
                            member_status = True
                            break
                    if member_status is not True and table is not None:
                        sql_db.create_account(table, member.id)
                        print(f"{member} добавлен в базу данных (Таблица: {table} с ID:{member.id}")
                continue
            print("Run online activity check")
            await self.starting_online_check()

    async def on_message(self, ctx):
        """Смотрим каждое сообщение в доступных каналах, выводим в консоль и обрабатываем"""
        print(f"{ctx.guild}| {ctx.channel} | {ctx.author} |{ctx.content}")
        channel = discord.Client.get_channel(self, ctx.channel.id)
        message = ctx.content.split()
        if channel.id in config.ADMIN_CHANNEL:  # channel id list
            try:
                if re.search(r"[\d]{17}", message[0].split("/")[0].split("<")[0]):
                    steam_id = message[0].strip()
                    steam_find_url = f'https://steamidfinder.com/lookup/{steam_id}/'
                    await channel.send(steam_find_url)

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
            except IndexError:
                pass

        if channel.id in config.INFO_CHANNEL:
            try:
                if re.search(r"^[Ии]нфо", message[0]) and len(ctx.raw_mentions) == 1:
                    target = ctx.author.guild.get_member(ctx.raw_mentions[0])
                    user = discord.Client.get_user(self, target.id)
                    emb = await gen_embedded_reply.user_info(target, user)
                    await channel.send(embed=emb)
            except IndexError:
                pass

        if channel.id in config.GAME_CHANNEL:  # channel id list
            await message_handlers.game_message(ctx, channel, self)

        if channel.id in config.DINO_CHANNEL:  # channel id list
            try:
                if re.search(r"^[Дд]ино\b", message[0]) and re.search(r"^[Ии]нфо\b", message[1]):
                    emb = await gen_emb_for_theisle.database_check(message)
                    await channel.send(embed=emb)
                    emb = await gen_emb_for_theisle.dino_info(ctx, message)
                    await channel.send(embed=emb)

                elif re.search(r"^[Вв]ыдать\b", message[0]) and re.search(r"^[Дд]ино\b", message[1]):
                    emb = await gen_emb_for_theisle.give_dino(message, channel)
                    await channel.send(embed=emb)

                elif re.search(r"^[Сс]писок\b", message[0]) and re.search(r"^[Дд]ино\b", message[1]):
                    await gen_emb_for_theisle.dino_catalog(channel)
            except IndexError:
                pass
        if channel.id == config.TEST_SERVER_CONFIG_CHANNEL or channel.id == config.SERVER_CONFIG_CHANNEL:
            try:
                if re.search(r'[Пп]рописать', message[0]) or re.search(r'[Сс]нять', message[0]):
                    if role_access(ctx, config.TECHNIC_ROLE):
                        await editing_configuration(channel, message)
                    else:
                        await channel.send(embed=await gen_embedded_reply.no_access())
                elif re.search(r'[Пп]еренести', message[0]) and re.search(r'с[еэ]йвы', message[1]):
                    if role_access(ctx, config.TECHNIC_ROLE):
                        await channel.send('```http\nНачинаю скачивание базы данных с основного сервера\n```')
                        test_server = (config.test_host, config.test_port, config.test_login, config.test_password,
                                       config.test_saves_directory)
                        main_server = (config.main_host, config.main_port, config.main_login, config.main_password,
                                       config.main_saves_directory)
                        if download_server_saves(main_server):
                            await channel.send('☑ *База данных основного сервера скопирована*')

                        else:
                            await channel.send('❌ *Ошибка. Не удалось скопировать базу данных основного сервера*')
                            raise IndexError
                        await channel.send('☑ *Загружаю базу данных на тестовый сервер*')
                        if upload_server_saves(test_server):
                            await channel.send('☑ *База данных основного сервера загружена на тестовый сервер*')
                            await channel.send('```http\n'
                                               'Перенос базы данных завершен, можно запускать тест-сервер\n```')
                        else:
                            await channel.send('❌ *Ошибка. Не удалось загрузить базу данных на тестовый сервер*')
                            await channel.send('```diff\nПеренос базы данных не удался\n```')
                            raise IndexError
            except IndexError:
                pass

    async def on_member_join(self, member):
        join_time = datetime.datetime.now()
        ban_time = datetime.timedelta(days=1)
        if ban_time > join_time - member.created_at:
            channel = discord.Client.get_channel(self, config.ADMIN_CHANNEL[1])
            user = discord.Client.get_user(self, member.id)
            emb = await gen_embedded_reply.user_info(member, user)
            await channel.send(f'<@{member.id}> *это новенький акк которому менее суток*\n'
                               f'*возможно стоит обратить внимание* 🍌 ', embed=emb)

    async def starting_online_check(self):
        while True:
            try:
                online = await server_info.bermuda_server_info()
                await client.online_activity(online)
                print(f"{self} установил статус, ожидание")
                await asyncio.sleep(30)
            except Exception as  error:
                print(error)
                await asyncio.sleep(30)
                continue

    async def online_activity(self, info):
        try:
            online = f"{info['players']['active']} из {info['players']['total']}"
        except TypeError:
            online = "Оффлайн"
        game = discord.Game(online)
        try:
            await client.change_presence(status=discord.Status.online, activity=game)
        except websockets.exceptions.ConnectionClosedOK:
            game = discord.Game("Обновляю информацию")
            await client.change_presence(status=discord.Status.online, activity=game)

    async def on_raw_message_delete(self, payload):
        if payload.channel_id in config.ADMIN_CHANNEL:
            channel = discord.Client.get_channel(self, payload.channel_id)
            await channel.send(f"`А х*й ты чё тут удалишь!`\nЭто <#{payload.channel_id}>!!!\n"
                               f"**{payload.cached_message.author}** отправлял сообщение:\n"
                               f"{payload.cached_message.content}")
            for emb in payload.cached_message.embeds:
                await channel.send(embed=emb)
            for attach in payload.cached_message.attachments:
                await channel.send(attach.url)
                await channel.send(attach.proxy_url)

    # async def on_raw_message_edit(self, payload):
    #     if payload.channel_id in config.ADMIN_CHANNEL:
    #         channel = discord.Client.get_channel(self, payload.channel_id)
    #         try:
    #             author = payload.cached_message.author
    #         except AttributeError:
    #             author = ''
    #         await channel.send(f"`А х*й ты чё тут исправишь просто так!`\nЭто <#{payload.channel_id}>!!!\n\n"
    #                            f"**{author}** `отправлял сообщение:`\n\n"
    #                            f"{payload.cached_message.content}")
    #         await channel.send(f"\n`И исправил так:`\n{payload.data['content']}")


def role_access(ctx, access_list) -> bool:
    """Checking access member to command"""
    for i in ctx.author.roles:
        if i.id in access_list:
            return True
    else:
        return False


# RUN
client = MyClient()
client.run(config.TOKEN)
