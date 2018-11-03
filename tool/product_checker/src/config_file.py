#!/usr/bin/python
# -*- coding: utf-8 -*-

invisible = {'invisible_chrome': True}  # True / False

log_level = {"level": "info"}  # info / debug

webdriver = {'windows':'..\webdriver\chromedriver.exe',
             'linux': '..\webdriver\linux_chromedriver'
             }

amazon = {'url': 'https://www.amazon.co.uk',  # enter the amazon url site region
          'search_choice': 'All Beauty',  # selected from "Shop by Department"
          'department': 'Beauty'  # desired department on page results
          }

google = {'url': 'https://www.google.com/shopping', # google url
          'return_hits': 3  # number of entries to record
          }

alias = {"name": "Alias"}  # header name for all the aliases

input_csv = {'name': 'beauty_searches'}  # input csv file name without file extension

folder_name = {'name': 'amazon'}  # output folder name

output_csv = {'name': 'beauty_search_results'}  # output csv file name without file extension


