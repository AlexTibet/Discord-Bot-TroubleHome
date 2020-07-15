import re
import gen_embedded_reply
import asyncio


async def game_message(ctx, channel):
    message = ctx.content.split()
    try:
        for i in message:
            i.replace('<', '').replace('!', '').replace('@', '').replace('?', '').replace('>', '').replace(',', '')

        if re.search(r"^[Кк]усь\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.bite(ctx, message))

        if re.search(r"^[Кк]то\b", message[0]) and re.search(r"^[Яя]\b", message[1]):
            await channel.send(embed=await gen_embedded_reply.who_am_i(ctx))

        if re.search(r"^[Шш]ипперить\b", message[0]) and re.search(r"[\d]{18}", message[1]) and re.search(
                r"[\d]{18}", message[2]):
            await channel.send(embed=await gen_embedded_reply.shipper(message))
        if re.search(r"^[Оо]бнять\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.hug(ctx, message))

        if re.search(r"^[Пп]окормить\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.feed(ctx, message))

        if (re.search(r"^[Пп]оцеловать\b", message[0]) or re.search(r"^[Зз]асосать\b", message[0]) or
                re.search(r"^[Цц]еловать\b", message[0])) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.kiss(ctx, message))

        if (re.search(r"^[Лл]юбить\b", message[0]) or re.search(r"^[Лл]юблю\b", message[0])) and \
                re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.love(ctx, message))

        if re.search(r"^[Уу]дарить\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.hit(ctx, message))

        if (re.search(r"^[Шш]л[её]п\b", message[0]) or re.search(r"^[Шш]л[её]пнуть\b", message[0])) and re.search(
                r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.slap(ctx, message))

        if (re.search(r"^[Тт]ык\b", message[0]) or re.search(r"^[Тт]ыкнуть\b", message[0])) and re.search(
                r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.poke(ctx, message))

        if re.search(r"^[Вв]зять\b", message[0]) and re.search(r"за", message[1]) and re.search(
                r"руку", message[2]) and re.search(r"[\d]{18}", message[3]):
            await channel.send(embed=await gen_embedded_reply.take_hand(ctx, message))

        if (re.search(r"^[Гг]ладить\b", message[0]) or re.search(r"^[Пп]огладить\b", message[0])) and re.search(
                r"[\d]{18}", message[1]):
            await channel.send(embed=await gen_embedded_reply.stroke(ctx, message))

        if re.search(r"^[Гг]русть\b", message[0]) or re.search(r"^[Пп]ечаль\b", message[0]):
            await channel.send(embed=await gen_embedded_reply.sad(ctx))

        if re.search(r"^[Бб]рак\b", message[0]) and re.search(r"[\d]{18}", message[1]):
            marry_message = await channel.send(embed=await gen_embedded_reply.marriage(ctx, message))
            print(marry_message)
            print(marry_message.id)
            await marry_message.add_reaction('✅')
            await marry_message.add_reaction('❎')
            try:
                member = None
                members = marry_message.guild.members
                message[1] = message[1].replace('<', '').replace('!', '').replace('@', '').replace('?', '').replace('>',
                                                                                                                    '').replace(
                    ',', '')
                for i in members:
                    print(i, i.id, message[1])
                    if i.id == int(message[1]):
                        member = i
                        print('\n!!!\n', member, '\n')
                print(member)
                if await marry_message.reaction_add('✅', member, timeout=60.0):
                    await channel.send('получилось')
            except asyncio.TimeoutError:
                await channel.send('👎')

    except IndexError:
        pass  # просто сообщение, не команда
