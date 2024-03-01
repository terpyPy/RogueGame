# import game_idea
# # this script launches the game
# game_idea.runPyGame()
import argparse
import sys
# 
parser = argparse.ArgumentParser(description='provides ability to run the game by version')
version_list = ['v1', 'v2']
parser.add_argument('version', type=str, help='version of the game to run', choices=version_list)
args = parser.parse_args()
#
if args.version == 'v1':
    import game_idea
    game_idea.runPyGame()
elif args.version == 'v2':
    import game_idea_v2
    game = game_idea_v2.MyGame()
    game.main()
else:
    sys.exit('invalid version number')