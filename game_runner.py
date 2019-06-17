#!/usr/bin/env python
import cPickle
import utils
import constants
from game_reader import Lexer, Interpreter
from player import PolicePlayer
from targeter import Graph

class GameRunner(object):
    def __init__(self, game_file, start_date, player_dict):
        self.date = start_date
        self.game_file = game_file
        self.player_dict = player_dict
        self.event_players = []
        self.name_set = set(self.player_dict.keys())

    def run_game(self, reporter):
        with open(self.game_file, 'r') as f:
            for line in f:
                self.run_event(line, reporter)
    
    def run_event(self, line, reporter):
        lexer = Lexer(line, self.name_set)
        interpreter = Interpreter(lexer)
        interpreter.event()
        events = interpreter.event_dict
        event_time = events.pop(constants.TIME, None)
        time_value = utils.get_datetime(self.date, event_time=event_time)
        if constants.DATE in events:
            self.date = events.pop(constants.DATE, None)
            formatted_date = utils.get_report_date(self.date)
            reporter.new_date(formatted_date)
        summaries, players_in_template = [], set()
        for token in events:
            if token.type == constants.KILLS:
                # has to be done before reporting to ensure correct colorisation
                self.event_players = [self.player_dict[name]
                                      for name in events[token]]
                self.update_kill(time_value)
        for token in events:
            self.event_players = [self.player_dict[name]
                                  for name in events[token]]
            players_in_template = players_in_template.union(self.event_players)
            self.get_token_summary(token, summaries, time_value)
        if event_time:
            reporter.new_report(summaries, players_in_template, event_time, time_value)
            
    def get_summary_pseuds(self, players, time):
        return ' and '.join([player.represent(time) for player in players])

    def get_token_summary(self, token, summaries, event_time):
        if token.type == constants.KILLS:
            summaries.append(self.kill_event(event_time))
        elif token.type == constants.PLAYER_OP:
            summary_pseuds = self.get_summary_pseuds(self.event_players, event_time)
            method_name = token.value.lower() + '_str'
            summary_method = getattr(self, method_name)
            summaries.append(summary_method(summary_pseuds))
        
    def event_str(self, summary_pseuds):
        return "An event happens involving {}.".format(summary_pseuds)

    def remove_str(self, summary_pseuds):
        for player in self.event_players:
            player.remove_from_game()
        return "{} removed from the game.".format(summary_pseuds)

    def casual_str(self, summary_pseuds):
        for player in self.event_players:
            player.make_casual()
        return "{} now playing casually.".format(summary_pseuds)

    def update_kill(self, event_time):
        killer = self.event_players[0]
        dead_players = self.event_players[1:]
        killer.killed(dead_players, event_time)


    def kill_event(self, event_time):
        killer = self.event_players[0]
        dead_str = self.get_summary_pseuds(self.event_players[1:], event_time)
        return '{} kills {}.'.format(killer.represent(event_time), dead_str)

class ShortGameRunner(GameRunner):
    def __init__(self, game_file, start_date, player_dict):
        super(ShortGameRunner, self).__init__(
            game_file, start_date, player_dict)
        
    # Score the playerlist
    def score(self):
        for player in self.player_dict.values():
            player.calc_points()

    def get_token_summary(self, token, summaries, event_time):
        if token.type == constants.BONUS:
            summary_pseuds = self.get_summary_pseuds(self.event_players, event_time)
            summaries.append(self.bonus_event(token.value, summary_pseuds))
        else:
            super(ShortGameRunner, self).get_token_summary(
                token, summaries, event_time)
            
    def run_game(self, reporter):
        with open(self.game_file, 'r') as f:
            for line in f:
                self.run_event(line, reporter)
        self.score()

    def bonus_event(self, points, summary_pseuds):
        for player in self.event_players:
            player.bonus(points)
        return '{} bonus points to {}.'.format(points, summary_pseuds)


class LongGameRunner(GameRunner):
    def __init__(self, game_file, start_date, player_dict, graph_file):
        super(LongGameRunner, self).__init__(game_file, start_date,
            player_dict)
        self.police = {}
        self.get_police()
        self.targeter = self.load(graph_file)
        
    def load(self, graph_file):
        try:
            with open(graph_file, 'rb') as f_in:
                print "Loading initial graph from {}".format(graph_file)
                targeter = cPickle.load(f_in)
                self.assign_initial_nodes(targeter)
                #targeter.print_graph(player_names=True)
        except(OSError, IOError):
            print "Cannot load from {} - initialising new graph".format(
                graph_file)
            targeter = Graph(len(self.player_dict) - len(self.police))
            targeter.initialise(self.player_dict.values(), graph_file)
        return targeter

    def assign_initial_nodes(self, targeter):
        for node in targeter.nodes:
            self.player_dict[node.player.name].node = node
            
    def get_police(self):
        for name, player in self.player_dict.items():
            if type(player) == PolicePlayer:
                self.police[name] = player

    def run_game(self, reporter):
        #self.targeter.print_graph(player_names=True)
        with open(self.game_file, 'r') as f:
            for line in f:
                self.run_event(line, reporter)
        #self.targeter.print_graph(player_names=True)
