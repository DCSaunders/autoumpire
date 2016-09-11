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
def read_player_details(player_file):
    player_dict = dict()
    with open(player_file, 'rb') as f:
        reader = csv.DictReader(f)            
        for row in reader:
            player = Player(row[Field.name], row[Field.pseud],
                            row[Field.college], row[Field.address],
                            row[Field.water], row[Field.notes], 
                            row[Field.email])
            player_dict[player.name] = player
    return player_dict

# Score the playerlist
# p: player dictionary
def score(player_dict):
    for player in player_dict.values():
        player.calc_points()


def kill_event(players, event_strings, date, kill_time):
    killer = players[0]
    dead = players[1:]
    death_time = get_datetime(date, event_time=kill_time)
    killer.killed(dead, death_time)
    dead_str = ' and '.join([player.represent(death_time) for player in dead])
    event_str = '{} kills {}.'.format(killer.represent(death_time), dead_str)
    event_strings.append(event_str)

    
def bonus_event(players, points, event_strings):
    for player in players:
        player.bonus(points)
    bonus_str = ', '.join([player.pseudonym for player in players])
    event_strings.append('{} bonus points to {}.'.format(points, bonus_str)) 

    
def event_str(players):
    event_players = [player.pseudonym for player in players]
    return "An event happens involving {}.".format(', '.join(event_players))


def get_report_date(events):
    original_date = events.pop(game_reader.DATE, None)
    date_struct = get_datetime(original_date)
    new_format = '%A, %d %B'
    new_date = time.strftime(new_format, date_struct)
    return new_date


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
                reporter.new_date(get_report_date(events))
            event_strings = []
            event_players = set()
            for token in events:
                token_players = [player_dict[name] for name in events[token]]
                event_players = event_players.union(token_players)
                if token.type == game_reader.KILLS:
                    kill_event(token_players, event_strings, date, event_time)
                elif token.type == game_reader.BONUS:
                    bonus_event(token_players, token.value, event_strings)
                elif token.type == game_reader.EVENT:
                    event_strings.append(event_str(token_players))
            if event_time:
                reporter.new_report(event_strings, event_players, event_time)

                
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
    player_dict = read_player_details(player_file)
    reporter = Reporter(news_file, player_dict, report_id)
    run_game(game_file, player_dict, reporter, start_date)
    score(player_dict)
    reporter.output_scores(html=False, key='points', desc=True) 
    reporter.output_scores(html=True, key='points', desc=True)
    reporter.output_scores(html=True, key='college', desc=False)
    reporter.output_scores(html=True, key='name', desc=False)
    reporter.output_scores(html=True, key='kills', desc=True)

