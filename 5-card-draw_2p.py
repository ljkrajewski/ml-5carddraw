import random
import pickle
from time import time
from datetime import datetime, timedelta
from os.path import exists

drawTablePath = "5card_table.pkl"
oddsTablePath = "5card_odds.pkl"
handSize = 5
debug = True

def pause():
  """Pauses the program and waits for user input."""
  input("==== Press <Enter> to continue...")

class deck:
  def __init__(self):
    self.deck = list(range(52))
    self.index = 0

  def shuffle(self):
    oldOrder = self.deck
    for i in range(3):
      newOrder = []
      while len(oldOrder) > 0:
        pick = oldOrder[random.randrange(0,len(oldOrder))]
        newOrder += [pick]
        oldOrder.remove(pick)
      oldOrder = newOrder
    cutLine = random.randrange(10,42)
    self.deck = oldOrder[cutLine:52] + oldOrder[0:cutLine]
    self.index = 0

  def dealCard(self):
    card = self.deck[self.index]
    self.index += 1
    if self.index > 52:
      exit("--- Oops, you're out of cards. Don't know how that happened. Program exiting. ---")
    return card

class hand:
  def __init__(self):
    self.hand = []

  def addCard(self,card):
    self.hand += [card]

  def delCard(self,card):
    self.hand.remove(card)

  def printCards(self):
    print("[ ",end="")
    rank = ['2','3','4','5','6','7','8','9','T','J','Q','K','A']  # c mod 13 (0-12)
    suit = ['S','H','C','D']  # c div 13 (0-3)
    for x in self.hand:
      r = x % 13
      s = x // 13
      print(rank[r]+suit[s]+" ",end="")
    print("]")

  def printCardsRaw(self):
    print("[ ",end="")
    for x in self.hand:
      print(str(x)+" ",end="")
    print("]")

class decisionTable:
  def __init__(self):
    self.movesTable = {}
    # Table = dictionary of 'hands' ({ hand1 : {dictionary of 'moves'}, hand2 : {dictionary of 'moves'}, ... })
    #      hand = str(list of [int])
    #      dictionary of 'moves' = { move1 [int] : moveValue1 [int], move2 [int] : moveValue2 [int], ...}
    self.epsilon = 1.0
    self.iterations = 0
    self.epsilonMultiplier = 0.99999999
    self.calculateds = 0
    self.randoms = 0

  class pickleTable:
    #only exists to create a pickle-friendly data format for saving & loading
    def __init__(self,table):
      self.movesTable = table.movesTable
      self.epsilon = table.epsilon
      self.iterations = table.iterations

  def addMove(self,result):
    tmp = result[0]
    tmp.sort()
    theHand = str(tmp)
    move = result[1]
    winner = result[2]
    if not theHand in self.movesTable:
      self.movesTable[theHand] = {}
    if move in self.movesTable[theHand]:
      self.movesTable[theHand][move] += winner
    else:
      self.movesTable[theHand][move] = winner
    self.epsilon = self.epsilon * self.epsilonMultiplier
    self.iterations += 1

  def makeRandomMove(self):
    global handSize

    self.randoms += 1
    return random.randint(0,(2**handSize)-1)

  def findCalculatedMove(self,thisHand):
    global handSize

    thisHand.sort()
    thisHandStr = str(thisHand)
    if thisHandStr in self.movesTable:
      movesDict = self.movesTable[str(thisHand)]
      ansList = [key for key, value in movesDict.items() if value == max(movesDict.values())]
      if len(ansList) == 1:
        ans = ansList[0]
      else:
        ans = ansList[random.randint(0,len(ansList)-1)]
        self.calculateds += 1
    else:
      ans = self.makeRandomMove()
    return ans

  def findMove(self,thisHand):
    if random.random() <= self.epsilon:
      if debug:
        print("Making random move...")
      answer = self.makeRandomMove()
    else:
      if debug:
        print("Making calculated move...")
      answer = self.findCalculatedMove(thisHand)
    return answer

  def saveTable(self,filename):
    pt = self.pickleTable(self)
    with open(filename, 'wb') as handle:
      pickle.dump(pt, handle)

  def loadTable(self,filename):
    with open(filename, 'rb') as handle:
      pt = pickle.load(handle)
    self.movesTable = pt.movesTable
    self.epsilon = pt.epsilon
    self.iterations = pt.iterations

