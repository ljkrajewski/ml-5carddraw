# === poker module ===
# To use: from poker.py import *

handSize = 5

# =======================================================================
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
# =======================================================================
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
# =======================================================================
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
# =======================================================================
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
    strHand = str(hand)
    if not (strHand in self.handsTable.keys()):
      self.handsTable[strHand] = [0, 0, 0, 0]
  
  def addWin(self,handBefore,handAfter):
    strHandBefore = str(handBefore)
    self.addKey(strHandBefore)
    self.handsTable[strHandBefore][2] += 1
    self.handsTable[strHandBefore][3] += 1
    strHandAfter = str(handAfter)
    self.addKey(strHandAfter)
    self.handsTable[strHandAfter][0] += 1
    self.handsTable[strHandAfter][1] += 1
    
  def addLoss(self,handBefore,handAfter):
    strHandBefore = str(handBefore)
    self.addKey(strHandBefore)
    self.handsTable[strHandBefore][2] += 1
    self.handsTable[strHandBefore][3] += -1
    strHandAfter = str(handAfter)
    self.addKey(strHandAfter)
    self.handsTable[strHandAfter][0] += 1
    self.handsTable[strHandAfter][1] += -1

  def addTie(self,handBefore,handAfter):
    strHandBefore = str(handBefore)
    self.addKey(strHandBefore)
    self.handsTable[strHandBefore][0] += 1
    strHandAfter = str(handAfter)
    self.addKey(strHandAfter)
    self.handsTable[strHandAfter][2] += 1

  def returnOdds(self,hand,BorA):
    numBorA = (ord(BorA.lower())-97)*2
    strHand = str(hand)
    handExists = strHand in self.handsTable.keys()
    if debug:
      print("\ntype(hand) = "+str(type(hand)))
      print("numBorA = "+str(numBorA))
      if handExists:
        print("self.handsTable["+strHand+"] = "+str(self.handsTable[strHand]))
        print("self.handsTable["+strHand+"]["+str(numBorA)+"] = "+str(self.handsTable[strHand][numBorA]))
        print("self.handsTable["+strHand+"]["+str(numBorA+1)+"] = "+str(self.handsTable[strHand][numBorA+1]))
      else:
        print(strHand+" not in odds table.")
    if handExists:
      answer = 1.0 * self.handsTable[strHand][numBorA+1] / self.handsTable[strHand][numBorA]
    else:
      answer = -10000000
    return answer

  def saveTable(self,filename):
    pt = self.pickleTable(self)
    with open(filename, 'wb') as handle:
      pickle.dump(pt, handle)

  def loadTable(self,filename):
    with open(filename, 'rb') as handle:
      pt = pickle.load(handle)
      self.handsTable = pt.handsTable
# =======================================================================
