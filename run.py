import os
import sys
import json
__author__ = 'sambodanis'

args = sys.argv
print args
config = {}

if len(args) == 1:
    with open('config.json', 'r') as in_file:
        config = json.loads(in_file.read())
    test_to_run = config['file_num']
    print config
else:
    test_to_run = args[1]
    with open('config.json', 'w') as outfile:
        json.dump({'file_num': test_to_run}, outfile)

os.system('python main.py')
os.system('./assmule -di Assembly/testAss' + test_to_run + '.ass')
