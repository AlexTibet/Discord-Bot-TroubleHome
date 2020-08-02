import discord
import re
import requests

import config
from datastorage import SqliteDataStorage
import gen_embedded_reply
import message_handlers


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
        for guild in self.guilds:   # для каждого сервера
            # создаём таблицы браков (для хранения данных о "браках" пользователей)
            sql_db.create_marriage_tabel(guild.name.strip().replace(' ', '_'))  # нельзя чтобы в названии был пробел
            table = None
            if re.search(config.BoB_server_name, guild.name):
                table = "BoB_Users"
            if re.search(config.TheIsle_server_name, guild.name):
                table = "TheIsle_Users"
            if table is not None:
                for member in guild.members:    # для каждого участника сервера
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
            except IndexError:
                pass

            try:
                if re.search(r"^[Кк]ако[йв]\b", message[0]) and re.search(r"^[Оо]нлайн\b", message[1].replace('?', '')):
                    await channel.send(embed=await gen_embedded_reply.online_info())
            except IndexError:
                pass

        if channel.id in config.GAME_CHANNEL:  # channel id list
            await message_handlers.game_message(ctx, channel, self)

        if channel.id in config.DINO_CHANNEL:  # channel id list
            try:
                if re.search(r"^[Дд]ино\b", message[0]) and re.search(r"^[Ии]нфо\b", message[1]):
                    emb = await gen_embedded_reply.database_check(message)
                    await channel.send(embed=emb)
                    emb = await gen_embedded_reply.dino_info(ctx, message)
                    await channel.send(embed=emb)

                elif re.search(r"^[Вв]ыдать\b", message[0]) and re.search(r"^[Дд]ино\b", message[1]):
                    emb = await gen_embedded_reply.give_dino(message, channel)
                    await channel.send(embed=emb)

                elif re.search(r"^[Сс]писок\b", message[0]) and re.search(r"^[Дд]ино\b", message[1]):
                    await gen_embedded_reply.dino_catalog(channel)
            except IndexError:
                pass


# RUN
client = MyClient()
client.run(config.TOKEN)
