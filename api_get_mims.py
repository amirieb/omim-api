import sys
import json
import requests
import time
from random import randint
import os

'''set the your API_KEY here, see https://omim.org/api'''
API_KEY = ''


def read_data(filename):
    f = open(filename, 'r')
    data = json.load(f)
    print(len(data))
    return data


def dump_data(data):
    with open('OMIM_FULL.json', 'w') as outfile:
        json.dump(data, outfile)


def get_omim_data():
    omim_data = {}
    omim_data['omim'] = []

    # read list of mim ids to download, read the most recent list from omim.org
    os.system('curl -o ./mim2gene.txt https://omim.org/static/omim/data/mim2gene.txt')
    mims = [line.split('\t')[0].strip() for line in open('mim2gene.txt', 'r').readlines() if not line.startswith('#')]

    # if any, reload entries that have been downloaded so far.
    mim_ids_down = set([])
    if os.path.exists('OMIM_FULL.json'):
        omim_down = read_data('OMIM_FULL.json')
        for row in omim_down['omim']:
            mim = row['entry']['mimNumber']
            if mim not in mim_ids_down:
                mim_ids_down.add(mim)
                omim_data['omim'].append(row)
                del mims[mims.index(str(mim))]
    print('#downloaded mims: ', len(mim_ids_down))
    print('#to download mims: ', len(mims))

    # send queries to the api
    i, cnt_item, mim_errors = 0, 19, []  # cnt_item: number of items to download per request.. double check, THERE IS A LIMIT IMPOSED BY THE API
    while i < len(mims):
        time.sleep(randint(5, 15))
        try:
            link = 'https://api.omim.org/api/entry?mimNumber=' + ','.join(
                [mim for mim in mims[i:i + cnt_item]]) + '&format=json&include=all&apiKey=' + API_KEY
            print(i + cnt_item, link)
            r = requests.get(link)
            data = r.json()
            for entry in data['omim']['entryList']:
                # print '\t', i + cnt_item, entry['mimNumber'],
                omim_data['omim'].append(entry)
            i += cnt_item
        except():
            # print(mims[i:i + cnt_item])
            mim_errors.append(mims[i:i + cnt_item])
            print("Unexpected error:", sys.exc_info()[0])
            dump_data(omim_data)
            continue
    dump_data(omim_data)
    if len(mim_errors) > 0:
        print('\n errors for these mim ids: ', mim_errors)
        print('\n re-run the code to restart downloading from the last downloaded mim id.')
    else:
        print('Done!')


if __name__ == '__main__':
    get_omim_data()
