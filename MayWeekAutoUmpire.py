#!/usr/bin/env python
import codecs 
import ConfigParser
import csv
import os.path
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from reporter import Reporter
from player import MayWeekPlayer
from game_runner import GameRunner
import utils

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
            player = MayWeekPlayer(row[Field.name], row[Field.pseud],
                            row[Field.college], row[Field.address],
                            row[Field.water], row[Field.notes], 
                            row[Field.email])
            player_dict[player.name] = player
    return player_dict

# Score the playerlist
def score(player_dict):
    for player in player_dict.values():
        player.calc_points()
    
def get_first_report_id(start_date):
    date_struct = utils.get_datetime(start_date)
    term = ('l', 'e', 'm')[(date_struct.tm_mon - 1) / 4]
    year = str(date_struct.tm_year)[-2:]
    return ''.join((term, year, '000'))

# Set up filenames, run game
if __name__ == '__main__':
    cfg = ConfigParser.ConfigParser()
    cfg.read('game_config.cfg')
    news_file = cfg.get('all', 'news_file') 
    game_file = cfg.get('all', 'game_file')
    player_file = cfg.get('all', 'player_file')
    start_date = cfg.get('all', 'start_date')
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

