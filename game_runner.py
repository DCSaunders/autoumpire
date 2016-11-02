#!/usr/bin/env python
import utils
import constants
from game_reader import Lexer, Interpreter


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
        lexer = Lexer(line, self.name_set)
        interpreter = Interpreter(lexer)
        interpreter.event()
        events = interpreter.event_dict
        event_time = events.pop(constants.TIME, None)
        if constants.DATE in events:
            self.date = events.pop(constants.DATE, None)
            formatted_date = utils.get_report_date(self.date)
            reporter.new_date(formatted_date)
        summaries, event_players = [], set()
        for token in events:
            self.players = [player_dict[name] for name in events[token]]
            event_players = event_players.union(self.players)
            self.get_token_summary(token, summaries, event_time)
        if event_time:
            reporter.new_report(summaries, event_players, event_time)
            
    def get_token_summary(self, token, summaries, event_time):
        summary_pseuds = ', '.join(
            [player.pseudonym for player in self.players])
        if token.type == constants.KILLS:
            summaries.append(self.kill_event(event_time))
        elif token.type == constants.BONUS:
            summaries.append(self.bonus_event(token.value, summary_pseuds))
        elif token.type == constants.PLAYER_OP:
            method_name = token.value.lower() + '_str'
            summary_method = getattr(self, method_name)
            summaries.append(summary_method(summary_pseuds))
        
    def event_str(self, summary_pseuds):
        return "An event happens involving {}.".format(summary_pseuds)

    def remove_str(self, summary_pseuds):
        for player in self.players:
            player.remove_from_game()
        return "{} removed from the game.".format(summary_pseuds)

    def casual_str(self, summary_pseuds):
        for player in self.players:
            player.make_casual()
        return "{} now playing casually.".format(summary_pseuds)

    def kill_event(self, kill_time):
        killer = self.players[0]
        dead_players = self.players[1:]
        kill_time = utils.get_datetime(self.date, event_time=kill_time)
        killer.killed(dead_players, kill_time)
        dead_list = [player.represent(kill_time) for player in dead_players]
        dead_str = ' and '.join(dead_list)
        return '{} kills {}.'.format(killer.represent(kill_time), dead_str)

class ShortGameRunner(GameRunner):
    def __init__(self, game_file, start_date, player_dict, reporter):
        super(ShortGameRunner, self).__init__(game_file, start_date, player_dict, reporter)
        
    def bonus_event(self, points, summary_pseuds):
        for player in self.players:
            player.bonus(points)
        return '{} bonus points to {}.'.format(points, summary_pseuds)


class LongGameRunner(GameRunner):
    def __init__(self, game_file, start_date, player_dict, reporter):
        self.police = {}
        self.split_police(player_dict)
        super(LongGameRunner, self).__init__(game_file, start_date, player_dict, reporter)

    def split_police(self, player_dict):
        for name, player in player_dict.items():
            print name, type(player)
  
