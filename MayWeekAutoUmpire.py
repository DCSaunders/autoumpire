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
def score(player_dict):
    for player in player_dict.values():
        player.calc_points()

    
def get_report_date(original_date):
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

class GameRunner(object):
    def __init__(self, game_file, start_date, player_dict, reporter):
        self.date = start_date
        self.game_file = game_file
        self.players = []
        self.name_set = set(player_dict.keys())
        with open(game_file, 'r') as f:
            for line in f:
                self.run_game(line, player_dict, reporter)
    
    def run_game(self, line, player_dict, reporter):
        lexer = game_reader.Lexer(line, self.name_set)
        interpreter = game_reader.Interpreter(lexer)
        interpreter.event()
        events = interpreter.event_dict
        event_time = events.pop(game_reader.TIME, None)
        if game_reader.DATE in events:
            self.date = events.pop(game_reader.DATE, None)
            reporter.new_date(get_report_date(self.date))
        summaries, event_players = [], set()
        for token in events:
            self.players = [player_dict[name] for name in events[token]]
            event_players = event_players.union(self.players)
            if token.type == game_reader.KILLS:
                summaries.append(self.kill_event(event_time))
            elif token.type == game_reader.BONUS:
                summaries.append(self.bonus_event(token.value))
            elif token.type == game_reader.PLAYER_OP:
                method_name = token.value.lower() + '_str'
                summary_method = getattr(self, method_name)
                summaries.append(summary_method())
        if event_time:
            reporter.new_report(summaries, event_players, event_time)
                    
    def event_str(self):
        event_players = [player.pseudonym for player in self.players]
        return "An event happens involving {}.".format(', '.join(event_players))

    def remove_str(self):
        for player in self.players:
            player.remove_from_game()
        event_players = [player.pseudonym for player in self.players]
        return "{} removed from the game.".format(', '.join(event_players))

    def casual_str(self):
        for player in self.players:
            player.make_casual()
        event_players = [player.pseudonym for player in self.players]
        return "{} now playing casually.".format(', '.join(event_players))

    def kill_event(self, kill_time):
        killer = self.players[0]
        dead_players = self.players[1:]
        kill_time = get_datetime(self.date, event_time=kill_time)
        killer.killed(dead_players, kill_time)
        dead_list = [player.represent(kill_time) for player in dead_players]
        dead_str = ' and '.join(dead_list)
        return '{} kills {}.'.format(killer.represent(kill_time), dead_str)

    def bonus_event(self, points):
        for player in self.players:
            player.bonus(points)
        bonus_str = ', '.join([player.pseudonym for player in self.players])
        return '{} bonus points to {}.'.format(points, bonus_str)

    
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
    GameRunner(game_file, start_date, player_dict, reporter)
    score(player_dict)
    reporter.output_scores(html=False, key='points', desc=True) 
    reporter.output_scores(html=True, key='points', desc=True)
    reporter.output_scores(html=True, key='college', desc=False)
    reporter.output_scores(html=True, key='name', desc=False)
    reporter.output_scores(html=True, key='kills', desc=True)

