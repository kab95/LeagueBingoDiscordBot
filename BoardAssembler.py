import PIL.Image as Image
import PIL.ImageDraw as Draw
import PIL.ImageColor as Color
import PIL.ImageFont as Font
import random
from typing import Final, List, Tuple
from dataclasses import dataclass

SQUARE_DATA_LIST = [('My mind is telling me no...', 'Åpenbar fristelse som går dårlig.'),
('No Control Wards', 'Du/noen på laget har ikke kjøpt control wards.'),
('Wierd Sum. Names', 'SpaceFart; HecarimDidNothingWrong; AverageAhriAhegaoEnjoyer'),
('Spam ? Ping', 'Spam av missing pings.'),
('FF 15 vote', 'FF 15 vote.'),
('Polar-Opposites', 'Ha en teamfight hvor alle går hver sin vei.'),
('"Flash er flash"', 'Du får noen sin flash for veldig lite investering.'),
('Fail Flash/Ult', 'Du bommer på en lang cooldown.'),
('Sharing is NOT caring', 'Brand ult blir delt som corona på en grottefest.'),
('BUT MAH BODEY!', 'Åpenbar fristelse som går bra.'),
('Its gRRReat!', 'Få minst 3 ults på deg i løpet av en teamfight.'),
('"Bææ-ron"', 'Tvilsomme baron-calls.'),
('Pyke Ban', 'Morten skal spille Tristana.'),
('Wrong Runes', 'Morten skal spille/har spilt Tristana.'),
('Bait a Teammate', 'Få noen til å engage; uten at det var med hensikt.'),
('Worlds Build/Champ', 'Noen som drar from noe fra Worlds; uten å skjønne hvorfor det er bra.'),
('Calculated', 'Overlev med under 30 hp.'),
('Too Cool-Prom. School', 'Dodge en skillshot.'),
('Skjegget i postkassen', 'Drep noen/bli drept av primært tårn/annet.'),
('"God tid"', 'Ihvertfall 4 sekunder til gode.'),
('"Ill take it"', 'Du fikk en fordel; fordi motstanderen tullet det til.'),
('The Root of the Prob.', 'Bli CCet for 3 sekunder (eller mer) i en fight.'),
('Goblin', '2000 gold (eller mer) før en back.'),
('Trynd. playing Trynd.', 'Noen queuet for X; som aldri har planer om å forlate X.'),
('"All me"', 'Fikk et objective/kill ved mager deltagelse.')]

@dataclass
class SquareData:
    DisplayName: str
    Description: str

    def GenerateKeyWords(self):
        self.KeyWords = self.DisplayName.split(" ")


BASE_SQUARE_SIZE: Final = (120, 80)
BASE_GRID_SIZE: Final = (5, 5)
BASE_BORDER_WIDTH: Final = 5
BASE_MARKER_WIDTH: Final = 3
BASE_BORDER_COLOR: Final = Color.getrgb("black")
BASE_MARKER_COLOR: Final = Color.getrgb("red")
BASE_TEXT_COLOR: Final = Color.getrgb("black")
BASE_TEXT_FONT: Final = Font.truetype("arial.ttf", 15)
BASE_TEXT_OFFSET: Final = (10, 20)
BASE_BOARD_SIZE: Final = (
    BASE_SQUARE_SIZE[0] * BASE_GRID_SIZE[0] + (BASE_GRID_SIZE[0] + 1) * BASE_BORDER_WIDTH,
    BASE_SQUARE_SIZE[1] * BASE_GRID_SIZE[1] + (BASE_GRID_SIZE[1] + 1) * BASE_BORDER_WIDTH)

def AssembleBoard():
    board = Image.new('RGB', BASE_BOARD_SIZE, Color.getrgb("cyan"))
    drawingBoard = Draw.Draw(board)
    widthDrawMarker = BASE_BORDER_WIDTH // 2   # Prevents first half of border from being drawn out of frame
    while widthDrawMarker < board.width:
        drawingBoard.line([(widthDrawMarker, 0), (widthDrawMarker, board.height)], BASE_BORDER_COLOR, BASE_BORDER_WIDTH)
        widthDrawMarker += BASE_SQUARE_SIZE[0] + BASE_BORDER_WIDTH
    heightDrawMarker = BASE_BORDER_WIDTH // 2   # Prevents first half of border from being drawn out of frame
    while heightDrawMarker < board.height:
        drawingBoard.line([(0, heightDrawMarker), (board.width, heightDrawMarker)], BASE_BORDER_COLOR, BASE_BORDER_WIDTH)
        heightDrawMarker += BASE_SQUARE_SIZE[1] + BASE_BORDER_WIDTH

    squareDataList = PopulateDataList()
    random.shuffle(squareDataList)
    drawSquareValues(squareDataList, drawingBoard)

    return board


def PopulateDataList():
    squareDataList = []
    for square in SQUARE_DATA_LIST:
        data = SquareData(square[0], square[1])
        data.GenerateKeyWords()
        squareDataList.append(data)
    return squareDataList


def drawSquareValues(squareDataList: List[SquareData], drawingBoard: Draw):
    totalSquares: Final = BASE_GRID_SIZE[0] * BASE_GRID_SIZE[1]
    squaresToDraw = squareDataList[:totalSquares]
    for i in range(totalSquares):
        index = (i % BASE_GRID_SIZE[0], i // BASE_GRID_SIZE[0])
        coords = indexToCoordinates(index, BASE_TEXT_OFFSET)
        curData = squaresToDraw.pop(0)
        displayText = makeTextMultiline(curData.DisplayName, drawingBoard)
        drawingBoard.multiline_text(coords, displayText, BASE_TEXT_COLOR, BASE_TEXT_FONT)
        print(f"{index}, {coords}")


def makeTextMultiline(text: str, drawingBoard: Draw.ImageDraw):
    textBounds = BASE_SQUARE_SIZE[0] - 2 * BASE_TEXT_OFFSET[0]
    print(drawingBoard.textsize(text, BASE_TEXT_FONT)[0])
    if drawingBoard.textsize(text, BASE_TEXT_FONT)[0] < textBounds:
        return text

    splitText = text.split(" ")
    for i in range(len(splitText)):
        segmentWidth = drawingBoard.textsize(" ".join(splitText[:i+1]), BASE_TEXT_FONT)[0]
        if segmentWidth > textBounds:
            splitText[i] = "\n" + splitText[i]
        textWidth = drawingBoard.textsize(" ".join(splitText), BASE_TEXT_FONT)[0]
        if textWidth < textBounds:
            break
    outText = " ".join(splitText)
    return outText.replace(" \n", "\n")


def indexToCoordinates(index, offset=(0, 0)):
    return (index[0] * BASE_SQUARE_SIZE[0] + (index[0] + 1) * BASE_BORDER_WIDTH + offset[0],
            index[1] * BASE_SQUARE_SIZE[1] + (index[1] + 1) * BASE_BORDER_WIDTH + offset[1])


def MarkSquare(index, drawingBoard):
    squareOrigin = indexToCoordinates(index)
    squareBounds = (squareOrigin[0] + BASE_SQUARE_SIZE[0], squareOrigin[1] + BASE_SQUARE_SIZE[1])
    drawingBoard.ellipse([squareOrigin, squareBounds], None, BASE_MARKER_COLOR, BASE_MARKER_WIDTH)


if __name__ == '__main__':
    print('Testing board assembler...')
    board = AssembleBoard()
    drawingBoard = Draw.Draw(board)
    MarkSquare((1, 1), drawingBoard)
    MarkSquare((3, 4), drawingBoard)
    board.show()
