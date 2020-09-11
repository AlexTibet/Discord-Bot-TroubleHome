import asyncio
import discord
import re
import datetime
import config
from datastorage import SqliteDataStorage
import gen_embedded_reply
import message_handlers
import gen_emb_for_theisle
import server_info
import websockets
import server_config_editor


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
        if channel.id == config.SERVER_CONFIG_CHANNEL:
            try:
                if re.search(r"^[Аа]дминка\b", message[0]) and re.search(r"^[\d]{17}\b", message[1].split("/")[0].split("<")[0]):
                    if role_access(ctx, [config.TECHNIC_ROLE, config.OWNER_ROLE]):
                        try:
                            server_config = await server_config_editor.editing_preparation()
                            response = await server_config_editor.add_server_admin(message[1], server_config)
                            if response:
                                emb = discord.Embed(title=f'✅ Готово', color=0x20B2AA)
                                emb.set_footer(text='Админка прописана, конфиг загружен на сервер')
                                await channel.send(embed=emb)
                        except FileNotFoundError:
                            emb = discord.Embed(title=f'❌ Сервер не отвечает.❌', color=0xFF0000)
                            await channel.send(embed=emb)
                    else:
                        emb = discord.Embed(title=f'❌ Нет доступа к команде ❌', color=0xFF0000)
                        await channel.send(embed=emb)
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
            online = await server_info.bermuda_server_info()
            await client.online_activity(online)
            print(f"{self} установил статус, ожидание")
            await asyncio.sleep(30)

    async def online_activity(self, info):
        online = f"{info['players']['active']} из {info['players']['total']}"
        game = discord.Game(online)
        try:
            await client.change_presence(status=discord.Status.online, activity=game)
        except websockets.exceptions.ConnectionClosedOK:
            game = discord.Game("Обновляю информацию")
            await client.change_presence(status=discord.Status.online, activity=game)
        print(self.activity)


async def role_access(ctx, access_list) -> bool:
    """Checking access member to command"""
    for i in ctx.author.roles:
        if i.id in access_list:
            return True
    else:
        return False

# RUN
client = MyClient()
client.run(config.TOKEN)
