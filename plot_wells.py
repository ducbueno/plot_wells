#!/usr/bin/env python3

import os
import sys
import shutil
import subprocess
import matplotlib.pyplot as plt

#-------------------------------------------------------------------------------

def parse_summary(summary, opts):
    filtered_summary = list(filter(lambda x: 'WBHP' in x, summary))
    filtered_summary = list(filter(lambda x: 'WBHPH' not in x, filtered_summary))

    wells = [entry.split(':')[-1] for entry in filtered_summary]
    if not wells:
        wells = [entry.split(':')[-1] for entry in summary]
        wells = list(dict.fromkeys(wells))

    try:
        available_opts = [entry.split(':')[0] for entry in summary]
        opts = list(set(available_opts).intersection(set(opts)))
    except NameError:
        opts = [val.split(':')[0] for val in output]

    return wells, opts


def write_wells(wells, opts, stype, summary_cmd, deck):
    if not os.path.isdir('data'):
        os.mkdir('data')

    for well in wells:
        for opt in opts:
            fname = stype + '-' + opt + '-' + well + '.dat'
            wellopt = opt + ':' + well
            output_file = open('data/' + fname, 'w')
            subprocess.call([summary_cmd, deck, 'TIME', wellopt], stdout=output_file)
            output_file.close()

#-------------------------------------------------------------------------------

summary_cmd = '/home/ducbueno/Tools/opm/opm-common/build/bin/summary'
deck = sys.argv[1]
opts = ['WBHP', 'WOPR', 'WGPR', 'WWPR']

try:
    summary = subprocess.check_output([summary_cmd, '-l', deck], stderr=subprocess.STDOUT).decode().split()
    wells, opts = parse_summary(summary, opts)
    write_wells(wells, opts, 'mysim', summary_cmd, deck)
except subprocess.CalledProcessError:
    print("Couldn't find deck {} \nExiting...".format(deck))
    sys.exit(1)

if len(sys.argv) > 2:
    try:
        deck_path = '/'.join(deck.split('/')[:-1])
        reference_prog = sys.argv[2].split('--reference=')[-1]
        if(reference_prog == 'flow'):
            reference_path = deck_path + '/opm-simulation-reference/flow_legacy/'
        elif(reference_prog == 'eclipse'):
            reference_path = deck_path + '/eclipse-simulation/'
        else:
            print("Invalid reference program. Valid options for --reference are \'flow\' and \'eclipse\'.")
            sys.exit(1)

        deck_name = deck.split('/')[-1]
        reference_deck = reference_path + deck_name
        summary_reference = subprocess.check_output([summary_cmd, '-l', reference_deck], stderr=subprocess.STDOUT).decode().split()
        wells, opts = parse_summary(summary_reference, opts)
        write_wells(wells, opts, 'reference', summary_cmd, reference_deck)
    except subprocess.CalledProcessError:
        print("Couldn't find deck {} in {} \nExiting...".format(deck_name, reference_path))
        sys.exit(1)

#-------------------------------------------------------------------------------

if not os.path.isdir('plots'):
    os.mkdir('plots')

if os.path.isdir('plots/' + deck_name):
    shutil.rmtree('plots/' + deck_name)
os.mkdir('plots/' + deck_name)

available_summaries = os.listdir('data')
summaries = list(dict.fromkeys([s.split('-', 1)[-1] for s in available_summaries]))
stypes = list(dict.fromkeys([s.split('-', 1)[0] for s in available_summaries]))

for s in summaries:
    opt, well = s.strip('.dat').split('-', 1)
    plt.xlabel('Time')
    plt.ylabel('{}'.format(opt))
    plt.title('Well: {}'.format(well))

    for t in stypes:
        with open('data/' + t + '-' + s, 'r') as scontent:
            sdata = scontent.readlines()
            sdata = [item.split() for item in sdata]

            try:
                time = [item[0] for item in sdata if len(item) > 0]
                time = [float(item) for item in time[1:]]
                vals = [item[1] for item in sdata if len(item) > 0]
                vals = [float(item) for item in vals[1:]]

                if t == 'reference':
                    plt.plot(time, vals, label=t)
                else:
                    if(len(stypes) > 1):
                        plt.plot(time, vals, '--', label=t)
                    else:
                        plt.plot(time, vals, label=t)

                valid_vals = True;

            except ValueError as e:
                valid_vals = False;
                pass

    if(valid_vals):
        plt.legend(loc='upper right')
        plt.savefig('plots/' + deck_name + '/{}-{}.png'.format(opt, well))
        plt.clf()

shutil.rmtree('data')
