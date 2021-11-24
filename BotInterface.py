import discord
import asyncio
import BoardAssembler

from PIL import Image

NEW_GAME_INIT_TIME = 60

class Player:
    markedIndexes = []

    def __init__(self, author: discord.User):
        self.player = author
        self.board, self.squares = BoardAssembler.AssembleBoard()
        self.save()

    def __eq__(self, other):
        return self.player == other

    def save(self):
        self.boardFileName = f"{self.player.display_name}.png"
        self.board.save(self.boardFileName)

    def markCategory(self, displayName):
        for i in range(len(self.squares)):
            if displayName != self.squares[i].displayName:
                continue
            markedIndex = BoardAssembler.listIndexToGridIndex(i)
            self.markedIndexes.append(markedIndex)
            BoardAssembler.MarkSquare(markedIndex, self.board)
            self.save()
            return

    def getTransmissibleFile(self):
        return discord.File(self.boardFileName)

class Game:
    initializingGame = False
    players = []
    gameChannel = None

    async def startNewGame(self, channel: discord.TextChannel):
        self.players = []
        self.gameChannel = channel
        self.initializingGame = True
        for i in range(NEW_GAME_INIT_TIME):
            if i % 10 == 0:
                await self.gameChannel.send(f'{NEW_GAME_INIT_TIME - i} seconds left before the game starts!')
            await asyncio.sleep(1)

        self.initializingGame = False

    async def addPlayer(self, author: discord.User):
        if (author in self.players):
            return

        newPlayer = Player(author)
        self.players.append(newPlayer)
        await self.gameChannel.send(f'{author.display_name} has joined the game!')
        await newPlayer.player.send(file=newPlayer.getTransmissibleFile())

    async def showGameState(self):
        for player in self.players:
            await player.player.send(file=player.getTransmissibleFile())
        await self.gameChannel.send('Sent updated board to all available participants')

    async def markSquares(self, category: str):
        if not self.players:
            return

        referenceSquares = self.players[0].squares
        for square in referenceSquares:
            if category in square.keyWords:
                await self.gameChannel.send(f'Marking off category: \"{square.displayName}\" for all players')
                for player in self.players:
                    player.markCategory(square.displayName)
                break
        else:
            await self.gameChannel.send(f'I was unable to find a category with this particular key-word: {category}')

    def isInitializing(self):
        return self.initializingGame

client = discord.Client()
currentGame = None

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    global currentGame
    if message.content.startswith('!NewGame'):
        currentGame = Game()
        await currentGame.startNewGame(message.channel)
        return

    if not currentGame:
        return

    if currentGame.isInitializing() and message.content.startswith('!Join'):
        await currentGame.addPlayer(message.author)

    if message.content.startswith('!GameState'):
        await currentGame.showGameState()

    if message.content.startswith('!b'):
        await currentGame.markSquares(message.content.lstrip("!b").strip(" ").lower())


client.run('')
