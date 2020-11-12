#!/usr/bin/env python3

import os
import ast
import sys
import shutil
import matplotlib.pyplot as plt
from subprocess import Popen, PIPE, call

dict_file = open('decks.dict', 'r')
content = dict_file.read()
address = ast.literal_eval(content)

deck = sys.argv[1]
model_dir = address[deck]
summary_cmd = '/home/ducbueno/Tools/opm/opm-common/build/bin/summary'
dirs = [model_dir + '/', model_dir + '/opm-simulation-reference/flow_legacy/']
mode = ['gpu', 'reference']
opts = ['WBHP', 'WOPR', 'WGPR', 'WWPR']

if os.path.isdir('data'):
    shutil.rmtree('data')
os.mkdir('data')

if os.path.isdir('plots'):
    shutil.rmtree('plots')
os.mkdir('plots')

count = 0
for d in dirs:
    process = Popen([summary_cmd, '-l', d + deck], stdout=PIPE, stderr=PIPE)
    output = process.stdout.read().split()
    output = [val.decode('ascii') for val in output]

    filtered_output = list(filter(lambda x: 'WBHP' in x, output))
    filtered_output = list(filter(lambda x: 'WBHPH' not in x, filtered_output))
    wells = [val.split(':')[-1] for val in filtered_output]
    if not wells:
        wells = [val.split(':')[-1] for val in output]
        wells = list(dict.fromkeys(wells))

    try:
        available_opts = [val.split(':')[0] for val in output]
        opts = list(set(available_opts).intersection(set(opts)))
    except NameError:
        opts = [val.split(':')[0] for val in output]

    for well in wells:
        for opt in opts:
            fname = mode[count] + '-' + opt + '-' + well + '.dat'
            wellopt = opt + ':' + well
            output_file = open('data/' + fname, 'w')
            call([summary_cmd, d + deck, 'TIME', wellopt], stdout=output_file)
            output_file.close()

    count = count + 1

files = os.listdir('data')
files = [f.split('-', 1)[-1] for f in files]
files = list(dict.fromkeys(files))
for f in files:
    opt, well = f.strip('.dat').split('-', 1)
    plt.xlabel('Time')
    plt.ylabel('{}'.format(opt))
    plt.title('Well: {}'.format(well))

    for m in mode:
        with open('data/' + m + '-' + f, 'r') as wdata:
            file_data = wdata.readlines()
            file_data = [item.split() for item in file_data]

            try:
                time = [item[0] for item in file_data if len(item) > 0]
                time = [float(item) for item in time[1:]]
                vals = [item[1] for item in file_data if len(item) > 0]
                vals = [float(item) for item in vals[1:]]

                if m == 'reference':
                    plt.plot(time, vals, '--', label=m)
                else:
                    plt.plot(time, vals, label=m)

                valid_vals = True;

            except ValueError as e:
                valid_vals = False;
                pass

    if(valid_vals):
        plt.legend(loc='upper right')
        plt.savefig('plots/{}-{}.png'.format(opt, well))
        plt.clf()

shutil.rmtree('data')
