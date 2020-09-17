import re
import gen_embedded_reply
import game_logic
import discord


async def game_message(ctx, channel, bot):
    message = ctx.content.split()
    try:
        if re.search(r"^[Кк]усь\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.bite(ctx, message))

        elif re.search(r"^[Кк]то\b", message[0]) and re.search(r"^[Яя]\b", message[1]):
            await channel.send(embed=await gen_embedded_reply.who_am_i(ctx))

        elif re.search(r"^[Шш]ипперить\b", message[0]) and re.search(r"[\d]{18}", message[1]) and re.search(
                r"[\d]{18}", message[2]):
            await channel.send(embed=await gen_embedded_reply.shipper(message))
        elif re.search(r"^[Оо]бнять\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.hug(ctx, message))

        elif re.search(r"^[Пп]окормить\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.feed(ctx))

        elif (re.search(r"^[Пп]оцеловать\b", message[0]) or re.search(r"^[Зз]асосать\b", message[0]) or
                re.search(r"^[Цц]еловать\b", message[0])) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.kiss(ctx, message))

        elif (re.search(r"^[Лл]юбить\b", message[0]) or re.search(r"^[Лл]юблю\b", message[0])) and \
                re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.love(ctx, message))

        elif re.search(r"^[Уу]дарить\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.hit(ctx, message))

        elif re.search(r"^[Лл]ежать\b", message[1]) and re.search(r"[\d]{18}", message[0]):
            await channel.send(embed=await gen_embedded_reply.rest(ctx))

        elif (re.search(r"^[Шш]л[её]п\b", message[0]) or re.search(r"^[Шш]л[её]пнуть\b", message[0])) and re.search(
                r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.slap(ctx, message))

        elif (re.search(r"^[Тт]ык\b", message[0]) or re.search(r"^[Тт]ыкнуть\b", message[0])) and re.search(
                r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.poke(ctx, message))

        elif re.search(r"^[Вв]зять\b", message[0]) and re.search(r"за", message[1]) and re.search(
                r"руку", message[2]) and re.search(r"[\d]{18}", message[3]):
            await channel.send(embed=await gen_embedded_reply.take_hand(ctx, message))

        elif (re.search(r"^[Гг]ладить\b", message[0]) or re.search(r"^[Пп]огладить\b", message[0])) and re.search(
                r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.stroke(ctx, message))

        elif (re.search(r"^[Лл]изь\b", message[0]) or re.search(r"^[Лл]изнуть\b", message[0])) and re.search(
                r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.lick(ctx, message))

        elif re.search(r"^[Гг]русть\b", message[0]) or re.search(r"^[Пп]ечаль\b", message[0]):
            await channel.send(embed=await gen_embedded_reply.sad(ctx))

        elif re.search(r"^[Зз]лость\b", message[0]):
            await channel.send(embed=await gen_embedded_reply.anger(ctx))

        elif re.search(r"^[Кк]урить\b", message[0]):
            await channel.send(embed=await gen_embedded_reply.smoke(ctx))

        elif re.search(r"^[Бб]ухать\b", message[0]) or re.search(r"^[Пп]ить\b", message[0]):
            await channel.send(embed=await gen_embedded_reply.drink(ctx))

        elif re.search(r"^[Кк]альян\b", message[0]):
            await channel.send(embed=await gen_embedded_reply.hookah(ctx))

        elif re.search(r"^[Тт]анцевать\b", message[0]):
            await channel.send(embed=await gen_embedded_reply.dance(ctx))

        elif re.search(r"^[Бб]рак\b", message[0]) and (re.search(r"[\d]{18}", message[1]) or re.search(r"[\d]{18}", message[2])):
            if await game_logic.marriage_check_self(ctx):
                await channel.send(embed=await gen_embedded_reply.marriage_self(ctx))
            elif await game_logic.marriage_check_husband(ctx):
                await channel.send(embed=await gen_embedded_reply.marriage_fail(ctx.author.id))
            elif await game_logic.marriage_check_wife(ctx, bot):
                await channel.send(embed=await gen_embedded_reply.marriage_fail(ctx.raw_mentions[0]))
            else:
                marriage_msg = await channel.send(embed=await gen_embedded_reply.marriage(ctx))
                await marriage_msg.add_reaction('✅')
                await marriage_msg.add_reaction('❎')
                await channel.send(embed=await game_logic.marriage_logic(ctx, bot))

        elif re.search(r"^[Рр]азвод\b", message[0]):
            await channel.send(embed=await game_logic.divorce(ctx, bot))

        elif (re.search(r"^[Сс]екс\b", message[0]) or re.search(r"^[Тт]рахнуть\b", message[0])) and re.search(
                r"[\d]{18}", message[1]):
            if channel.id == 739370283571478590:
                await channel.send(embed=await gen_embedded_reply.sex_accept(ctx.author.id, ctx.raw_mentions[0]))
            else:
                marriage_msg = await channel.send(embed=await gen_embedded_reply.sex(ctx))
                await marriage_msg.add_reaction('✅')
                await marriage_msg.add_reaction('❎')
                await channel.send(embed=await game_logic.sex_logic(ctx, bot))

        elif re.search(r"^[Ии]стория\b", message[0]) and re.search(r"браков\b", message[1]):
            try:
                await channel.send(embed=await gen_embedded_reply.marriage_history(ctx, channel))
            except discord.errors.HTTPException:
                pass
        elif re.search(r"^[Ии]стория\b", message[0]) and re.search(r"сексов\b", message[1]):
            if len(ctx.raw_mentions) == 1:
                await gen_embedded_reply.sex_history(ctx, channel, whore=ctx.raw_mentions[0])
            else:
                await gen_embedded_reply.sex_history(ctx, channel)

        elif re.search(r"^[Нн]а\b", message[0]) and re.search(r"ком", message[1]) and re.search(
                r"поиграть", message[2]):
            await channel.send(embed=await gen_embedded_reply.who_should_i_play(ctx))
    except IndexError:
        pass  # просто сообщение, не команда
