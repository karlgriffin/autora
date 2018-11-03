#!/usr/bin/python
# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import codecs
import csv
import sys
import re
import time
import os
import logging
import config_file as config

logger = logging.getLogger(__name__)
datetime_stamp = str(time.strftime("%Y_%m_%d_%H%M_%S"))


class ProductChecker(object):

    def __init__(self):
        self.output_csv_header = True

    def check_and_create_dir(self, path):
        if not os.path.exists(path):
            logger.info("Creating directory: {0}".format(path))
            os.makedirs(path)

    def setup(self, output_name):
        self.output_dir = "{0}_{1}".format(output_name, datetime_stamp)
        self.check_and_create_dir(
            '../logs/{0}_{1}'.format(output_name, datetime_stamp))
        # format = '%(levelname)s:%(message)s'
        format = '%(message)s'
        if config.log_level['level'] == "info":
            log_level = logging.INFO
            print("Log level: INFO")
        elif config.log_level['level'] == "debug":
            log_level = logging.DEBUG
            print("Log level: DEBUG")
        else:
            log_level = logging.INFO
            print("Default - Log level: INFO")

        logging.basicConfig(
            format=format,
            filename="../logs/{0}_{1}/{0}_{1}.log".format(
                output_name, datetime_stamp), level=log_level)
        logger.debug(
            'Date and Time of operation: {0}\n'.format(str(time.strftime(
                "%Y_%m_%d_%H%M_%S"))))

    def chrome_setup(self, url):
        # check the operating system and select chrome driver
        if os.name == 'nt':
            os_driver = config.webdriver['windows']
        else:
            os_driver = config.webdriver['linux']
        logger.info("Chrome driver path: {}".format(os_driver))
        logger.debug("Current path: {}".format(os.getcwd()))
        if config.invisible['invisible_chrome'] == True:
            print('Running Headless Chrome\n')
            logger.info('Running Headless Chrome')
            chrome_options = Options()
            chrome_options.accept_untrusted_certs = True
            chrome_options.assume_untrusted_cert_issuer = True
            chrome_options.add_argument("--headless")
            driver = webdriver.Chrome(
                executable_path=os_driver,
                chrome_options=chrome_options)
        else:
            print('Running Chrome with GUI')
            logger.info('Running Chrome with GUI')
            driver = webdriver.Chrome(
                executable_path=os_driver)
        return driver

    def wait_for_text(self, driver, url, text):
        try:
            # load the url
            driver.get(url)
            try:
                # wait for the visible 'text' to appear
                WebDriverWait(
                    driver, 45).until(
                    EC.text_to_be_present_in_element((
                        By.XPATH, "//*"), text))
                logger.debug("Load successful")
            except:
                print("Login not confirmed")
                logger.error(
                    "Login Not Confirmed")
                sys.exit()
        except:
            print("Is this the correct url: {}".format(url))
            logger.error("Could not resolve URL: {}".format(url))

    def get_soup(self, html_string):
        try:
            soup = BeautifulSoup(html_string, 'html.parser')
            logger.debug('Created soup')
            return soup
        except:
            logger.error('Failed to create soup..')
            return None

    def write_headers(self, file_name):
        if self.output_csv_header:
            write_header = u'Search Term,Result,Amazon,Google\n'
            with open(file_name, 'a') as f:
                f.write(write_header)
            self.output_csv_header = False

    def amazon_search_for_item(self, driver, item_entry):
        self.wait_for_text(driver, config.amazon['url'], "Your Account")

        elem = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.ID, 'nav-shop')))
        elem.click()

        elem = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((
                By.LINK_TEXT, config.amazon['search_choice'])))
        elem.click()

        elem = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.ID, 'twotabsearchtextbox')))
        print(u"Amazon: '{}'".format(item_entry))
        logger.info(u"Amazon: '{}'".format(item_entry))
        elem.send_keys(u'{}'.format(item_entry))

        elem = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'nav-input')))
        elem.click()

        elem = driver.find_element_by_xpath("//*")
        html_string = elem.get_attribute("outerHTML")
        item_result_page = self.get_soup(html_string)

        try:
            no_result = item_result_page.find_all(
                'h1', {'id':'noResultsTitle'})
            return u"No result: {}".format(no_result[0].text)
        except:
            pass

        try:
            no_result = item_result_page.find_all(
                'div', {'id':'apsRedirectLink'})
            return u"No result: {}".format(no_result[0].text)
        except:
            pass

        try:
            result_department = item_result_page.find_all(
                'li', {'class':'s-ref-indent-one'})
            if len(result_department) == 0:
                return "Undetermined - Manual check needed"
        except:
            logger.error("Could not find results department")
            return "Undetermined - Manual check needed"

        if config.amazon['department'] == result_department[0].text:
            number_of_results = item_result_page.find_all(
                'span', {"id": "s-result-count"})
            result_details = u'{}'.format(number_of_results[0].text)
            result_details_formatted = re.findall(
                ur'^.+\:\s{0,}\n{0,}\".+\"', result_details)
            result_details_formatted = re.sub(
                ur'\n', u' ', result_details_formatted[0])
            return result_details_formatted
        else:
            return(
                u"'{}' is not: '{}'".format(
                    result_department[0].text, config.amazon['department']))

    def google_search_for_item(self, driver, item_entry):
        self.wait_for_text(driver, config.google['url'], "Advertising")
        elem = WebDriverWait(driver, 50).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'lst')))
        print(u"Google: '{}'".format(item_entry))
        logger.info(u"Google: '{}'".format(item_entry))
        elem.send_keys(u'{}'.format(item_entry))

        try:
            time.sleep(3)
            WebDriverWait(driver, 50).until(
                EC.presence_of_element_located((By.NAME, 'btnG'))).click()
        except:
            logger.error("Could not click on Google search button")
            return 'Undetermined - Manual check needed*'

        elem = driver.find_element_by_xpath("//*")
        html_string = elem.get_attribute("outerHTML")
        item_result_page = self.get_soup(html_string)

        try:
            no_result = item_result_page.find_all(
                'div', {'class':'xHpZgd mnr-c'})
            return u"No result: {}".format(no_result[0].text)
        except:
            pass

        result_div = item_result_page.find_all(
            'div', {'class': 'sh-pr__product-results'})
        result_div_obj = result_div[0]
        result_entries = result_div_obj.find_all(
            'div', {'class': 'sh-dlr__list-result'})
        logger.info("Google result entries: {}".format(len(result_entries)))

        count = 1
        result = u''
        try:
            for entry in result_entries:
                logger.debug("count: {}".format(count))
                if count <= config.google['return_hits']:
                    name = entry.find_all('div', {'class': 'eIuuYe'})
                    cost = entry.find_all('div', {'class': 'mQ35Be'})
                    result +=  u"({} {}  )".format(name[0].text, cost[0].text)
                    count += 1
                else:
                    logger.debug("Count {} reached breaking loop".format(count))
                    break
            return result
        except:
            return 'Undetermined - Manual check needed**'

    def results_csv(self, item_entry, amazon_result, google_result):
        logger.info(u"Amazon result original: '{}'".format(amazon_result))
        logger.info(u"Google result original: '{}'".format(google_result))
        self.check_and_create_dir('../reports/')
        file_name = ur'../reports/{}_{}.csv'.format(
            config.output_csv['name'], datetime_stamp)
        # write csv output headings
        self.write_headers(file_name)
        # remove ',' from item
        item_entry = re.sub(",", "", item_entry)
        # remove ',' from results
        amazon_result = re.sub(",", "", amazon_result)
        google_result = re.sub(",", "", google_result)
        # pattern to check amazon result for hit numbers
        amazon_hit_pattern = re.findall(ur'[1-9]{1,}', amazon_result)
        google_hit_pattern = re.findall(ur'[1-9]{1,}', google_result)
        logger.info(u"Amazon result modified: '{}'".format(amazon_result))
        logger.info(u"Google result modified: '{}'".format(google_result))
        logger.info(u"Amazon hit pattern result: {}".format(
            amazon_hit_pattern))
        logger.info(u"Google hit pattern result: {}".format(
            google_hit_pattern))
        # if both hits are 1 or more
        if (len(amazon_hit_pattern)) and (len(google_hit_pattern)) >= 1:
            write_string = u"{},Hits,{},{}\n".format(
                item_entry, amazon_result, google_result)
        # if either hits are 1 or more
        elif (len(amazon_hit_pattern)) or (len(google_hit_pattern)) >= 1:
            write_string = u"{},Hit,{},{}\n".format(
                item_entry, amazon_result, google_result)
        # if no hits
        else:
            write_string = u"{},,{},{}\n".format(
                item_entry, amazon_result, google_result)
        # write the entry to the output csv file
        logger.info(u"writing to csv: {}".format(write_string))
        with codecs.open(file_name, 'a') as f:
            f.write(write_string.encode("utf8"))

    def open_items_csv(self, driver, csv_file_name):
        alias_row_dict = {}
        row_number = 1
        csv_path = '../inputs/{}.csv'.format(csv_file_name)
        csv_dict = csv.DictReader(open("{}".format(csv_path)))
        logger.info(u"Alias csv header: '{}'".format(config.alias['name']))
        # loop each row of the input csv file
        for row in csv_dict:
            logger.debug(u"Dict row: {}".format(row))
            # get the row number, alias value and add it to a dictionary
            alias_row_dict[row_number] = row[config.alias['name']]
            # Increase the number by 1 for next loop
            row_number += 1
        logger.info(u"Using these entries: {}".format(alias_row_dict))
        logger.info("")

        with open(csv_path, 'rb') as csvfile:
            alias_num = 1
            readCSV = csv.reader(csvfile, delimiter=',')
            current_row = 0
            for row in readCSV:
                # Skip the header row
                if current_row == 0:
                    pass
                else:
                    for item_entry in row:
                        # skip empty cells
                        if item_entry == '':
                            pass
                        elif item_entry == alias_row_dict[alias_num]:
                            # skip the alias entry
                            pass
                        else:
                            item_entry = u"{} {}".format(
                                alias_row_dict[alias_num], item_entry)
                            # logger.info(u"Item Entry: {}".format(item_entry))
                            amazon_result = self.amazon_search_for_item(
                                driver, item_entry)
                            google_result = self.google_search_for_item(
                                driver, item_entry)
                            logger.info(amazon_result)
                            self.results_csv(
                                item_entry, amazon_result, google_result)
                            logger.info("")
                    alias_num += 1
                current_row += 1

    def main(self):
        # Get url from config file
        url = config.amazon['url']
        # Get output folder name from config file
        output_name = config.folder_name['name']
        # Create output directory and log file
        self.setup(output_name)
        # Open Chrome and load the url
        driver = self.chrome_setup(url)
        # Read the input csv from config and
        # loop through the data as searches
        self.open_items_csv(driver, config.input_csv['name'])

ProductChecker().main()