class oddsTable:
  def __init__(self):
    self.handsTable = {}  ## Table = dictionary of 'odds'
    # Table = dictionary of 'hands' ({ hand1 : [list of integers], hand2 : [list of integers], ... })
    #      list[0] = number of times hand appears after draw
    #      list[1] = number of times hand appears after draw and leads to a win - number of times hand appears before draw and leads to a loss
    #      list[2] = number of times hand appears before draw
    #      list[3] = number of times hand appears before draw and leads to a win - number of times hand appears after draw and leads to a loss

  class pickleTable:
    #only exists to create a pickle-friendly data format for saving & loading
    def __init__(self,table):
      self.handsTable = table.handsTable

  def addKey(self,hand):
    if not (hand in self.handsTable.keys()):
      self.handsTable[hand] = [0, 0, 0, 0]
  
  def addWin(self,handBefore,handAfter):
    self.addKey(handBefore)
    self.handsTable[handBefore][2] += 1
    self.handsTable[handBefore][3] += 1
    self.addKey(handAfter)
    self.handsTable[handAfter][0] += 1
    self.handsTable[handAfter][1] += 1
    
  def addLoss(self,handBefore,handAfter):
    self.addKey(handBefore)
    self.handsTable[handBefore][2] += 1
    self.handsTable[handBefore][3] += -1
    self.addKey(handAfter)
    self.handsTable[handAfter][0] += 1
    self.handsTable[handAfter][1] += -1

  def addTie(self,handBefore,handAfter):
    self.addKey(handBefore)
    self.handsTable[handBefore][0] += 1
    self.addKey(handAfter)
    self.handsTable[handAfter][2] += 1

  def returnOdds(self,hand,BorA):
    numBorA = (ord(BorA.lower())-97)*2
    return 1.0 * self[hand][numBorA+1] / self[hand][numBorA]

  def saveTable(self,filename):
    pt = self.pickleTable(self)
    with open(filename, 'wb') as handle:
      pickle.dump(pt, handle)

  def loadTable(self,filename):
    with open(filename, 'rb') as handle:
      pt = pickle.load(handle)
      self.handsTable = pt.handsTable
    
#https://briancaffey.github.io/2018/01/02/checking-poker-hands-with-python.html
def rankCount(hand):
  ranks_counts = {}
  for r in [(v%13) for v in hand]:
    if r in ranks_counts:
      ranks_counts[r] += 1
    else:
      ranks_counts[r] = 1
  counts = sorted(ranks_counts.values(), reverse = True)
  ranks = sorted(ranks_counts, key=lambda k:(ranks_counts[k], k), reverse = True)
  return [counts, ranks]

def isStraight(hand):
  global handSize

  values = [(v%13) for v in hand]
  values.sort()
  #Check for low ace
  if (values[0] == 0) and (values[-1] == 12):
    values[-1] = -1
    values.sort()
  range = values[-1] - values[0]
  return (range == (handSize-1)) and (len(set(values)) == handSize)

