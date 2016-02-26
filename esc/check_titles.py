#!/usr/bin/env python3

import collections
import csv
import pathlib
import pprint
import re
import sys
import shutil
import tempfile
import time
import ck2parser

rootpath = ck2parser.rootpath
vanilladir = ck2parser.vanilladir
modpath = rootpath / 'SWMH-BETA/SWMH'
minipath = rootpath / 'MiniSWMH/MiniSWMH'

MINISWMH = False

source_paths = (modpath, minipath) if MINISWMH else (modpath,)

results = {True: collections.defaultdict(list),
           False: collections.defaultdict(list)}

def check_title(v, path, titles, lhs=False, line=None):
    if isinstance(v, str):
        v_str = v
    else:
        v_str = v.val
    if ck2parser.is_codename(v_str) and v_str not in titles:
        if line is None:
            line = '<file>'
        else:
            line.indent = 0
            v_lines = line.inline_str(0)[0].splitlines()
            line = next((l for l in v_lines if not re.match(r'\s*#', l)),
                        v_lines[0])
        results[lhs][path].append(line)
        return False
    return True

def check_titles(path, titles):
    def recurse(tree):
        if tree.has_pairs:
            for p in tree:
                n, v = p
                v_is_obj = isinstance(v, ck2parser.Obj)
                check_title(n, path, titles, v_is_obj, p)
                if v_is_obj:
                    recurse(v)
                else:
                    check_title(v, path, titles, line=p)
        else:
            for v in tree:
                check_title(v, path, titles, line=v)

    try:
        recurse(ck2parser.parse_file(path))
    except:
        print(path)
        raise

def check_regions(titles, titles_de_jure):
    bad_titles = []

    def check_region(n):
        if ck2parser.is_codename(n.val) and n.val not in titles_de_jure:
            bad_titles.append(n.val)

    def recurse(tree):
        if tree.has_pairs:
            for p in tree:
                n, v = p
                v_is_obj = isinstance(v, ck2parser.Obj)
                check_title(n, path, titles, v_is_obj, p)
                check_region(n)
                if v_is_obj:
                    recurse(v)
                else:
                    check_title(v, path, titles, line=p)
                    check_region(v)
        else:
            for v in tree:
                check_title(v, path, titles, line=v)
                check_region(v)

    path = (minipath if MINISWMH else modpath) / 'map/geographical_region.txt'
    tree = ck2parser.parse_file(path)
    recurse(tree)
    return bad_titles

def check_province_history(titles):
    tree = ck2parser.parse_file(modpath / 'map/default.map')
    defs = tree['definitions'].val
    _max_provinces = int(tree['max_provinces'].val)
    id_name_map = {}
    for row in ck2parser.csv_rows(
        (minipath if MINISWMH else modpath) / 'map' / defs):
        try:
            id_name_map[int(row[0])] = row[4]
        except (IndexError, ValueError):
            continue
    for path in ck2parser.files('history/provinces/*', *source_paths):
        number, name = path.stem.split(' - ')
        number = int(number)
        if id_name_map[number] == name:
            check_titles(path, titles)

def process_landed_titles():
    titles = set()
    titles_de_jure = set()

    def recurse(tree):
        parent_is_titular = True
        for n, v in tree:
            if ck2parser.is_codename(n.val):
                if n.val in titles:
                    print('Duplicate title {}'.format(n.val))
                titles.add(n.val)
                if ('title' in v.dictionary and
                    'title_female' not in v.dictionary):
                    print('{} missing title_female'.format(n.val))
                if n.val.startswith('b_'):
                    titles_de_jure.add(n.val)
                    parent_is_titular = False
                else:
                    is_titular = recurse(v)
                    if not is_titular:
                        titles_de_jure.add(n.val)
                        parent_is_titular = False
        return parent_is_titular

    for path in ck2parser.files('common/landed_titles/*', *source_paths):
        recurse(ck2parser.parse_file(path))
    # print('{} titles, {} de jure'.format(len(titles), len(titles_de_jure)))
    return titles, titles_de_jure

def main():
    global modpath
    if len(sys.argv) > 1:
        modpath = pathlib.Path(sys.argv[1])
    titles, titles_de_jure = process_landed_titles()
    check_province_history(titles)
    bad_region_titles = check_regions(titles, titles_de_jure)
    for path in ck2parser.files('history/titles/*.txt', *source_paths):
        tree = ck2parser.parse_file(path)
        if tree.contents:
            good = check_title(path.stem, path, titles)
            if (not good and
                modpath not in path.parents and
                not (MINISWMH and minipath in path.parents)):
                newpath = modpath / 'history/titles' / path.name
                # newpath.open('w').close()
                print('Should override {} with blank file'.format(
                      '<vanilla>' / path.relative_to(vanilladir)))
            else:
                check_titles(path, titles)
    for _ in ck2parser.parse_files('history/characters/*.txt', modpath, minipath):
        pass # just parse it to see if it parses
    globs = [
        'events/*.txt',
        'decisions/*.txt',
        'common/laws/*.txt',
        'common/objectives/*.txt',
        'common/minor_titles/*.txt',
        'common/job_titles/*.txt',
        'common/job_actions/*.txt',
        'common/religious_titles/*.txt',
        'common/cb_types/*.txt',
        'common/scripted_triggers/*.txt',
        'common/scripted_effects/*.txt',
        'common/achievements.txt'
        ]
    for glob in globs:
        for path in ck2parser.files(glob, *source_paths):
            check_titles(path, titles)
    with (rootpath / 'check_titles.txt').open('w', encoding='cp1252') as fp:
        if bad_region_titles:
            print('Invalid or titular titles in regions:\n\t', end='', file=fp)
            print(*bad_region_titles, sep=' ', file=fp)
        for lhs in [True, False]:
            if results[lhs]:
                if lhs:
                    print('Undefined references as SCOPE:', file=fp)
                else:
                    print('Undefined references:', file=fp)
            for path, titles in sorted(results[lhs].items()):
                if titles:
                    if modpath in path.parents:
                        rel_path = '<mod>' / path.relative_to(modpath)
                    elif MINISWMH and minipath in path.parents:
                        rel_path = '<mod>' / path.relative_to(minipath)
                    else:
                        rel_path = '<vanilla>' / path.relative_to(vanilladir)
                    print('\t' + str(rel_path), *titles, sep='\n\t\t', file=fp)

if __name__ == '__main__':
    start_time = time.time()
    try:
        main()
    finally:
        end_time = time.time()
        print('Time: {:g} s'.format(end_time - start_time))
