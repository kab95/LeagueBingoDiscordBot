import discord
import asyncio
import BoardAssembler

from PIL import Image

NEW_GAME_INIT_TIME = 60

# Shamelessly stolen from stack overflow https://stackoverflow.com/questions/9647202/ordinal-numbers-replacement
ORDINAL = lambda n: "%d%s" % (n,"tsnrhtdd"[(n//10%10!=1)*(n%10<4)*n%10::4])

class Player:

    def __init__(self, author: discord.User):
        self.player = author
        self.board, self.squares = BoardAssembler.AssembleBoard()
        self.markedIndexes = []
        self.boardFileName = ""
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
            return BoardAssembler.checkIfWon(self.markedIndexes)

    def getTransmissibleFile(self):
        return discord.File(self.boardFileName)

class Game:
    initializingGame = False
    players = []
    wonPlayers = []
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
        await self.gameChannel.send('The game has begun!')

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

    async def gameWon(self, player: Player):
        await self.gameChannel.send(file=player.getTransmissibleFile())
        await self.gameChannel.send(f'{player.player.display_name} has completed a board!')
        self.wonPlayers.append(player)
        await self.gameChannel.send(f'{player.player.display_name} was the {ORDINAL(len(self.wonPlayers))} winner!')

    async def markSquares(self, category: str):
        if not self.players:
            return

        referenceSquares = self.players[0].squares
        for square in referenceSquares:
            if category in square.keyWords:
                await self.gameChannel.send(f'Marking off category: \"{square.displayName}\" for all players')
                for player in self.players:
                    if player.markCategory(square.displayName) and player not in self.wonPlayers:
                        await self.gameWon(player)
                break
        else:
            await self.gameChannel.send(f'I was unable to find a category with this particular key-word: {category}')

    async def endGame(self, player: discord.User):
        await self.gameChannel.send(f"Ending the game. Ending call was made by {player.display_name}")

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

    if message.content.startswith('!EndGame'):
        await currentGame.endGame(message.author)
        currentGame = None

    if message.content.startswith('!help'):
        await message.channel.send(
            "!NewGame starts a new round of bingo.\n"
            f"New players can join a game with !join for {NEW_GAME_INIT_TIME} seconds after !NewGame has been called\n"
            "Categories experienced can be marked with '!b <key-word>' for example '!b wrong' for  Wrong Runes\n"
            "The players can get a peek at the state of their current board with !GameState\n"
            "The game can be ended with !EndGame")

    if currentGame.isInitializing():
        return

    if message.content.startswith('!GameState'):
        await currentGame.showGameState()

    if message.content.startswith('!b'):
        await currentGame.markSquares(message.content.lstrip("!b").strip(" ").lower())

client.run('')
