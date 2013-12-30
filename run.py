import os
import sys
import json
__author__ = 'sambodanis'

args = sys.argv
config = {}

# If user specifies new test file to use then use it, else use previous
if len(args) == 1:
    with open('config.json', 'r') as in_file:
        config = json.loads(in_file.read())
else:
    config['file_num'] = args[1]
    with open('config.json', 'w') as outfile:
        json.dump(config, outfile)

# Run compiler on specified test file and then
# run output through assembler and emulator
os.system('python main.py')
#os.system('./assmule -di Assembly/testAss' + config['file_num'] + '.ass')
