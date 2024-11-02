# -*- coding: utf-8 -*-
"""
Created on 17.02.2023

@author: DarkMatter1

"""
import discord
import io
import os
import glob
from PIL import Image
from MapInitialiser import Map_Initialiser, formatText
from MapRunner import Map_Runner

async def send_message(message, is_private, response):
    await message.author.send(response) if is_private else await message.channel.send(response)


async def send_image_message(image, message, isPrivate):
    """
    Sends an image as a file attachment in a Discord message.
    :param image: The image to send.
    :param message: The message(channel) to send the image in.
    """
    # convert image data to bytes-like object
    with io.BytesIO() as image_bytes:
        image.save(image_bytes, format='PNG')
        image_bytes.seek(0)
        # create a discord.File object from the image bytes
        image_file = discord.File(fp=image_bytes, filename='image.png')
        # check if file size is small enough
        try:
            if isPrivate:
                await message.author.send(file=image_file)
            else:
                await message.channel.send(file=image_file)
        except:
            await send_message(message, isPrivate, f'`Too big - Use a smaller image`')


def run_discord_bot():
    # default stuff
    TOKEN = 'MTA3NjI2MDE0MDM4MDA4MjE3OQ.Gc1p--.h_T7hq9e-QgBGLGjngEgj9pScciy4GBHTbJWFQ'#ADD TOKEN HERE
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    # activation confirmation
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    active_game = False
    active_round = False
    commands = []
    round_number = 0
    game_name = "BattleMap"
    active_channel = ""

    folders_to_create = [
        'Resources',
        'Resources/Standards',
        'creation',
        'creation/maps',
        'creation/maps/debug',
        'creation/data'
    ]
    for folder in folders_to_create:
        if not os.path.exists(folder):
            os.makedirs(folder)

    # message listening
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        if user_message.startswith('!#'):
            user_message = '!' + user_message[2:]
            isPrivate = True
        elif user_message.startswith('!'):
            isPrivate = False

        bot_commander_role = discord.utils.get(message.guild.roles, name="High Captain")
        if bot_commander_role in message.author.roles:
            Commanders = True
        else:
            Commanders = False

        nonlocal active_game
        nonlocal active_round
        nonlocal commands
        nonlocal round_number
        nonlocal game_name
        nonlocal active_channel
        # debug
        print(f'{username} said: "{user_message}" ({channel})')

        if user_message.startswith('!generate'):
            if not Commanders:
                await send_message(message, isPrivate, '`You are not allowed to generate maps`')
                return
            game_name = user_message[10:]
            attachment = message.attachments[0] if len(message.attachments) == 1 else None
            try:
                if attachment:
                    Excel = io.BytesIO(await attachment.read())
                    await send_message(message, isPrivate, '`Creating...`')
                    image = Map_Initialiser(Excel, game_name)
                else:
                    image = Image.open(f'creation/maps/{game_name}0.png').convert('RGBA')
                await send_image_message(image, message, isPrivate)
            except:
                file_list = [os.path.splitext(os.path.basename(file))[0][:-1] for file in
                             glob.glob(os.path.join(r"creation\maps", "*0.png"))]
                await send_message(message, isPrivate,
                                   f'`Error: Please attach the correct Excel file or name one of the following maps: {file_list}`')

        elif user_message.startswith('!startgame') and not active_game:
            active_channel = str(message.channel)
            isPrivate = False
            active_game = True
            labels = user_message.endswith('labels')
            game_name = user_message[11:-7] if labels else user_message[11:]
            try:
                image = Image.open(f'creation/maps/{game_name}0.png').convert('RGBA')
                await send_message(message, isPrivate, '`Game started! This will be your map:`')
                await send_image_message(image, message, isPrivate)
                if labels:
                    labelled = Image.open(f'creation/maps/debug/{game_name}_debug.png').convert('RGBA')
                    await send_image_message(labelled, message, isPrivate)
            except:
                active_game = False
                file_list = [os.path.splitext(os.path.basename(file))[0][:-1] for file in
                             glob.glob(os.path.join(r"creation\maps", "*0.png"))]
                await send_message(message, isPrivate,
                                   f'`Please specify your desired map. Available maps are: {file_list}`')

        elif user_message.startswith('!continuegame'):
            active_channel = str(message.channel)
            active_game = True
            isPrivate = False
            game_name = message.content[14:]
            try:
                # Find the next available attachment number for the short filename
                round_number = 0
                for f in os.listdir('creation/maps'):
                    if f.startswith(game_name):
                        round_number += 1
                image = Image.open(f'creation/maps/{game_name}{round_number-1}.png').convert('RGBA')
                await send_message(message, isPrivate, f'`Game continues in round {round_number}! This will be your map:`')
                await send_image_message(image, message, isPrivate)
                round_number -= 1
            except:
                active_game = False
                file_list = [os.path.splitext(os.path.basename(file))[0][:-1] for file in
                             glob.glob(os.path.join(r"creation\maps", "*0.png"))]
                await send_message(message, isPrivate,
                                   f'`Please specify your desired map. Available maps are: {file_list}`')

        elif user_message == '!stopgame' and active_game:
            isPrivate = False
            round_number = 0
            active_game = False

            # Delete everything inside creation/data
            data_folder = "creation/data"
            for filename in os.listdir(data_folder):
                try:
                    os.remove(os.path.join(data_folder, filename))
                except Exception as e:
                    print(f"Failed to delete {os.path.join(data_folder, filename)}. Reason: {e}")

            # Delete images in creation/maps that do not end with 0.png
            maps_folder = "creation/maps"
            for filename in os.listdir(maps_folder):
                if not filename.endswith("0.png"):
                    try:
                        os.remove(os.path.join(maps_folder, filename))
                    except Exception as e:
                        print(f"Failed to delete {os.path.join(maps_folder, filename)}. Reason: {e}")

            await send_message(message, isPrivate, '`Game ended!`')

        elif user_message == '!round' and active_game:
            isPrivate = False
            if not active_round:
                round_number += 1
                active_round = True
                commands = ["del,x", "add,u,x,-1,-1"]
                await send_message(message, isPrivate, f'`Round {round_number} started! Enter your commands:`')
            else:
                await send_message(message, isPrivate, '`There is already an active round in progress!`')

        elif user_message == '!finish' and active_game:
            isPrivate = False
            if active_round:
                active_round = False
                filename = 'creation/data/commands.txt'
                with open(filename, 'w') as file:
                    commands = formatText(commands)
                    file.write(commands)
                await send_message(message, isPrivate, f'`Round {round_number} movement ended! Battle Map is being updated...`')
                image = Map_Runner(round_number, game_name)
                await send_image_message(image, message, isPrivate)
            else:
                await send_message(message, isPrivate, '`There is no active round in progress!`')

        elif active_round:
            if active_channel == str(message.channel):
                commands.append(message.content + '\n')

        elif user_message.startswith('!resources'):
            if not Commanders:
                await send_message(message, isPrivate, '`You are not allowed to access the resources`')
                return
            attachment = message.attachments[0] if len(message.attachments) == 1 else None
            if attachment:
                # Check if attachment is a .png image
                if attachment.filename.lower().endswith('.png'):
                    image_bytes = await attachment.read()
                    # Save the image to the Resources folder
                    filename = message.content[11:]

                    # Shorten the filename to 2 letters
                    short_filename = filename[:2].lower()

                    # Find the next available attachment number for the short filename
                    attachment_number = 0
                    for f in os.listdir('Resources'):
                        if f.startswith(short_filename):
                            attachment_number += 1

                    # Construct the attachment filename with the short filename and attachment number
                    attachment_filename = short_filename + '_' + str(attachment_number)

                    # Save the attachment to the Resources folder
                    with open('Resources/' + attachment_filename + ".png", 'wb') as f:
                        f.write(image_bytes)
                else:
                    await send_message(message, isPrivate, '`Can only accept .png images`')
            else:
                if message.content.endswith('showall'):
                    for file in glob.glob(os.path.join(r"Resources", "*.png")):
                        resource = Image.open(file).convert('RGBA')
                        await send_message(message, isPrivate, file + ":")
                        await send_image_message(resource, message, isPrivate)
                elif len(user_message) == 10:
                    file_list = [os.path.splitext(os.path.basename(file))[0] for file in
                                 glob.glob(os.path.join(r"Resources", "*.png"))]
                    await send_message(message, isPrivate, f'`{file_list}`')
                else:
                    file = user_message[11:]
                    resource = Image.open(r"Resources/" + file + ".png").convert('RGBA')
                    await send_message(message, isPrivate, file + ".png:")
                    await send_image_message(resource, message, isPrivate)

        elif user_message.startswith('!help'):
            command = user_message.split(' ')[1] if len(user_message.split(' ')) > 1 else ''
            if command == '':
                # User just typed "!help"
                await send_message(message, isPrivate,
                                   '`All:\n!help {docu}{param}\n!startgame [name]\n!round\n!finish\n!stopgame\n\n'
                                   'Commanders only:\n!generate [name] {labels} + Excel attachment\n!resources {[name]} {showall}\n!resources [name] + .png attachment\n\n'
                                   '! for public messages\n!# for private messages\n[_] is required, but variable\n{_} is optional`')
            elif command == 'docu':
                # User typed "!help docu"
                with open('Resources/Standards/Documentation.txt', 'rb') as f:
                    if isPrivate:
                        await message.author.send(file=discord.File(f))
                    else:
                        await message.channel.send(file=discord.File(f))
            elif command == 'param':
                # User typed "!help param"
                with open('Resources/Standards/Parameters.xlsx', 'rb') as f:
                    if isPrivate:
                        await message.author.send(file=discord.File(f))
                    else:
                        await message.channel.send(file=discord.File(f))

        else:
            return

    client.run(TOKEN)
