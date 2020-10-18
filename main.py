import asyncio
import discord
import datetime
import re
import websockets

from datastorage import SqliteDataStorage
import message_handlers
import gen_embedded_reply
import server_info

import config


class MyClient(discord.Client):
    """
    Класс обработчик событий Discord
    """
    async def on_ready(self):
        """
        Действия при запуске бота
        (Отображение информации о названии серверов на которых запустился бот в консоль)
        """
        print(f'Logged on as {self.user}!')
        for i in range(len(self.guilds)):
            print(f"Bot run on server '{self.guilds[i].name}' with serverID = {self.guilds[i].id},"
                  f" with {self.guilds[i].member_count} users")
        print("Connecting to database...")
        sql_db = SqliteDataStorage(config.db_name)
        print("Connection to the database is complete.")
        # Добавление пользователей в базу данных
        await self.database_filling(sql_db)
        await self.starting_online_check()
        print("Run online activity check")

    async def on_message(self, ctx: discord.Message):
        """
        Метод обработки события отправки сообщения любым пользователем в любой канал.
        Смотрим каждое сообщение в доступных каналах, выводим в консоль и обрабатываем
        Вызываем функции обработки сообщений соответствующих категорий команд
        """
        await message_handlers.message_logging(ctx)

        channel = discord.Client.get_channel(self, ctx.channel.id)
        await message_handlers.moderators_message(ctx, channel)

        if channel.id in config.ADMIN_CHANNEL:
            await message_handlers.admin_message(ctx, channel)

        if channel.id in config.GAME_CHANNEL:
            await message_handlers.game_message(ctx, channel, self)

        if channel.id in config.ADMIN_CHANNEL or channel.id in config.GAME_CHANNEL:
            await message_handlers.user_info_message(ctx, channel, self)

        if channel.id == config.TEST_SERVER_CONFIG_CHANNEL or channel.id == config.SERVER_CONFIG_CHANNEL:
            await message_handlers.server_config_message(ctx, channel)

        if channel.id in config.DINO_CHANNEL:  # только для серверов The Isle
            await message_handlers.dino_from_the_isle_message(ctx, channel)

    async def on_member_join(self, member: discord.Member):
        """
        Метод обработки события появления нового пользователя на дискорд сервере
        Реализована проверка на "твинк"
        Если возраст аккаунта менее 1 дня информация о нём отправляется в чат администраторов
        """
        join_time = datetime.datetime.now()
        ban_time = datetime.timedelta(days=1)
        if ban_time > join_time - member.created_at:
            channel = discord.Client.get_channel(self, config.ADMIN_CHANNEL[1])
            emb = await gen_embedded_reply.user_info(member)
            await channel.send(f'<@{member.id}> *это новенький акк которому менее суток*\n'
                               f'*возможно стоит обратить внимание* 🍌 ', embed=emb)

    async def on_raw_message_delete(self, payload: discord.RawMessageDeleteEvent):
        """
        Метод обработки события удаления сообщения в любом канале к которому у бота есть доступ
        Для чатов администраторов реализован запрет на удаление сообщений
        Удалённое сообщение переотправляется в тот же чат в котором было удалено
        """
        if payload.channel_id in config.ADMIN_CHANNEL:
            channel = discord.Client.get_channel(self, payload.channel_id)
            await channel.send(f"`А ничего ты тут не удалишь!`\nЭто <#{payload.channel_id}>!!!\n"
                               f"**{payload.cached_message.author}** отправлял сообщение:\n"
                               f"{payload.cached_message.content}")
            for emb in payload.cached_message.embeds:
                await channel.send(embed=emb)
            for attach in payload.cached_message.attachments:
                await channel.send(attach.url)
                await channel.send(attach.proxy_url)

    # ОТКЛЮЧЕНО, в дальнейшем будет использовано для логгирования редактирований сообщений
    # async def on_raw_message_edit(self, payload):
    # """
    # Метод обработки события редактирования сообщения в любом канале к которому у бота есть доступ
    # Для чатов администраторов реализован запрет на редактирование сообщений
    # Первоначальное сообщение переотправляется в тот же чат в котором было отредактировано
    # """
    #     if payload.channel_id in config.ADMIN_CHANNEL:
    #         channel = discord.Client.get_channel(self, payload.channel_id)
    #         try:
    #             author = payload.cached_message.author
    #         except AttributeError:
    #             author = ''
    #         await channel.send(f"`А ничего ты тут не исправишь просто так!`\nЭто <#{payload.channel_id}>!!!\n\n"
    #                            f"**{author}** `отправлял сообщение:`\n\n"
    #                            f"{payload.cached_message.content}")
    #         await channel.send(f"\n`И исправил так:`\n{payload.data['content']}")

    @staticmethod
    async def starting_online_check():
        """
        Отслеживание ко-во игроков на игровом сервере и выставление в качестве статуса
        Пример: (Играет в 96 из 100)
        Каждые 30 сек отправляет запрос на хост, получает данные о текущем онлайне
        Вызывает метод подставляющий полученную информацию в статус бота
        """
        while True:
            try:
                online = await server_info.bermuda_server_info()
                await client.online_activity(online)
                await asyncio.sleep(30)
            except Exception as error:
                print(error)
                await asyncio.sleep(30)
                continue

    @staticmethod
    async def online_activity(info: dict):
        """
        Выставление в качестве статуса бота данных о текущем онлайне сервера
        info: словарь со словарём вида info = {'players': {'active': 96, 'total': 100 }}'
        с данными о текущем онлайне
        """
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

    async def database_filling(self, sql_db: SqliteDataStorage):
        """
        Создание и заполнение базы данных
        """
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


# RUN
client = MyClient()
client.run(config.TOKEN)
