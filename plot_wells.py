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
opts = [b'WBHP', b'WOPR', b'WGPR', b'WWPR']

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

    filtered_output = list(filter(lambda x: b'WBHP' in x, output))
    filtered_output = list(filter(lambda x: b'WBHPH' not in x, filtered_output))
    wells = [val.split(b':')[-1] for val in filtered_output]
    if not wells:
        wells = [val.split(b':')[-1] for val in output]
        wells = list(dict.fromkeys(wells))

    try:
        available_opts = [val.split(b':')[0] for val in output]
        opts = list(set(available_opts).intersection(set(opts)))
    except NameError:
        opts = [val.split(b':')[0] for val in output]

    for well in wells:
        well = well.decode('ascii')
        for opt in opts:
            opt = opt.decode('ascii')
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
            next(wdata)
            time = []
            vals = []

            try:
                for line in wdata:
                    l = line.split()
                    time.append(float(l[0]))
                    vals.append(float(l[1]))
            except ValueError as e:
                pass

            if vals:
                if m == 'reference':
                    plt.plot(time, vals, '--', label=m)
                else:
                    plt.plot(time, vals, label=m)

    plt.legend(loc='upper right')
    plt.savefig('plots/{}-{}.png'.format(opt, well))
    plt.clf()
