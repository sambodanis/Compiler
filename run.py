import os
import sys
import json
__author__ = 'sambodanis'

args = sys.argv
config = {}

if len(args) == 1:
    with open('config.json', 'r') as in_file:
        config = json.loads(in_file.read())
else:
    config['file_num'] = args[1]
    with open('config.json', 'w') as outfile:
        json.dump(config, outfile)

os.system('python main.py')
os.system('./assmule -di Assembly/testAss' + config['file_num'] + '.ass')
