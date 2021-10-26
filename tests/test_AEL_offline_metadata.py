#!/usr/bin/python -B
# -*- coding: utf-8 -*-

# Test AEL Offline metadata scraper.
# First time a platform is used the XML database is loaded and cached for subsequent
# calls until the scraper object is destroyed or the platform is changed.

# --- Python standard library ---
from __future__ import unicode_literals
import os
import pprint
import sys

# --- AEL modules ---
if __name__ == "__main__" and __package__ is None:
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    print('Adding to sys.path {}'.format(path))
    sys.path.append(path)
from resources.scrap import *
from resources.utils import *
import common

# --- main ---------------------------------------------------------------------------------------
print('*** Fetching candidate game list ********************************************************')
set_log_level(LOG_DEBUG)

# Set addon dir
common.settings['scraper_aeloffline_addon_code_dir'] = path
print('Setting scraper_aeloffline_addon_code_dir = "{}"'.format(path))

# --- Create scraper object ---
scraper_obj = AEL_Offline(common.settings)
scraper_obj.set_verbose_mode(False)
scraper_obj.set_debug_file_dump(True, os.path.join(os.path.dirname(__file__), 'assets'))
status_dic = kodi_new_status_dic('Scraper test was OK')

# --- Get candidates non-MAME ---
# search_term, rombase, platform = common.games['metroid']
# search_term, rombase, platform = common.games['mworld']
search_term, rombase, platform = common.games['sonic_megaDrive']
# search_term, rombase, platform = common.games['sonic_genesis'] # Aliased platform
# search_term, rombase, platform = common.games['chakan']
# search_term, rombase, platform = common.games['console_wrong_title']
# search_term, rombase, platform = common.games['console_wrong_platform']

# --- Get candidates MAME ---
# search_term, rombase, platform = common.games['atetris']
# search_term, rombase, platform = common.games['mslug']
# search_term, rombase, platform = common.games['dino']
# search_term, rombase, platform = common.games['MAME_wrong_title']
# search_term, rombase, platform = common.games['MAME_wrong_platform']

# --- Get candidates, print them and set first candidate ---
rom_FN = FileName(rombase)
rom_checksums_FN = FileName(rombase)
if scraper_obj.check_candidates_cache(rom_FN, platform):
    print('>>>> Game "{}" "{}" in disk cache.'.format(rom_FN.getBase(), platform))
else:
    print('>>>> Game "{}" "{}" not in disk cache.'.format(rom_FN.getBase(), platform))
candidate_list = scraper_obj.get_candidates(search_term, rom_FN, rom_checksums_FN, platform, status_dic)
# pprint.pprint(candidate_list)
common.handle_get_candidates(candidate_list, status_dic)
print_candidate_list(candidate_list)
scraper_obj.set_candidate(rom_FN, platform, candidate_list[0])

# --- Print metadata of first candidate ----------------------------------------------------------
print('*** Fetching game metadata **************************************************************')
metadata = scraper_obj.get_metadata(status_dic)
# pprint.pprint(metadata)
print_game_metadata(metadata)
scraper_obj.flush_disk_cache()
