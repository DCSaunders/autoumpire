# autoumpire
Tool to help with umpiring an Assassins game, specifically the May Week game. The current input involves a CSV file containing relevant player details (should be collected on signup) and writing a game file, which contains a near-natural-language description of events. Sample inputs are provided in this repo.

Running MayWeekAutoUmpire.py with the gamefile and the player CSV in the same directory runs every event in the gamefile from start to finish.

The output includes a news text file and score files. The news text file contains individual HTML report templates for every individual event in the game file. An event is everything that happens on a line of the gamefile which includes a time. Example scorefile creation is at the bottom of MayWeekAutoUmpire.py. Scorefiles can be created to contain plaintext scores or HTML tables, ordered by any player attribute.

Evolving variants of this tool have been used in games MW14, MW15, MW16.

There are no assassins in Cambridge.
