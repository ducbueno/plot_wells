#!/usr/bin/env python3

import os

models_dir = '/home/ducbueno/Tools/opm/opm-tests/'
models = [f.path for f in os.scandir(models_dir) if f.is_dir()]
dict_file = open('decks.dict', 'a')
dict_file.write('{')

for model in models:
    for f in os.listdir(model):
        if f.endswith('.DATA'):
            model_path = model.split(f)[0]
            model_deck = f.strip('.DATA')
            dict_file.write('\'{}\': \'{}\', '.format(model_deck, model_path))

dict_file.write('}')
dict_file.close()
