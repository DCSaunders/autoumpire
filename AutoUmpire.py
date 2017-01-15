#!/usr/bin/env python
import codecs 
import ConfigParser
import csv
import os.path
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from reporter import Reporter
from player import ShortGamePlayer, LongGamePlayer, PolicePlayer
from game_runner import LongGameRunner, ShortGameRunner
import utils
from constants import SHORT_GAME, LONG_GAME

# If changing playerlist column headers, be sure to edit these strings.
class Field(object):
    name = 'Name'
    pseud = 'Pseudonym'
    college = 'College'
    address = 'Address'
    water = 'Water Status'
    notes = 'Notes'
    email = 'Email'
    police = 'Police'
    seed = 'Seed'

# Reads player details from given csv
def read_player_details(player_file, game_type):
    player_dict = dict()
    with open(player_file, 'rb') as f:
        reader = csv.DictReader(f)            
        for row in reader:
            if game_type == LONG_GAME:
                if row[Field.police]:
                    player = PolicePlayer(row[Field.name], row[Field.pseud],
                            row[Field.college], row[Field.address],
                            row[Field.water], row[Field.notes], 
                            row[Field.email], 'long', 'default rank')
                else:
                    player = LongGamePlayer(row[Field.name], row[Field.pseud],
                            row[Field.college], row[Field.address],
                            row[Field.water], row[Field.notes], 
                            row[Field.email], row[Field.seed])
            elif game_type == SHORT_GAME:
                player = ShortGamePlayer(row[Field.name], row[Field.pseud],
                            row[Field.college], row[Field.address],
                            row[Field.water], row[Field.notes], 
                            row[Field.email])
            player_dict[player.name] = player
    return player_dict
     
def get_first_report_id(start_date):
    date_struct = utils.get_datetime(start_date)
    term = ('l', 'e', 'm')[(date_struct.tm_mon - 1) / 4]
    year = str(date_struct.tm_year)[-2:]
    return ''.join((term, year, '000'))

# Set up filenames, run game
if __name__ == '__main__':
    cfg = ConfigParser.ConfigParser()
    cfg.read('game_config.cfg')
    game_type = cfg.get('all', 'game_type').lower()
    news_file = cfg.get('all', 'news_file') 
    game_file = cfg.get('all', 'game_file')
    player_file = cfg.get('all', 'player_file')
    start_date = cfg.get('all', 'start_date')
    report_id = get_first_report_id(start_date)
    player_dict = read_player_details(player_file, game_type)
    reporter = Reporter(news_file, player_dict, report_id)
    if game_type == SHORT_GAME:
        runner = ShortGameRunner(game_file, start_date, player_dict)
    else:
        runner = LongGameRunner(game_file, start_date, player_dict)
    runner.run_game(reporter)
    reporter.output_scores(html=False, key='points', desc=True) 
    reporter.output_scores(html=True, key='points', desc=True)
    reporter.output_scores(html=True, key='college', desc=False)
    reporter.output_scores(html=True, key='name', desc=False)
    reporter.output_scores(html=True, key='kills', desc=True)

