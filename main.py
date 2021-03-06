#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import lxml
import re
from datetime import datetime
import csv
import time


# generates lists of links to the URLs with trip raport lists

def func_URL_generator(URL="https://www.neurogroove.info/raporty?page="):
    URL_list = ["https://www.neurogroove.info/raporty"]
    for i in range(1, 65):
        URL_list.append(f"{URL}{i}")
    return URL_list


# returns list of links to trip reports based on URL trip raport lists

def link_to_scrape_generator(URLs):
    trip_URLs = []
    for URL in URLs:
        soup = BeautifulSoup(requests.get(URL).text, 'lxml')
        for link in soup.find_all("a"):
            temp_link = link.get('href')
            if temp_link is not None and temp_link.startswith("/trip/"):
                trip_URLs.append(f'https://www.neurogroove.info/{temp_link}')

    return trip_URLs


# class taking URL from neurogroove and parsing it, each method returns dictionaries with data

class NeurogrooveScraper():

    def __init__(self, URL):
        self.URL = URL
        self.soup = BeautifulSoup(requests.get(URL).text, 'lxml')

    # returns basic data[main substance, dosage, type of experience, set & setting, age, previous experience, title]

    def details_scraper(self):

        details_soup = self.soup.select(".views-field")
        details = {}
        try:
            for i in details_soup[:9]:
                splitted = i.text.split(":", maxsplit=1)
                details[splitted[0]] = splitted[1]
        except IndexError:
            return details
        return details

    # returns more basic data[date of trip report submission and nick]

    def date_nick_scraper(self):

        date_nick = {}
        date_nick_soup = self.soup.select(".submitted")[0].text.strip().split(",", maxsplit=1)
        time_numbers = datetime.strptime(re.sub('[^0-9]+', '', date_nick_soup[1]), '%d%m%Y%H%M')
        date_nick["Nick"] = date_nick_soup[0]
        date_nick["Time"] = time_numbers

        return date_nick

    # returns content of trip report

    def trip_raport_scraper(self):
        trip_text_dict = dict()
        trip_raport_soup = self.soup.find_all('p')
        trip_raport_text = []
        for i in trip_raport_soup[1:]:
            paragraph = i.text
            trip_raport_text.append(paragraph)
            trip_text_dict["Content"] = "".join(trip_raport_text)
        return trip_text_dict


# changing the format from dictionaries to CSV


def data_to_CSV(URL_list):
    with open('Trip_reports2.csv', 'w', newline='') as csvfile:
        fieldnames = [' Substancja wiod??ca', ' Natura', ' Chemia', ' Apteka', ' Dawkowanie',
                      ' Rodzaj prze??ycia', ' Set&Setting', ' Do??wiadczenie', ' Wiek', 'Nick', 'Time', 'Content']

        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, restval=None, extrasaction='ignore')
        writer.writeheader()

        scraper = (NeurogrooveScraper(URL)
        for URL in URL_list:
            temp_dict = dict()
            temp_dict.update(scraper.details_scraper())
            temp_dict.update(scraper.date_nick_scraper())
            temp_dict.update(scraper.trip_raport_scraper())
            writer.writerow(temp_dict)


start = time.time()
if __name__ == '__main__':
    data_to_CSV(link_to_scrape_generator(func_URL_generator()))
end = time.time()
print("Time elapsed: ", end - start)
