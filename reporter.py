#!/usr/bin/env python

import codecs
import operator
import constants

class Reporter(object):

    def __init__(self, news_file, player_dict, report_id, using_windows):
        self.HEADERS = ['Name', 'Pseudonym', 'Address', 'College', 'Water status', 'Notes', 'Kills', 'Deaths', 'Points']
        self.player_dict = player_dict
        self.news_file = news_file
        self.report_id = report_id
        self.le = '\n'
        if using_windows:
            self.le = '\r\n'
        with open(self.news_file, 'w') as f:
            f.write(constants.NEWS_PREAMBLE)


    # Build HTML string for report template
    def report_string(self, players, event_str, event_time):
        event_div = "{}{}<div xmlns="" class=\"event\"><hr/>{}</div>"
        id_str = "<span id={}>[{}] {} </span>"
        headline = "<span class=\"headline\">{}</span>"
        indent = "<div class=\"indent\">{}</div>"
        report = "<div class=\"report\">{}</div>".format(indent)
        report_para = "<p>{} reports:{}</p>"   
        report_list =  [report.format(report_para.format(player.pseudonym, self.le))
                        for player in players]
        event = event_div.format(
            self.le,
            self.le,
            id_str.format(self.report_id, event_time, headline.format(event_str)))
        return event + ''.join(report_list)

    # Create a template for a new report.
    def new_report(self, event_strings, players, event_time):
        event_str = ' '.join(event_strings)
        pad_len = len(self.report_id) - 1
        report = self.report_string(players, event_str, event_time)
        report_num = int(self.report_id[1:]) + 1
        report_numstr = str(report_num).zfill(pad_len)
        self.report_id = self.report_id[0] + report_numstr
        with codecs.open(self.news_file, 'a', encoding='utf-8') as f:
            f.write(report)

    def new_date(self, date_str):
        date_str = '{}<h3 xmlns="">{}</h3>{}'.format(self.le, date_str, self.le)
        with open(self.news_file, 'a') as f:
            f.write(date_str)
            
    # Output plaintext scores
    # p: sorted player dictionary
    # scoreFile: file to output plaintext scores
    def plaintext_scores(self, player_list, score_file):
        with codecs.open(score_file, 'w', encoding='utf-8') as f:
            for player in player_list:
                point_str = ' '.join(
                    (player.name, str(player.points), self.le))
                f.write(point_str)


    # Output scores in HTML table
    # player_list: sorted player dictionary.
    # score_file: file for output.
    def html_scores(self, player_list, score_file):
        table_start = '<table xmlns="" class="playerlist">'
        table_end = "</table>"
        row = "<tr>{}</tr>{}"
        header = "<th>{}</th>" 
        cell = "<td>{}</td>"
        with codecs.open(score_file, 'w', encoding='utf-8') as f:
            # Write scores in table
            f.write(constants.SCORES_PREAMBLE)
            f.write(table_start)
            headers = ''.join([header.format(info) for info in self.HEADERS])
            f.write(row.format(headers, self.le))
            for player in player_list:
                pseuds = ' AKA '.join(player.pseud_list)
                player_info = [player.name, pseuds,
                               player.address, player.college,
                               player.water_status, player.notes,
                               str(player.kills), str(player.deaths),
                               '%.2f' % player.points]
                if player.casual:
                    for index, info in enumerate(player_info):
                        player_info[index] = '<i>{}</i>'.format(info)
                cells = ''.join([cell.format(info) for info in player_info])
                f.write(row.format(cells, self.le))
            f.write(table_end)
            f.write(constants.SCORES_POSTAMBLE)

    def get_current_players_and_casuals(self):
        casual_players = []
        srs_players = []
        all_players = self.player_dict.values()
        for player in all_players:
            if player.in_game:
                if player.casual:
                    casual_players.append(player)
                else:
                    srs_players.append(player)
        return srs_players, casual_players

    # Output scores in HTML table or plaintext
    # html: false if plaintext output, true if html table
    # k: key to sort on.
    # desc: false if ascending, true if descending.
    def output_scores(self, html, key, desc):
        players, casual_players = self.get_current_players_and_casuals()
        players = sorted(players,
                         key=lambda x: x.kill_death_ratio(),
                         reverse = True)
        ordered_players = sorted(players,
                                 key=operator.attrgetter(key), reverse = desc)
        all_players = ordered_players + casual_players
        output_format = "html" if html else "txt"
        file_name = "scores-{}.{}".format(key, output_format)
        if (html):
            self.html_scores(all_players, file_name)
        else:
            self.plaintext_scores(all_players, file_name)

    def finish_news(self):
        with open(self.news_file, 'a') as f:
            f.write(constants.NEWS_POSTAMBLE)

