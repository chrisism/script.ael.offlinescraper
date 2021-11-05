#!/usr/bin/python -B
# -*- coding: utf-8 -*-

# Test AEL Offline metadata scraper.
# First time a platform is used the XML database is loaded and cached for subsequent
# calls until the scraper object is destroyed or the platform is changed.

# --- Python standard library ---
from __future__ import unicode_literals
import os
import unittest
import unittest.mock
from unittest.mock import patch, MagicMock
import logging

logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.DEBUG)
logger = logging.getLogger(__name__)

from resources.lib.scraper import AEL_Offline_Scraper
from ael.utils import kodi, io
from ael.api import ROMObj

# --- Test data -----------------------------------------------------------------------------------
games = {
    # Console games
    'metroid'                : ('Metroid', 'Metroid.zip', 'Nintendo SNES'),
    'mworld'                 : ('Super Mario World', 'Super Mario World.zip', 'Nintendo SNES'),
    'sonic_megaDrive'        : ('Sonic the Hedgehog', 'Sonic the Hedgehog (USA, Europe).zip', 'Sega Mega Drive'),
    'sonic_genesis'          : ('Sonic the Hedgehog', 'Sonic the Hedgehog (USA, Europe).zip', 'Sega Genesis'),
    'chakan'                 : ('Chakan', 'Chakan (USA, Europe).zip', 'Sega MegaDrive'),
    'ff7'                    : ('Final Fantasy VII', 'Final Fantasy VII (USA) (Disc 1).iso', 'Sony PlayStation'),
    'console_wrong_title'    : ('Console invalid game', 'mjhyewqr.zip', 'Sega MegaDrive'),
    'console_wrong_platform' : ('Sonic the Hedgehog', 'Sonic the Hedgehog (USA, Europe).zip', 'mjhyewqr'),

    # MAME games
    'atetris'             : ('Tetris (set 1)', 'atetris.zip', 'MAME'),
    'mslug'               : ('Metal Slug - Super Vehicle-001', 'mslug.zip', 'MAME'),
    'dino'                : ('Cadillacs and Dinosaurs (World 930201)', 'dino.zip', 'MAME'),
    'MAME_wrong_title'    : ('MAME invalid game', 'mjhyewqr.zip', 'MAME'),
    'MAME_wrong_platform' : ('Tetris (set 1)', 'atetris.zip', 'mjhyewqr'),
}


class Test_offline_metadata(unittest.TestCase):
    
    ROOT_DIR = ''
    TEST_DIR = ''
    TEST_ASSETS_DIR = ''
    TEST_OUTPUT_DIR = ''

    @classmethod
    def setUpClass(cls):        
        cls.TEST_DIR = os.path.dirname(os.path.abspath(__file__))
        cls.ROOT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR, os.pardir))
        cls.TEST_ASSETS_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'assets/'))
        cls.TEST_OUTPUT_DIR = os.path.abspath(os.path.join(cls.TEST_DIR,'output/'))
                
        print('ROOT DIR: {}'.format(cls.ROOT_DIR))
        print('TEST DIR: {}'.format(cls.TEST_DIR))
        print('TEST ASSETS DIR: {}'.format(cls.TEST_ASSETS_DIR))
        print('TEST OUTPUT DIR: {}'.format(cls.TEST_OUTPUT_DIR))
        print('---------------------------------------------------------------------------')
    
    
    @patch('resources.lib.scraper.kodi.getAddonDir')
    def test_offline_metdata(self, addon_dir_mock: MagicMock):         
        
        addon_dir_mock.return_value = io.FileName(self.ROOT_DIR)
        #settings_mock.side_effect = lambda key: self.TEST_OUTPUT_DIR if key == 'scraper_cache_dir' else ''
        #settings_mock.side_effect = lambda key: self.TEST_ASSETS_DIR if key == 'scraper_aeloffline_addon_code_dir' else ''
        
        # --- main ---------------------------------------------------------------------------------------
        print('*** Fetching candidate game list ********************************************************')

        # Set addon dir
        print('Setting scraper_aeloffline_addon_code_dir = "{}"'.format(self.TEST_ASSETS_DIR))

        # --- Create scraper object ---
        scraper_obj = AEL_Offline_Scraper()
        scraper_obj.set_verbose_mode(False)
        scraper_obj.set_debug_file_dump(True, self.TEST_OUTPUT_DIR)
        status_dic = kodi.new_status_dic('Scraper test was OK')

        # --- Get candidates non-MAME ---
        # search_term, rombase, platform = common.games['metroid']
        # search_term, rombase, platform = common.games['mworld']
        search_term, rombase, platform = games['sonic_megaDrive']
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
        rom_FN = io.FileName(rombase)
        rom = ROMObj({
            'platform': platform,
            'scanned_data': { 'file': rombase, 'identifier': rom_FN.getBaseNoExt() }
        })
        
        if scraper_obj.check_candidates_cache(rom.get_identifier(), platform):
            print('>>>> Game "{}" "{}" in disk cache.'.format(rom.get_identifier(), platform))
        else:
            print('>>>> Game "{}" "{}" not in disk cache.'.format(rom.get_identifier(), platform))
        candidate_list = scraper_obj.get_candidates(search_term, rom, platform, status_dic)
        # pprint.pprint(candidate_list)
        self.assertTrue(status_dic['status'], 'Status error "{}"'.format(status_dic['msg']))
        self.assertIsNotNone(candidate_list, 'Error/exception in get_candidates()')
        self.assertNotEquals(len(candidate_list), 0, 'No candidates found.')
            
        for candidate in candidate_list:
            print(candidate)
            
        scraper_obj.set_candidate(rom.get_identifier(), platform, candidate_list[0])

        # --- Print metadata of first candidate ----------------------------------------------------------
        print('*** Fetching game metadata **************************************************************')
        metadata = scraper_obj.get_metadata(status_dic)
        # pprint.pprint(metadata)
        print(metadata)
        scraper_obj.flush_disk_cache()
