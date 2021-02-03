import random
import game_config
import discord
import gen_embedded_reply
import config
import asyncio
from datastorage import SqliteDataStorage as sql_db


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


async def marriage_check_wife(ctx, bot) -> True or False:
    wife = discord.Client.get_user(bot, ctx.raw_mentions[0])
    wife_member = ctx.author.guild.get_member(wife.id)
    for role in wife_member.roles:
        if role.id == config.MARRIAGE_ROLE:
            return True
    return False


async def marriage_check_husband(ctx) -> True or False:
    husband = ctx.author
    for role in husband.roles:
        if role.id == config.MARRIAGE_ROLE:
            return True
    return False


async def marriage_check_self(ctx):
    if ctx.author.id == ctx.raw_mentions[0]:
        return True
    else:
        return False


async def marriage_logic(ctx, bot):
    marriage_msg = await ctx.channel.send(embed=await gen_embedded_reply.marriage(ctx))
    await marriage_msg.add_reaction('✅')
    await marriage_msg.add_reaction('❎')
    husband = discord.Client.get_user(bot, ctx.author.id)
    wife = discord.Client.get_user(bot, int(ctx.raw_mentions[0]))
    try:
        answer = await discord.Client.wait_for(bot,
                                               event='reaction_add',
                                               check=lambda reaction, user: reaction.message.id == marriage_msg.id and user == wife,
                                               timeout=120.0)
        if answer[0].emoji == '✅':
            marriage_role = discord.utils.get(ctx.author.guild.roles, id=config.MARRIAGE_ROLE)
            wife_member = ctx.author.guild.get_member(wife.id)
            db = sql_db(config.db_name)
            db.set_marriage_account(ctx.guild.name.strip().replace(' ', '_'), ctx.author.id, ctx.raw_mentions[0])
            db.set_marriage_account(ctx.guild.name.strip().replace(' ', '_'), ctx.raw_mentions[0], ctx.author.id)
            await wife_member.add_roles(marriage_role)
            await ctx.author.add_roles(marriage_role)
            return await gen_embedded_reply.marriage_accept(husband.id, wife.id)
        elif answer[0].emoji == '❎':
            return await gen_embedded_reply.marriage_rejected(husband.id, wife.id)
    except asyncio.TimeoutError:
        return await gen_embedded_reply.marriage_rejected(husband.id, wife.id)


async def sex_logic(ctx, bot):
    marriage_msg = await ctx.channel.send(embed=await gen_embedded_reply.sex(ctx))
    await marriage_msg.add_reaction('✅')
    await marriage_msg.add_reaction('❎')
    husband = discord.Client.get_user(bot, ctx.author.id)
    wife = discord.Client.get_user(bot, int(ctx.raw_mentions[0]))
    try:
        answer = await discord.Client.wait_for(bot,
                                               event='reaction_add',
                                               check=lambda reaction, user: reaction.message.id == marriage_msg.id and user == wife,
                                               timeout=120.0)
        if answer[0].emoji == '✅':
            db = sql_db(config.db_name)
            db.set_sex_in_marriage_account(ctx.guild.name.strip().replace(' ', '_'), ctx.author.id, ctx.raw_mentions[0])
            if ctx.author.id != ctx.raw_mentions[0]:
                db.set_sex_in_marriage_account(ctx.guild.name.strip().replace(' ', '_'), ctx.raw_mentions[0], ctx.author.id)
            return await gen_embedded_reply.sex_accept(husband.id, wife.id)
        elif answer[0].emoji == '❎':
            return await gen_embedded_reply.marriage_rejected(husband.id, wife.id)
    except asyncio.TimeoutError:
        return await gen_embedded_reply.marriage_rejected(husband.id, wife.id)


async def divorce(ctx, bot):
    db = sql_db(config.db_name)
    history = db.get_marriage_account(f"marriage_{ctx.guild.name.strip().replace(' ', '_')}", ctx.author.id)
    if history['spouse'] is None or history['spouse'] != ctx.raw_mentions[0]:
        return await gen_embedded_reply.divorce_fail(ctx)
    else:
        date = history["date_of_marriage"]
        db.divorce(ctx.guild.name.strip().replace(' ', '_'), ctx.author.id)
        db.divorce(ctx.guild.name.strip().replace(' ', '_'), ctx.raw_mentions[0])
        marriage_role = discord.utils.get(ctx.author.guild.roles, id=config.MARRIAGE_ROLE)
        wife_member = ctx.author.guild.get_member(ctx.raw_mentions[0])
        await ctx.author.remove_roles(marriage_role)
        await wife_member.remove_roles(marriage_role)
        return await gen_embedded_reply.divorce_complete(ctx, date)


def ending_check(n):
    non_ending, a_ending, stov = False, False, False
    if len(n) == 1:
        if "5" <= n <= "9" or n == "0":
            stov = True
        elif "2" <= n <= "4":
            a_ending = True
        else:
            non_ending = True
    else:
        if n[len(n) - 1] == "0" or "5" <= n[len(n) - 1] <= "9" or n[len(n) - 2] == "1":
            stov = True
        elif n[len(n) - 1] == "1" and n[len(n) - 2] != "1":
            non_ending = True
        else:
            a_ending = True
    if non_ending is True:
        return n, "раз"
    elif a_ending is True:
        return n, "раза"
    elif stov is True:
        return n, "раз"