def isFlush(hand):
  return len(set([(s//13) for s in hand])) == 1

def isStraightFlush(hand):
  return isStraight(hand) and isFlush(hand)

def is4ofKind(cardDigest):
  count = 0
  for x in cardDigest[0]:
    if x == 4:
      count += 1
  return count == 1

def is3ofKind(cardDigest):
  count = 0
  for x in cardDigest[0]:
    if x == 3:
      count += 1
  return count == 1

def is2Pair(cardDigest):
  count = 0
  for x in cardDigest[0]:
    if x == 2:
      count += 1
  return count == 2

def isPair(cardDigest):
  count = 0
  for x in cardDigest[0]:
    if x == 2:
      count += 1
  return count == 1

def isFullHouse(cardDigest):
  count2 = 0
  count3 = 0
  for x in cardDigest[0]:
    if x == 2:
      count2 += 1
    elif x == 3:
      count3 += 1
  return (count2 == 1) and (count3 == 1)

def handType(hand):
  #returns list of integers
  #[ rank_of_hand, most_significant_card, next_most_significant_card, ... ]
  cardDigest = rankCount(hand)
  if isStraightFlush(hand):
    ans = 9
  elif is4ofKind(cardDigest):
    ans = 8
  elif isFullHouse(cardDigest):
    ans = 7
  elif isFlush(hand):
    ans = 6
  elif isStraight(hand):
    ans = 5
  elif is3ofKind(cardDigest):
    ans = 4
  elif is2Pair(cardDigest):
    ans = 3
  elif isPair(cardDigest):
    ans = 2
  else: #high card
    ans = 1
  # low ace in straights/straight flushes
  cardsRanks = cardDigest[1]
  if (ans == 5) or (ans == 9):
    if (cardsRanks[0] == 12) and (cardsRanks[-1] == 0):
      cardsRanks[0] = -1
      cardsRanks.sort(reverse=True)
  return [ans] + cardsRanks

def compareHands(hand1,hand2):
  type1 = handType(hand1)
  if debug:
    print("hand 1 digest:  "+str(type1))
  type2 = handType(hand2)
  if debug:
    print("hand 2 digest:  "+str(type2))
  i = 0
  while (i < len(type1)) and (type1[i] == type2[i]):
    i += 1
  if i >= len(type1): #draw
    return 0
  elif type1[i] > type2[i]:
    return -1  #worse hand
  else:
    return 1  #better hand

### Card print routines ###
# hand = list of integers (cards) of unknown length

def printMove(move):
  global handSize

  print("[ ",end="")
  for i in range(handSize):
    if ((2 ** i) & move) > 0:
      print(str(i)+" ",end="")
  print("]")

####################################################

"""
def playOneGame():
  global handSize
  global debug

  myDeck = deck()
  myDeck.shuffle()
  handOne = hand()
  handTwo = hand()

  # Deal first hand
  for i in range(handSize):
    handOne.addCard(myDeck.dealCard())
  # Determine cards to drop
  move = myTable.findMove(handOne.hand)
  # Make second hand (drop cards from 1st hand, add cards to complete hand)
  for i in range(handSize):
    if (move & (2 ** i)) == 0:
      handTwo.addCard(handOne.hand[i])
  for i in range(handSize-len(handTwo.hand)):
    handTwo.addCard(myDeck.dealCard())

  if debug:
    print("\nHand 1:\t\t",end="")
    handOne.printCards()
    print("Hand 1 (raw):\t",end="")
    handOne.printCardsRaw()
    print("\nDropped cards:\t",end="")
    printMove(move)
    #print(str(move))
    print("\nHand 2:\t\t",end="")
    handTwo.printCards()
    print("Hand 2 (raw):\t",end="")
    handTwo.printCardsRaw()
    print("")
  result = compareHands(handOne.hand,handTwo.hand)
  return [handOne.hand, move, result]
"""

def drawNewCards(oldHand):
  global handSize
  global myDeck
  global debug
  global cardDrawTable

  move = cardDrawTable.findMove(oldHand.hand)
  if debug:
    print("Original hand: ",end="")
    oldHand.printCards()
  newHand = hand()
  # Make second hand (drop cards from 1st hand, add cards to complete hand)
  for i in range(handSize):
    if (move & (2 ** i)) == 0:
      newHand.addCard(oldHand.hand[i])
  for i in range(handSize-len(newHand.hand)):
    newHand.addCard(myDeck.dealCard())
  if debug:
    print("New hand: ",end="")
    newHand.printCards()
  return newHand


### main routine ###
print("Running...")

# load (or make new) tables
print("Loading draw table...")
cardDrawTable = decisionTable()
if exists(drawTablePath):
  cardDrawTable.loadTable(drawTablePath)
  print("Draw table loaded with "+str(cardDrawTable.iterations)+" iterations.")
  print("Start epsilon = "+str(cardDrawTable.epsilon))
else:
  print("New draw table created.")

print("Loading odds table...")
oddsDrawTable = oddsTable()
if exists(oddsTablePath):
  oddsDrawTable.loadTable(oddsTablePath)
  print("Odds table loaded.")
else:
  print("New odds table created.")

# play the game
print("Playing the game...")
myDeck = deck()
if debug:
  loopEnd=1
else:
  loopEnd=cardDrawTable.iterations
for i in range(cardDrawTable.iterations):
  myDeck.shuffle()
  playerOneBefore = hand()
  playerTwoBefore = hand()
  playerOneAfter = hand()
  playerTwoAfter = hand()
  # Deal cards for players 1 & 2
  if debug:
    print("Dealing orginal hands...")
  for i in range(handSize):
    playerOneBefore.addCard(myDeck.dealCard())
    playerTwoBefore.addCard(myDeck.dealCard())
  # Toss/draw cards for player 1
  if debug:
    print("Player 1 drawing cards...")
  playerOneAfter = drawNewCards(playerOneBefore)
  # Toss/draw cards for player 2
  if debug:
    print("Player 2 drawing cards...")
  playerTwoAfter = drawNewCards(playerTwoBefore)
  if debug:
    # Print hand 1
    print("Hand 1 after draw: ",end="")
    playerOneAfter.printCards()
    # Print hand 2
    print("Hand 2 after draw: ",end="")
    playerTwoAfter.printCards()
  # Declare winner and update odds table
  winner = compareHands(playerOneAfter.hand,playerTwoAfter.hand)
  if winner == -1:
    if debug:
      print("Player 1 wins.")
    oddsDrawTable.addWin(playerOneBefore,playerOneAfter)
    oddsDrawTable.addLoss(playerTwoBefore,playerTwoAfter)
  elif winner == 1:
    if debug:
      print("Player 2 wins.")
    oddsDrawTable.addLoss(playerOneBefore,playerOneAfter)
    oddsDrawTable.addWin(playerTwoBefore,playerTwoAfter)
  else:
    if debug:
      print("Tie.")
    oddsDrawTable.addTie(playerOneBefore,playerOneAfter)
    oddsDrawTable.addTie(playerTwoBefore,playerTwoAfter)
  # Print output (to make sure script is still running
  if debug:
    pause()
  else:
    if (i % 5000) == 0:
      print(".",end="")
    if (i % (5000*80)) == 0:
      print("")
oddsDrawTable.saveTable(oddsTablePath)
print("\n\nProgram ending.")
