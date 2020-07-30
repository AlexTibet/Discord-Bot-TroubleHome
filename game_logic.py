import random
import game_config
import discord
from datastorage import SqliteDataStorage
import datetime
import gen_embedded_reply
import config
import asyncio


async def bite_logic(message: str) -> (str, str, str):
    victim = message[1].replace('<', '').replace('!', '').replace('@', '').replace('>', '').replace(',', '')
    targets = random.choice(game_config.TARGET)
    gif_id = targets[1]
    target = targets[0]
    return target, victim, gif_id


async def shipper_logic(message: str) -> (str, str, str, str):
    victim_one = message[1]
    victim_two = message[2]
    compatibility = [i for i in range(101)]
    random.shuffle(compatibility)
    compatibility = random.choice(compatibility)
    title = None
    if compatibility <= 20:
        title = 'Ну такое...'
    elif 20 < compatibility < 50:
        title = 'Могут попробовать'
    elif 50 <= compatibility < 70:
        title = 'Хорошая пара'
    elif 70 <= compatibility <= 85:
        title = 'Отличная пара'
    elif 85 < compatibility <= 95:
        title = 'Идеальная пара'
    elif compatibility > 95:
        title = 'Созданы друг для друга!'
    return victim_one, victim_two, compatibility, title


async def marriage_check_wife(ctx, message, bot):
    wife = discord.Client.get_user(bot, int(
        message[1].replace('<', '').replace('!', '').replace('@', '').replace('>', '').replace(',', '')))
    wife_member = ctx.author.guild.get_member(wife.id)
    for role in wife_member.roles:
        if role.id == config.MARRIAGE_ROLE:
            return True
    return False


async def marriage_check_husband(ctx):
    husband = ctx.author
    for role in husband.roles:
        if role.id == config.MARRIAGE_ROLE:
            return True
    return False


async def marriage_logic(ctx, message, bot):
    husband = discord.Client.get_user(bot, ctx.author.id)
    wife = discord.Client.get_user(bot, int(
        message[1].replace('<', '').replace('!', '').replace('@', '').replace('>', '').replace(',', '')))
    try:
        answer = await discord.Client.wait_for(bot,
                                               event='reaction_add',
                                               check=lambda reaction, user: user == wife,
                                               timeout=60.0)
        # print(answer) (<Reaction emoji='✅' me=True count=2>, <Member id=200987782674513921 name='Pixelcat' discriminator='3840' bot=False nick=None guild=<Guild id=585729392907517962 name='TIbetTestDis' shard_id=None chunked=True member_count=20>>)
        if answer[0].emoji == '✅':
            marriage_role = discord.utils.get(ctx.author.guild.roles, id=config.MARRIAGE_ROLE)
            wife_member = ctx.author.guild.get_member(wife.id)
            await wife_member.add_roles(marriage_role)
            await ctx.author.add_roles(marriage_role)
            return await gen_embedded_reply.marriage_accept(husband.id, wife.id)
        elif answer[0].emoji == '❎':
            return await gen_embedded_reply.marriage_rejected(husband.id, wife.id)
    except asyncio.TimeoutError:
        return await gen_embedded_reply.marriage_rejected(husband.id, wife.id)
