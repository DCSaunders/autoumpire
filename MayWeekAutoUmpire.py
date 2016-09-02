#!/usr/bin/env python
import ConfigParser
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
# player_dict: dictionary mapping string player name to player object
# playerFile: csv file containing playerlist.
def initialise_game(player_dict, player_file, news_file):
    open(news_file, 'w').close()
    with open(player_file, 'rb') as f:
        reader = csv.DictReader(f)            
        for row in reader:
            player = Player(row[Field.name], row[Field.pseud],
                            row[Field.college], row[Field.address],
                            row[Field.water], row[Field.notes], 
                            row[Field.email], news_file)
            # Assign player dictionary, indexing by attribute defined in main
            player_dict[player.name] = player


# Score the playerlist
# p: player dictionary
def score(p):
    for player in p.itervalues():
        player.calcPoints()

# Build HTML string for report template
def report_string(players, event_str, ID, event_time):
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
    killed_str =  " and ".join(["{} ({})".format(otherPlayer.pseudonym, otherPlayer.name) for otherPlayer in otherPlayers])
    return "{} ({}) kills {}".format(killer.pseudonym, killer.name, killed_str)

def bonus_str(players):
    bonus_players = ["{}".format(player.pseudonym) for player in players]
    return "bonus points to {}".format(', '.join(bonus_players)) 

def event_str(players):
    event_players = ["{}".format(player.pseudonym) for player in players]
    return "an event happens involving {}".format(', '.join(event_players))

    
# Create a template for a new report.
def new_report(news, event_str, players, report_id, event_time, date=None):
    if not date:
        rep = report_string(players, event_str, report_id, event_time)
        report_num = str(int(report_id[1:]) + 1).zfill(len(report_id) - 1)
        report_id = report_id[0] + report_num
    else:
        rep = date
    with open(news, 'a') as f:
        f.write(rep)
    if report_id:
        return report_id

            
# Output plaintext scores
# p: sorted player dictionary
# scoreFile: file to output plaintext scores
def plaintext_scores(player_list, score_file):
    with open(score_file, 'w') as f:
        for player in player_list:
            point_str = ' '.join((player.name, str(player.points), "\n"))
            print point_str
            f.write(point_str)


# Output scores in HTML table
# p: sorted player dictionary.
# score_file: file for output.
def html_scores(player_list, score_file):
    t_s = "<table>"
    t_e = "</table>"
    row_s = "<tr>"
    row_e = "</tr>"
    entry_s = "<td>"
    entry_e = "</td>"
    nl = "\n"
    with open(score_file, 'w') as f:
        # Write scores in table
        f.write(t_s)
        for player in player_list:
            point_str = (player.name, player.pseudonym,
                      player.address, player.college,
                      player.waterStatus, player.notes,
                      str(player.kills), str(player.deaths),
                      '%.2f' % player.points)
            points ="{}{}".format(entry_e, entry_s).join(point_str)
            out = '%s%s%s%s%s%s' % (row_s, entry_s, points, entry_e, row_e, nl)
            f.write(out)
        f.write(t_e)


# Output scores in HTML table or plaintext
# p: player dictionary.
# k: key to sort on.
# html: false if plaintext output, true if html table
# desc: false if ascending, true if descending.
def output_scores(p, html, k, desc):
    player_list = sorted(p.values(), key=operator.attrgetter(k), reverse = desc)
    output_format = "html" if html else "plaintext"
    file_name = "scores-{}-{}.txt".format(k, output_format)
    if (html):
        html_scores(player_list, file_name)
    else:
        plaintext_scores(player_list, file_name)

def get_date(original_date):
    original_format = '%d.%m.%y'
    date_struct = time.strptime(original_date, original_format)
    new_format = '%A, %d %B'
    converted_date = time.strftime(new_format, date_struct)
    date_str = '\n<h3 xmlns="">{}</h3>\n'.format(converted_date)
    return date_str
    
def run_game(game_file, news_file, player_dict, report_id):
    name_set = set(player_dict.keys())
    date = None
    with open(game_file, 'r') as f:
        for line in f:
            lexer = game_reader.Lexer(line, name_set)
            interpreter = game_reader.Interpreter(lexer)
            interpreter.event()
            events = interpreter.event_dict
            event_time = events.pop(game_reader.TIME, None)
            if game_reader.DATE in events:
                date = events.pop(game_reader.DATE, None)
                date_str = get_date(date)
                new_report(news_file, None, None, None, None, date=date_str)
            event_strings = []
            event_players = set()
            for token in events:
                token_players = [player_dict[name] for name in events[token]]
                event_players = event_players.union(token_players)
                if token.type == game_reader.KILLS:
                    killer = token_players[0]
                    killer.killed(token_players[1:], event_time)
                    event_strings.append(kill_str(token_players))
                elif token.type == game_reader.BONUS:
                    for player_name in events[token]:
                        player_dict[player_name].bonus(token.value)
                    event_strings.append(bonus_str(token_players))
                elif token.type == game_reader.EVENT:
                    event_strings.append(event_str(token_players))
            if event_time:
                all_events = ', '.join(event_strings)
                report_id = new_report(news_file, all_events, event_players, report_id, event_time)
        
# Set up filenames, run game
if __name__ == '__main__':
    news_file = "news.txt" # Text file the news will be written to.
    game_file = "game.txt" # text file for game input
    report_id = "e17000" # Anchor for first entry in news file
    player_file = "MWAUexampleplayers.csv"
    player_dict = dict() 
    initialise_game(player_dict, player_file, news_file)
    run_game(game_file, news_file, player_dict, report_id)
    score(player_dict)
    output_scores(player_dict, False, 'points', True) 
    output_scores(player_dict, True, 'points', True)
    output_scores(player_dict, True, 'college', False)
    output_scores(player_dict, True, 'name', False)
    output_scores(player_dict, True, 'kills', True)

