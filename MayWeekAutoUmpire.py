#!/usr/bin/env python
import csv
import operator
import os.path
from Player import Player
import game_reader

# If changing playerlist column headers, be sure to edit these strings.
class Field(object):
    name = 'Name'
    pseud = 'Pseudonym'
    college = 'College'
    address = 'Address'
    water = 'Water Status'
    notes = 'Notes'
    email = 'Email'
    

# Initialises playerlist and newsfile
# p: player dictionary.
# playerFile: csv file containing playerlist.
# newsFile: text file to output report templates
# startID: anchor ID used for unique HTML links
# index_attr: attribute to index playerlist. Default set to be name
def initialiseGame(p, playerFile, newsFile, startID, index_attr):
    initialiseNews(newsFile, startID)
    with open(playerFile, 'rb') as f:
        reader = csv.DictReader(f)            
        for row in reader:
            player = Player(row[Field.name], row[Field.pseud], row[Field.college], 
                            row[Field.address], row[Field.water], row[Field.notes], 
                            row[Field.email], newsFile)
            # Assign player dictionary, indexing by attribute defined in main
            p[getattr(player, index_attr)] = player


# Score the playerlist
# p: player dictionary
def score(p):
    for player in p.itervalues():
        player.calcPoints()

        
# Sets up news file with anchor for unique HTML links
# newsFile: output file.
# startID: ID for unique HTML links
def initialiseNews(newsFile, startID):
    with open(newsFile, 'w') as f:
            f.write(startID)



# Build HTML string for report template
def reportString(players, event_str, ID, time):
    nl = "\n"
    event_s = "<div xmlns="" class=\"event\">"
    hr = "<hr/>"
    id_s = "<span id={}>[{}]".format(ID, time)
    head_s = "<span class=\"headline\">"
    report_s = "<div class=\"report\">"
    indent_s = "<div class=\"indent\">"
    p_s = "<p>"
    p_e = "</p>"
    div_e = "</div>"
    span_e = "</span>"
    
    report_str = "".join(["{}{}{}{} reports: {}{}{}{}{}".format(report_s, indent_s, p_s, player.pseudonym, nl, p_e, div_e, div_e, div_e) for player in players])
    report = ("{}{}{}{}{}{}".format(nl, nl, event_s, hr, id_s, head_s),
              event_str,
              "{}{}{}{}".format(span_e, span_e, span_e, hr),
              report_str)

    return "".join(report)

def kill_str(players):
    killer = players[0]
    otherPlayers = players[1:]
    killed_str =  ", ".join(["{} ({})".format(otherPlayer.pseudonym, otherPlayer.name) for otherPlayer in otherPlayers])
    return " {} ({}) kills {}".format(killer.pseudonym, killer.name, killed_str)

    
# Create a template for a new report.
def newReport(news, events, players, time):
    lines = open(news, 'r').readlines()

    # ID is formed of one letter, then numbers
    ID = lines[0]
    idnum = int(ID[1:]) + 1
    ID = ID[0] + str(idnum)
    lines[0] = ID+"\n"
    event_str = kill_str(players)
    with open(news, 'w') as f:       
        for line in lines:
            f.write(line)
        f.close()
        rep = reportString(players, event_str, ID, time)

        with open(news, 'a') as f:
            f.write(rep)

            
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

def run_game(gameFile, newsFile, player_dict):
    with open(gameFile, 'r') as f:
        for line in f:
            lexer = game_reader.Lexer(line)
            interpreter = game_reader.Interpreter(lexer)
            interpreter.event()
            events = interpreter.event_dict
            time = events.pop(game_reader.TIME, None)
            
            for token in events:    
                if token.type == game_reader.KILLS:
                    killer = player_dict[events[token][0]]
                    killer.killed([player_dict[dead_player_name] for dead_player_name in events[token][1:]], time)
                elif token.type == game_reader.BONUS:
                    for player_name in events[token]:
                        player_dict[player_name].bonus(token.value)
            newReport(newsFile, events, [player_dict[player_name] for player_name in events[token]], time)
        
# Set up filenames, run game
if __name__ == '__main__':
    newsFile = "news.txt" # Text file the news will be written to.
    gameFile = "game.txt" # text file for game input
    startID = "e16000" # Anchor for first entry in news file
    playerFile = "MWAUexampleplayers.csv"
    index_attr = 'name' # Change to e.g. 'email', 'pseudonym' or other unique attr of Player class if want
    
    player_dict = dict() # Player dictionary
    initialiseGame(player_dict, playerFile, newsFile, startID, index_attr)
    run_game(gameFile, newsFile, player_dict)
    score(player_dict)
    # outputScore(p=playerdict, html=True/False, k=attribute-to-sort-by, desc=True/False)
    outputScores(player_dict, False, 'points', True) # simple plaintext scores in point order
    outputScores(player_dict, True, 'points', True) # html scores in point order
    outputScores(player_dict, True, 'college', False) # html scores in college order
    outputScores(player_dict, True, 'name', False) # html scores in name order
    outputScores(player_dict, True, 'kills', True) # simple plaintext scores in kills order

