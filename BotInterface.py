import discord
import asyncio

class Player:

    def __init__(self, author):
        self.username = author

    def __eq__(self, other):
        self.username == other

NEW_GAME_INIT_TIME = 60
players = []

client = discord.Client()
gameChannel = None
initializingGame = False

async def startNewGame(channel: discord.TextChannel):
    global players
    players = []
    global gameChannel
    gameChannel = channel

    global initializingGame
    initializingGame = True
    for i in range(NEW_GAME_INIT_TIME):
        if i % 10 == 0:
            await gameChannel.send(f'{NEW_GAME_INIT_TIME - i} seconds left before the game starts!')
        await asyncio.sleep(1)

    initializingGame = False

async def addPlayer(author: discord.User):
    if (author in players):
        return

    players.append(Player(author))
    await gameChannel.send(f'{author.display_name} has joined the game!')

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    cs = message.channel
    if message.content.startswith('!NewGame'):
        await startNewGame(message.channel)

    if initializingGame and message.content.startswith('!Join'):
        await addPlayer(message.author)


client.run('OTEzMDM2MTc0NDY0MDA4MjYy.YZ4pMw.Q2E6xHcEHJenUP1gTVBTKXvhVvY')
