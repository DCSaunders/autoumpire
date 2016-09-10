#!/usr/bin/env python
import ConfigParser
import csv
import os.path
import time
from reporter import Reporter
from player import Player
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

# Reads player details from given csv
def read_player_details(player_dict, player_file):
    with open(player_file, 'rb') as f:
        reader = csv.DictReader(f)            
        for row in reader:
            player = Player(row[Field.name], row[Field.pseud],
                            row[Field.college], row[Field.address],
                            row[Field.water], row[Field.notes], 
                            row[Field.email])
            player_dict[player.name] = player

# Score the playerlist
# p: player dictionary
def score(p):
    for player in p.itervalues():
        player.calcPoints()

def kill_str(players, date_time):
    killer = players[0]
    other_players = players[1:]
    killed_str =  " and ".join(['{}'.format(other_player.represent_player(date_time)) for other_player in other_players])
    return "{} kills {}.".format(killer.represent_player(date_time), killed_str)

def bonus_str(players):
    bonus_players = ["{}".format(p.pseudonym) for p in players]
    return "Bonus points to {}.".format(', '.join(bonus_players)) 

def event_str(players):
    event_players = ["{}".format(p.pseudonym) for p in players]
    return "An event happens involving {}.".format(', '.join(event_players))


def get_report_date(original_date):
    date_struct = get_datetime(original_date)
    new_format = '%A, %d %B'
    converted_date = time.strftime(new_format, date_struct)
    date_str = '\n<h3 xmlns="">{}</h3>\n'.format(converted_date)
    return date_str

def get_datetime(date, event_time=None):
    date_format = '%d.%m.%y'
    if event_time:
        date = ' '.join((date, event_time))
        date_format = ' '.join((date_format, '%H:%M'))
    return time.strptime(date, date_format)
    
def run_game(game_file, player_dict, reporter, start_date):
    name_set = set(player_dict.keys())
    date = start_date
    with open(game_file, 'r') as f:
        for line in f:
            lexer = game_reader.Lexer(line, name_set)
            interpreter = game_reader.Interpreter(lexer)
            interpreter.event()
            events = interpreter.event_dict
            event_time = events.pop(game_reader.TIME, None)
            if game_reader.DATE in events:
                date = events.pop(game_reader.DATE, None)
                date_str = get_report_date(date)
                reporter.new_report(None, None, None, date=date_str)
            event_strings = []
            event_players = set()
            for token in events:
                token_players = [player_dict[name] for name in events[token]]
                event_players = event_players.union(token_players)
                if token.type == game_reader.KILLS:
                    killer = token_players[0]
                    death_time = get_datetime(date, event_time=event_time)
                    killer.killed(token_players[1:], death_time)
                    event_strings.append(kill_str(token_players, death_time))
                elif token.type == game_reader.BONUS:
                    for player_name in events[token]:
                        player_dict[player_name].bonus(token.value)
                    event_strings.append(bonus_str(token_players))
                elif token.type == game_reader.EVENT:
                    event_strings.append(event_str(token_players))
            if event_time:
                all_events = ' '.join(event_strings)
                reporter.new_report(all_events, event_players, event_time)
   
def get_first_report_id(start_date):
    date_struct = get_datetime(start_date)
    term = ('l', 'e', 'm')[(date_struct.tm_mon - 1) / 4]
    year = str(date_struct.tm_year)[-2:]
    return ''.join((term, year, '000'))
                   
# Set up filenames, run game
if __name__ == '__main__':
    cfg = ConfigParser.ConfigParser()
    cfg.read('game_config.cfg')
    news_file = cfg.get('MWAU', 'news_file') 
    game_file = cfg.get('MWAU', 'game_file')
    player_file = cfg.get('MWAU', 'player_file')
    start_date = cfg.get('MWAU', 'start_date')
    report_id = get_first_report_id(start_date)
    player_dict = dict() 
    read_player_details(player_dict, player_file)
    reporter = Reporter(news_file, player_dict, report_id)
    run_game(game_file, player_dict, reporter, start_date)
    score(player_dict)
    reporter.output_scores(False, 'points', True) 
    reporter.output_scores(True, 'points', True)
    reporter.output_scores(True, 'college', False)
    reporter.output_scores(True, 'name', False)
    reporter.output_scores(True, 'kills', True)

