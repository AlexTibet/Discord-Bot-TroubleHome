import re
import gen_embedded_reply
import game_logic


async def game_message(ctx, channel, bot):
    message = ctx.content.split()
    try:
        for i in message:
            i.replace('<', '').replace('!', '').replace('@', '').replace('?', '').replace('>', '').replace(',', '')

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
            await channel.send(embed=await gen_embedded_reply.feed(ctx, message))

        elif (re.search(r"^[Пп]оцеловать\b", message[0]) or re.search(r"^[Зз]асосать\b", message[0]) or
                re.search(r"^[Цц]еловать\b", message[0])) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.kiss(ctx, message))

        elif (re.search(r"^[Лл]юбить\b", message[0]) or re.search(r"^[Лл]юблю\b", message[0])) and \
                re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.love(ctx, message))

        elif re.search(r"^[Уу]дарить\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.hit(ctx, message))

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

        elif (re.search(r"^[Сс]екс\b", message[0]) or re.search(r"^[Тт]рахнуть\b", message[0])) and re.search(
                r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.sex(ctx, message))

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

        elif re.search(r"^[Бб]рак\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            if await game_logic.marriage_check_husband(ctx):
                await channel.send(embed=await gen_embedded_reply.marriage_fail(ctx.author.id))
            elif await game_logic.marriage_check_wife(ctx, message, bot):
                await channel.send(embed=await gen_embedded_reply.marriage_fail(ctx.raw_mentions[0]))
            else:
                marriage_msg = await channel.send(embed=await gen_embedded_reply.marriage(ctx, message))
                await marriage_msg.add_reaction('✅')
                await marriage_msg.add_reaction('❎')
                await channel.send(embed=await game_logic.marriage_logic(ctx, message, bot))

        elif re.search(r"^[Пп]рошмандовки\b", message[0]):
            await channel.send(embed=await gen_embedded_reply.sex_history(ctx))



    except IndexError:
        pass  # просто сообщение, не команда
