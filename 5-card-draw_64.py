import random
import pickle
from time import time
from datetime import datetime, timedelta
from os.path import exists

tablePath = "5card_table.pkl"
handSize = 5
debug = False

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
    self.epsilonMultiplier = 0.9999999999
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
    if random.random() <= myTable.epsilon:
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

### main routine ###
print("Running...")

# load (or make new) table
print("Loading table...")
myTable = decisionTable()
if exists(tablePath):
  myTable.loadTable(tablePath)
  print("Table loaded with "+str(myTable.iterations)+" iterations.")
  print("Start epsilon = "+str(myTable.epsilon))
else:
  print("New table created.")

# play the game
print("Playing the game...")
percentWins = 0.0
percentLosses = 100.0
while ((percentWins -gt 65.0) and (percentLosses -lt 15.0)):
  numIterations = 500000
  myDeck = deck()
  wins = 0
  losses = 0
  draws = 0
  debug = False
  start = time()
  print("Start time:\t"+str(datetime.fromtimestamp(start)))
  for i in range(numIterations):
    ans = playOneGame()
    if ans[2] == 1:
      wins += 1
    elif ans[2] == -1:
      losses += 1
    else:
      draws += 1
    myTable.addMove(ans)
  end = time()
  
  percentWins = (100.0*wins/numIterations)
  percentLosses = (100.0*losses/numIterations)
  percentDraws = (100.0*draws/numIterations)
  print("End time:\t"+str(datetime.fromtimestamp(end)))
  print("Time to run:\t"+str(timedelta(seconds=(end-start))))
  print("\nEpsilon:\t"+str(myTable.epsilon))
  print("Iterations:\t"+str(myTable.iterations))
  print("\nRandoms:\t"+str(myTable.randoms))
  print("Calculateds:\t"+str(myTable.calculateds))
  print("Wins:\t"+str(wins),end="")
  print(" (%5.2f%%)" % percentWins)
  print("Losses:\t"+str(losses),end="")
  print(" (%5.2f%%)" % percentLosses)
  print("Draws:\t"+str(draws),end="")
  print(" (%5.2f%%)" % percentDraws)
  print("==============================================")
  
  # save updated move table w/ new info
  myTable.saveTable(tablePath)

print("\n\nExit condition met. Program ending.")
