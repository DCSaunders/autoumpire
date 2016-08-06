#!/usr/bin/env python
import csv
import operator
import os.path
from Player import Player

NAME_MARKER, KILLS = '"', 'KILLS'

# Enum for columns of playerlist containing relevant info
# If changing playerlist layout, be sure to edit this enum.
class Field(object):
    name = 0
    pseud = 1
    college = 2
    address = 3
    water = 4
    notes = 5
    email = 6
    

# Initialises playerlist and newsfile
# p: player dictionary.
# playerFile: csv file containing playerlist.
# newsFile: text file to output report templates
# startID: anchor ID used for unique HTML links
# index_attr: attribute to index playerlist. Default set to be name
def initialiseGame(p, playerFile, newsFile, startID, index_attr):
    initialiseNews(newsFile, startID)
    with open(playerFile, 'rb') as f:
        reader = csv.reader(f)
        reader.next()
           
        for row in reader:
            player = Player(row[Field.name],row[Field.pseud],row[Field.college], \
                            row[Field.address],row[Field.water],row[Field.notes], \
                            row[Field.email], newsFile)
            # Assign player dictionary, indexing by attribute defined in main
            p[getattr(player, index_attr)] = player

class GameRunner(object):
    
    def __init__(self, p, index_attr, gameFile):
        self.gameFile = gameFile
        self.players = p
        self.index_attr = index_attr
        self.current_char = ''
        self.current_token = ''
        self.text = ''
        self.index = 0

    def skipWhitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
        
    def advance(self):
        self.index += 1
        if self.index > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.index]
        
    def getPlayerName(self):
        self.advance()
        name = ''
        while self.current_char is not NAME_MARKER:
            name += self.current_char
            self.advance()
        self.advance()
        self.current_token = name

    def getKeyword(self):
        while self.current_char.isalpha():
            if self.text[self.index:self.index+len(KILLS)] == KILLS:
                self.current_token = KILLS
                self.index += len(KILLS)
                self.current_char = self.text[self.index]
    
    # Runs the game start to finish.
    # NB Example function indexes using name
    # p: player dictionary
    # index_attr: attribute to index playerlist. Default set to be name
    # gameFile: text file for running game
    def runGame(self):
        with open(self.gameFile, 'r') as f:
            for line in f:
                self.index = 0
                self.text = line
                self.current_char = self.text[self.index]
                while self.current_char is not None:
                    if self.current_char == NAME_MARKER:
                        self.getPlayerName()
                        print self.current_token
                    elif self.current_char.isspace():
                        self.skipWhitespace()
                    elif self.current_char.isalpha():
                        self.getKeyword()
                        print self.current_token

        
        self.players["Player1"].killed(self.players["Player3"], "00:00")
        self.players["Player2"].killed(self.players["Player1"], "11:00")
        self.players["Player2"].killed(self.players["Player1"], "15:20")
        self.players["Player2"].killed(self.players["Player1"], "19:25")
        self.players["Player2"].killed(self.players["Player1"], "08:20")
        self.players["Player3"].bonus(17)
        self.players["Player2"].killed(self.players["Player1"], "10:00")
        startReporting(p) 


# Score the playerlist
# p: player dictionary
def score(p):
    for player in p.itervalues():
        player.calcPoints()

        
# Enable addition of new report templates
# p: player dictionary
def startReporting(p):
    for player in p.itervalues():
        player.startReporting()


# Sets up news file with anchor for unique HTML links
# newsFile: output file.
# startID: ID for unique HTML links
def initialiseNews(newsFile, startID):
    if (os.path.isfile(newsFile) == False):
        with open(newsFile, 'w') as f:
            f.write(startID)
    else:
        print 'News file already initialised'


# Output plaintext scores
# p: sorted player dictionary
# scoreFile: file to output plaintext scores
def plaintextScores(pList, scoreFile):
    with open(scoreFile, 'w') as f:
        for player in pList:
            pointStr = (player.name, str(player.points), "\n")
            pointStr = " ".join(pointStr)
            print pointStr
            f.write(pointStr)


# Output scores in HTML table
# p: sorted player dictionary.
# scoreFile: file for output.
def htmlScores(pList, scoreFile):
    t_s = "<table>"
    t_e = "</table>"
    row_s = "<tr>"
    row_e = "</tr>"
    entry_s = "<td>"
    entry_e = "</td>"
    nl = "\n"

    with open(scoreFile, 'w') as f:
        # Write scores in table
        f.write(t_s)

        for player in pList:
            pointStr = (player.name, player.pseudonym,
                        player.address, player.college,
                        player.waterStatus, player.notes,
                        str(player.kills), str(player.deaths),
                        '%.2f' % player.points)
            pointStr ="{}{}".format(entry_e, entry_s).join(pointStr)
            f.write("{}{}{}{}{}{}".format(row_s, entry_s, pointStr, entry_e, row_e, nl))
        f.write(t_e)


# Output scores in HTML table or plaintext
# p: player dictionary.
# k: key to sort on.
# html: false if plaintext output, true if html table
# desc: false if ascending, true if descending.
def outputScores(p, html, k, desc):
    pList = sorted(p.values(), key=operator.attrgetter(k), reverse = desc)
    oType = "html" if html else "plaintext"
    fileName = "scores-{}-{}.txt".format(k, oType)

    if (html):
        htmlScores(pList, fileName)
    else:
        plaintextScores(pList, fileName)


# Set up filenames, run game
if __name__ == '__main__':
    newsFile = "news.txt" # Text file the news will be written to.
    gameFile = "game.txt" # text file for game input
    startID = "e16000" # Anchor for first entry in news file
    playerFile = "MWAUexampleplayers.csv"
    index_attr = 'name' # Change to e.g. 'email', 'pseudonym' or other unique attr of Player class if want
    
    p = dict() # Player dictionary
    initialiseGame(p, playerFile, newsFile, startID, index_attr)
    gameRunner = GameRunner(p, index_attr, gameFile)
    gameRunner.runGame()
    p = gameRunner.players
    score(p)
    # outputScore(p=playerdict, html=True/False, k=attribute-to-sort-by, desc=True/False)
    outputScores(p, False, 'points', True) # simple plaintext scores in point order
    outputScores(p, True, 'points', True) # html scores in point order
    outputScores(p, True, 'college', False) # html scores in college order
    outputScores(p, True, 'name', False) # html scores in name order
    outputScores(p, True, 'kills', True) # simple plaintext scores in kills order

