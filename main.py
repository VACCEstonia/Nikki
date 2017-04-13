import discord
import requests
import json
import asyncio
import getmetar

import nikkidb

DISCORD_SERVER = 'YOUR_DISCORD_SERVER_ID'

CNL_TEST = 'TEST_CHANNEL_ID'
CNL_REQUESTS = 'REQUESTS_CHANNEL_ID'
CNL_VACCUA = 'PUBLIC_CHANNEL_ID'
CNL_NIKKI = 'BOT_CHANNEL_ID'

I_AM_NANCY = 'YOUR_BOT_API_KEY'

client = discord.Client()


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.channel.id == CNL_REQUESTS:
        result = ""
        num = ""
        for num in message.content.split(' '):
            if num.isdigit():
                result = nikkidb.check(message.author.id, num)
                if result == "OK":
                    break
        msg = ""
        if result == "USER_DUPLICATE":
            msg = "{0.author.mention}, I can't register this VATSIM id. Contact Community admins in Private Messages! \U0001f626 ".format(
                message)
            await client.send_message(message.channel, msg)
        elif result == "INVALID_CID":
            msg = "{0.author.mention}, you provided me invalid VATSIM id \U0001f626. Waiting for valid VATSIM id. (If you don't have VATSIM ID contact Community admins in Private Messages). ".format(
                message)
            await client.send_message(message.channel, msg)
        elif result == "OK":
            name = nikkidb.insert(message.author.id, num)
            msg = "There is new user {0.author.mention} on our server. Have a nice day! \U0001f603".format(message)
            await client.change_nickname(message.author, name)
            await client.add_roles(message.author, client.get_server(DISCORD_SERVER).roles[1])
            await client.send_message(client.get_channel(CNL_VACCUA), msg)
            await client.send_message(client.get_channel(CNL_TEST),
                                      'I have just added a user DiscordID: ' + message.author.mention + ' with VatsimID: ' + num)

    if message.channel.id == CNL_NIKKI:
        if message.content.startswith('!reg '):
            role = discord.utils.get(client.get_server(DISCORD_SERVER).roles, name="Community admins")
            if role in message.author.roles:
                params = message.content.split(' ')
                if len(params) == 3 and len(message.mentions) == 1:
                    result = ""
                    vatsimID = params[2]
                    member = message.mentions[0]
                    result = nikkidb.check(member.id, vatsimID)
                    if result == "OK":
                        name = nikkidb.insert(message.mentions[0].id, vatsimID)
                        await client.change_nickname(message.mentions[0], name)
                        await client.send_message(client.get_channel(CNL_NIKKI),
                                                  'I have just added a user ' + member.mention + ' with VatsimID: ' + vatsimID)
                    elif result == "INVALID_CID":
                        msg = "{0.author.mention}, invalid VATSIM ID".format(message)
                        await client.send_message(message.channel, msg)
                    elif result == "USER_DUPLICATE":
                        msg = "{0.author.mention}, user is already in DB!".format(message)
                        await client.send_message(message.channel, msg)
                else:
                    await client.send_message(message.channel, 'Invalid using of !reg.\nExample: !reg @Nikki 12345678')
            else:
                await client.send_message(message.channel,
                                          "{0.author.mention}, you don't have rights to use this feature!".format(
                                              message))

        if message.content == '!reglist':
            role = discord.utils.get(client.get_server(DISCORD_SERVER).roles, name="Community admins")
            if role in message.author.roles:
                answer = nikkidb.get_reg_list()
                reg_list = ''
                i = 0
                reg_list += '----------------USERS IN DB----------------\n'
                for row in answer:
                    user_info = client.get_server(DISCORD_SERVER).get_member(str(row[0]))
                    if user_info is None:
                        continue
                    name = str(user_info.nick)
                    reg_list += '| ' + str(i)
                    reg_list += ' | ' + name + ' | '
                    reg_list += str(row[1]) + ' |\n'
                    i += 1

                reg_list += '-----------------------------------------------\n'

                await client.send_message(message.channel, reg_list)
            else:
                await client.send_message(message.channel,
                                          "{0.author.mention}, you don't have rights to use this feature!".format(
                                              message))

        if message.content.startswith('!metar'):
            params = message.content.split(' ')
            apt = str(params[1]).upper()
            if len(params) != 2 or len(apt) != 4:
                await client.send_message(message.channel, 'Invalid using of !metar.\nExample: !metar UKBB')
            else:
                metar = getmetar.extract_metar(apt)
                if metar:
                    await client.send_message(message.channel, '{0.author.mention} '.format(message) + "```" + metar + "```")
                else:
                    await client.send_message(message.channel,
                                              "{0.author.mention} METAR is not available for {1}".format(message,
                                                                                                         apt))

        if message.content.startswith('!taf'):
            params = message.content.split(' ')
            apt = str(params[1]).upper()
            if len(params) != 2 or len(apt) != 4:
                await client.send_message(message.channel, 'Invalid using of !taf.\nExample: !taf UKBB')
            else:
                taf = getmetar.extract_metar(apt, "taf")
                if taf:
                    await client.send_message(message.channel, '{0.author.mention} '.format(message) + "```" + taf + "```")
                else:
                    await client.send_message(message.channel,
                                              "{0.author.mention} TAF is not available for {1}".format(message,
                                                                                                       apt))

        if message.content.startswith('!metaf'):
            params = message.content.split(' ')
            apt = str(params[1]).upper()
            if len(params) != 2 or len(apt) != 4:
                await client.send_message(message.channel, 'Invalid using of !taf.\nExample: !metaf UKBB')
            else:
                metaf = getmetar.extract_metar(apt, "all")
                if metaf:
                    await client.send_message(message.channel, '{0.author.mention} '.format(message) + "```" + metaf + "```")
                else:
                    await client.send_message(message.channel,
                                              "{0.author.mention} TAF is not available for {1}".format(message,
                                                                                                       apt))

        if message.content == '!help':
            await client.send_message(message.channel, 'Commands accepted by bot: \n'
                                                       '!metar UKBB - provides METAR for airport\n'
                                                       '!taf UKBB - provides TAF for airport\n'
                                                       '!metaf UKBB - provides both METAR and TAF for airport\n'
                                                       '!reglist - gives registered users list (admin only)\n'
                                                       '!reg @Mention vatsimid - register user in db (admin only)\n')


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.send_message(client.get_channel(CNL_TEST), "I'm ready")


async def check_online():
    await client.wait_until_ready()
    i = 0
    while not client.is_closed:
        i += 1
        await client.send_message(client.get_channel(CNL_TEST), "Testing ASYNCIO " + str(i))
        await asyncio.sleep(2)


# client.loop.create_task(check_online())
client.run(I_AM_NIKKI)
