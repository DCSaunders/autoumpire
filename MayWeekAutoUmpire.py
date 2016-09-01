#!/usr/bin/env python
import csv
import operator
import os.path
import time
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
# index_attr: attribute to index playerlist. Default set to be name
def initialiseGame(p, playerFile, index_attr, newsFile):
    open(newsFile, 'w').close()
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

# Build HTML string for report template
def reportString(players, event_str, ID, event_time):
    nl = "\n"
    event_s = "<div xmlns="" class=\"event\">"
    hr = "<hr/>"
    id_s = "<span id={}>[{}]".format(ID, event_time)
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
    return "{} ({}) kills {}".format(killer.pseudonym, killer.name, killed_str)

def bonus_str(players):
    bonus_players = ["{}".format(player.pseudonym) for player in players]
    return "bonus points to {}".format(', '.join(bonus_players)) 

def event_str(players):
    event_players = ["{}".format(player.pseudonym) for player in players]
    return "an event happens involving {}".format(', '.join(event_players))

    
# Create a template for a new report.
def newReport(news, event_str, players, report_id, event_time, date=None):
    if not date:
        rep = reportString(players, event_str, report_id, event_time)
        report_num = str(int(report_id[1:]) + 1).zfill(len(report_id) - 1)
        report_id = report_id[0] + report_num
    else:
        rep = get_date(date)
    with open(news, 'a') as f:
        f.write(rep)
    if report_id:
        return report_id

            
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

def get_date(date):
    date_format = '%A, %d %B'
    converted_date = time.strftime(date_format, date)
    date_str = '\n<h3 xmlns="">{}</h3>\n'.format(converted_date)
    return date_str
    
def run_game(gameFile, newsFile, player_dict, report_id):
    name_set = set(player_dict.keys())
    date = None
    date_format = '%d.%m.%y'
    with open(gameFile, 'r') as f:
        for line in f:
            lexer = game_reader.Lexer(line, name_set)
            interpreter = game_reader.Interpreter(lexer)
            interpreter.event()
            events = interpreter.event_dict
            event_time = events.pop(game_reader.TIME, None)
            if game_reader.DATE in events:
                date = events.pop(game_reader.DATE, None)
                date = time.strptime(date, date_format)
                newReport(newsFile, None, None, None, None, date=date)
            event_strings = []
            players = set()
            for token in events:
                event_players = [player_dict[player_name] for player_name in events[token]]
                players = players.union(event_players)
                if token.type == game_reader.KILLS:
                    killer = event_players[0]
                    killer.killed(event_players[1:], event_time)
                    event_strings.append(kill_str(event_players))
                elif token.type == game_reader.BONUS:
                    for player_name in events[token]:
                        player_dict[player_name].bonus(token.value)
                    event_strings.append(bonus_str(players))
                elif token.type == game_reader.EVENT:
                    event_strings.append(event_str(players))
            if event_time:
                all_events = ', '.join(event_strings)
                report_id = newReport(newsFile, all_events, players, report_id, event_time)
        
# Set up filenames, run game
if __name__ == '__main__':
    newsFile = "news.txt" # Text file the news will be written to.
    gameFile = "game.txt" # text file for game input
    report_id = "e17000" # Anchor for first entry in news file
    playerFile = "MWAUexampleplayers.csv"
    index_attr = 'name'
    player_dict = dict() # Player dictionary
    initialiseGame(player_dict, playerFile, index_attr, newsFile)
    run_game(gameFile, newsFile, player_dict, report_id)
    score(player_dict)
    outputScores(player_dict, False, 'points', True) # simple plaintext scores in point order
    outputScores(player_dict, True, 'points', True) # html scores in point order
    outputScores(player_dict, True, 'college', False) # html scores in college order
    outputScores(player_dict, True, 'name', False) # html scores in name order
    outputScores(player_dict, True, 'kills', True) # simple plaintext scores in kills order

