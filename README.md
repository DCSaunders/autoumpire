# autoumpire
Tool to help with umpiring an Assassins game. The current input involves a CSV file containing relevant player details (should be collected on signup) and writing a game file, which contains a near-natural-language description of events. Sample inputs are provided in this repo.

Running AutoUmpire.py with the gamefile and the player CSV in the same directory runs every event in the gamefile from start to finish.

To run the autoumpire, first ensure all Python files are in the same directory as a game_config.cfg file. Then:

```
python AutoUmpire.py
```

The config file must contain the following details (defaults shown):
```
[all]
# Name of file to contain output news templates
news_file = news.html
# Name of file to read game events from
game_file = game.txt
# Name of file containing player information
player_file = exampleplayers.csv
# Start of game date. Date format: dd.mm.yy
start_date = 01.06.16
```
The output includes a news text file and score files. The news text file contains individual HTML report templates for every individual event in the game file. An event is everything that happens on a line of the gamefile which includes a time. Example scorefile creation is at the bottom of AutoUmpire.py. Scorefiles can be created to contain plaintext scores or HTML tables, ordered by any player attribute.

Evolving variants of this tool have been used in games MW14, MW15, MW16.

There are no assassins in Cambridge.
