import asyncio
import discord
import datetime
import logging
import websockets
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
        logging.info(f'Logged on as {self.user}!')
        for i in range(len(self.guilds)):
            logging.info(f"Bot run on server '{self.guilds[i].name}' with serverID = {self.guilds[i].id},"
                         f" with {self.guilds[i].member_count} users")
        game = discord.Game("Кусь")
        await client.change_presence(status=discord.Status.online, activity=game)
        await self.starting_online_check()
        logging.info("Run online activity check")

    async def on_message(self, ctx: discord.Message):
        """
        Метод обработки события отправки сообщения любым пользователем в любой канал.
        Смотрим каждое сообщение в доступных каналах, выводим в консоль и обрабатываем
        Вызываем функции обработки сообщений соответствующих категорий команд
        """
        channel = discord.Client.get_channel(self, ctx.channel.id)

        await message_handlers.message_logging(ctx)
        await message_handlers.moderators_message(ctx, channel)

        if channel.id in config.ADMIN_CHANNEL:
            await message_handlers.admin_message(ctx, channel)

        if channel.id in config.GAME_CHANNEL:
            await message_handlers.game_message(self, ctx, channel)

        if channel.id in config.ADMIN_CHANNEL or channel.id in config.GAME_CHANNEL:
            await message_handlers.user_info_message(ctx, channel)

        if channel.id == config.TEST_SERVER_CONFIG_CHANNEL or channel.id == config.SERVER_CONFIG_CHANNEL:
            await message_handlers.server_config_message(ctx, channel)

        if channel.id in config.PROPOPOSITION_CHANNEL:
            await ctx.add_reaction('<a:6093_Animated_Checkmark:653294316134989834>')
            await ctx.add_reaction('<a:1603_Animated_Cross:653294299642855453>')

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
                online_rs = await server_info.bermuda_server_info((config.main_host, config.main_query_port))
                # online_ap = await server_info.bermuda_server_info((config.ap_host, config.ap_query_port))
                await client.online_activity(online_rs)
                await asyncio.sleep(30)
            except Exception as error:
                logging.info("Ошибка проверки онлайна\n", error)
                await asyncio.sleep(30)
                continue

    async def online_activity(self, info_rs: dict):
        """
        Выставление в качестве статуса бота данных о текущем онлайне серверов
        info: словарь со словарём вида info = {'players': {'active': 96, 'total': 100 }}'
        с данными о текущем онлайне
        """
        try:
            count = int(info_rs['player_count'])
            max_count = int(info_rs['max_players'])
            online = f"{count} из {max_count}"

        except TypeError as error:
            logging.info(error)
            online = "Кусь"
        guild = self.get_guild(config.MAIN_DISCORD_ID)
        rs_count_channel = guild.get_channel(config.RS_CHANNEL_ID)
        await rs_count_channel.edit(name=f"Rival {info_rs['player_count']} из {info_rs['max_players']}")
        game = discord.Game(online)
        try:
            await client.change_presence(status=discord.Status.online, activity=game)
        except websockets.exceptions.ConnectionClosedOK:
            game = discord.Game("Обновляю информацию")
            await client.change_presence(status=discord.Status.online, activity=game)


# RUN
if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.members = True
    logging.basicConfig(filename='bot.log', level=logging.INFO)
    client = MyClient(intents=intents)
    client.run(config.TOKEN)
