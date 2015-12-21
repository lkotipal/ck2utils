#!/usr/bin/env python3

import re
import time
import ck2parser

rootpath = ck2parser.rootpath
modpath = rootpath / 'SWMH-BETA/SWMH'

def process_landed_titles(where, prov_title):
    def recurse(tree):
        for n, v in tree:
            if re.match('c_', n.val):
                yield n.val
            elif re.match('[ekd]_', n.val):
                de_jure_counties = tuple(recurse(v))
                try:
                    cap_prov = v['capital'].val
                    try:
                        cap_title = prov_title[cap_prov]
                        if (de_jure_counties and
                            cap_title not in de_jure_counties):
                            print('Title {} capital {} ({}) is not de jure'
                                  .format(n.val, cap_title, cap_prov))
                    except KeyError:
                        print('Title {} has invalid capital {}'
                              .format(n.val, cap_prov))
                except KeyError:
                    print('Title {} missing a capital'.format(n.val))
                yield from de_jure_counties

    for _, tree in ck2parser.parse_files('common/landed_titles/*', modpath):
        for _ in recurse(tree):
            pass

def main():
    start_time = time.time()

    province_title = {prov: title
                      for prov, title, _ in ck2parser.provinces(modpath)}
    process_landed_titles(modpath, province_title)

    end_time = time.time()
    print('Time: {} s'.format(end_time - start_time))

if __name__ == '__main__':
    main()