#!/usr/bin/env python
import csv
import operator
import os.path
from Player import Player

NAME, NAME_MARKER, KILLS, BONUS, TIME, TIME_FORMAT = 'NAME', '"', 'KILLS', 'BONUS', 'TIME', 'hh:mm'

class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self):
        """String representation of the class instance.
        """
        return 'Token({type}, {value})'.format(
            type=self.type,
            value=repr(self.value)
        )

    def __repr__(self):
        return self.__str__()


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

class Lexer(object):    
    def __init__(self, text):
        self.text = text
        self.index = 0
        self.current_char = self.text[self.index]
    
    def skipWhitespace(self):
        while self.current_char is not None and self.current_char.isspace():
            self.advance()
        
    def advance(self, steps=1):
        self.index += steps
        if self.index > len(self.text) - 1:
            self.current_char = None
        else:
            self.current_char = self.text[self.index]
        
    def get_player_name(self):
        self.advance()
        name = ''
        while self.current_char is not NAME_MARKER:
            name += self.current_char
            self.advance()
        self.advance()
        return name

    def get_time(self):
        self.advance()
        time_end = self.index + len(TIME_FORMAT)
        self.advance(len(TIME_FORMAT))
        return self.text[self.index:time_end]

    def get_bonus(self):
        self.advance()
        bonus = ''
        while self.current_char.isdigit():
            bonus += self.current_char
            self.advance()
        return int(bonus)

    def eat(self, keyword):
        eaten = False
        if self.text[self.index:self.index+len(keyword)] == keyword:
            self.advance(len(keyword))
            eaten = True
        return eaten
           
    def readKeyword(self):
        while self.current_char.isalpha():
            if self.eat(KILLS):
                return Token(KILLS, KILLS)
            elif self.eat(BONUS):
                return Token(BONUS, self.get_bonus())
            elif self.eat(TIME):
                return Token(TIME, self.get_time())

    def error(self):
        raise Exception('invalid character: {}'.format(self.current_char))
        
    def get_next_token(self):
        while self.current_char is not None:
            
            if self.current_char.isspace():
                self.skipWhitespace()
                continue
            
            if self.current_char == NAME_MARKER:
                return Token(NAME, self.get_player_name())
                
            if self.current_char.isalpha():
                return self.readKeyword()

            self.error()

            
                
class Interpreter(object):
    def __init__(self, lexer):
        self.lexer = lexer
        self.current_token = self.lexer.get_next_token()

    def error(self):
        raise Exception('Invalid syntax')
        
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def kill_event(self, player_dict, event_players):
        while self.current_token.type == NAME:
            event_players.append(self.current_token.value)
            self.eat(NAME)
        print event_players
        for player in event_players[1:]:
            player_dict[event_players[0]].killed(player_dict[player])
            
            
    def event(self, player_dict):
        event_players = []
        while self.current_token.type in (NAME, KILLS):
            token = self.current_token
            if token.type == NAME:
                event_players.append(token.value)
                self.eat(NAME)
            if token.type == KILLS:
                self.eat(KILLS)
                self.kill_event(player_dict, event_players)
   
                
            
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
    
    player_dict = dict() # Player dictionary
    initialiseGame(player_dict, playerFile, newsFile, startID, index_attr)
    startReporting(player_dict) 
    with open(gameFile, 'r') as f:
        for line in f:
            lexer = Lexer(line)
            interpreter = Interpreter(lexer)
            interpreter.event(player_dict)
    score(player_dict)
    # outputScore(p=playerdict, html=True/False, k=attribute-to-sort-by, desc=True/False)
    outputScores(player_dict, False, 'points', True) # simple plaintext scores in point order
    outputScores(player_dict, True, 'points', True) # html scores in point order
    outputScores(player_dict, True, 'college', False) # html scores in college order
    outputScores(player_dict, True, 'name', False) # html scores in name order
    outputScores(player_dict, True, 'kills', True) # simple plaintext scores in kills order

