#!/usr/bin/env python
import operator

class Reporter(object):

    def __init__(self, news_file, player_dict, report_id):
        self.HEADERS = ['Name', 'Pseudonym', 'Address', 'College', 'Water status', 'Notes', 'Kills', 'Deaths', 'Points']
        self.news_file = news_file
        self.players = player_dict
        self.report_id = report_id
        open(self.news_file, 'w').close()


    # Build HTML string for report template
    def report_string(self, players, event_str, event_time):
        event_div = "\n\n<div xmlns="" class=\"event\"><hr/>{}</div>"
        id_str = "<span id={}>[{}] {} </span>"
        headline = "<span class=\"headline\">{}</span>"
        indent = "<div class=\"indent\">{}</div>"
        report = "<div class=\"report\">{}</div>".format(indent)
        report_para = "<p>{} reports:\n</p>"   
        report_str = "".join([report.format(report_para.format(player.pseudonym))
                              for player in players])
        event = (event_div.format(id_str.format(self.report_id, event_time, headline.format(event_str))))
        return event + report_str


    # Create a template for a new report.
    def new_report(self, event_str, players, event_time, date=None):
        if not date:
            rep = self.report_string(players, event_str, event_time)
            report_num = str(int(self.report_id[1:]) + 1).zfill(len(self.report_id) - 1)
            self.report_id = self.report_id[0] + report_num
        else:
            rep = date
        with open(self.news_file, 'a') as f:
            f.write(rep)


    # Output plaintext scores
    # p: sorted player dictionary
    # scoreFile: file to output plaintext scores
    def plaintext_scores(self, player_list, score_file):
        with open(score_file, 'w') as f:
            for player in player_list:
                point_str = ' '.join((player.name, str(player.points), "\n"))
                print point_str
                f.write(point_str)


    # Output scores in HTML table
    # p: sorted player dictionary.
    # score_file: file for output.
    def html_scores(self, player_list, score_file):
        table_start = '<table xmlns="" class="playerlist">'
        table_end = "</table>"
        row = "<tr>{}</tr>\n"
        header = "<th>{}</th>" 
        cell = "<td>{}</td>"
        with open(score_file, 'w') as f:
            # Write scores in table
            f.write(table_start)
            headers = ''.join([header.format(info) for info in self.HEADERS])
            f.write(row.format(headers))
            for player in player_list:
                player_info = (player.name, player.pseudonym,
                               player.address, player.college,
                               player.water_status, player.notes,
                               str(player.kills), str(player.deaths),
                               '%.2f' % player.points)
                cells = ''.join([cell.format(info) for info in player_info])
                f.write(row.format(cells))
            f.write(table_end)


    # Output scores in HTML table or plaintext
    # p: player dictionary.
    # k: key to sort on.
    # html: false if plaintext output, true if html table
    # desc: false if ascending, true if descending.
    def output_scores(self, html, k, desc):
        ordered_players = sorted(self.players.values(),
                                 key=operator.attrgetter(k), reverse = desc)
        output_format = "html" if html else "txt"
        file_name = "scores-{}.{}".format(k, output_format)
        if (html):
            self.html_scores(ordered_players, file_name)
        else:
            self.plaintext_scores(ordered_players, file_name)

