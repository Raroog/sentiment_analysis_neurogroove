#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import lxml
import re
from datetime import datetime


# generates lists of links to the URLs with trip raport lists

def func_URL_generator(URL="https://www.neurogroove.info/raporty?page="):
    URL_list = ["https://www.neurogroove.info/raporty"]
    for i in range(1, 64):
        URL_list.append(f"{URL}{i}")
    yield from URL_list




# returns list of links to trip reports based on URL trip raport lists

def link_to_scrape_generator(URL):
    trip_URLs = []
    soup = BeautifulSoup(requests.get(URL).text, 'lxml')
    for link in soup.find_all("a"):
        temp_link = link.get('href')
        if temp_link is not None and temp_link.startswith("trip/"):
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
        for i in range(6):
            splitted = details_soup[i].text.split(":", maxsplit=1)
            details[splitted[0]] = splitted[1]
        details["Title"] = details_soup[6].text.strip()
        return details

    # returns more basic data[date of trip report submission and nick]

    def date_nick_scraper(self):

        date_nick = {}
        date_nick_soup = self.soup.select(".submitted")[0].text.strip().split(",", maxsplit=1)
        time_numbers = datetime.strptime(re.sub('[^0-9]+', '', date_nick_soup[1]), '%d%m%Y%H%M')
        date_nick["Nick"] = date_nick_soup[0]
        date_nick["Time"] = time_numbers.year

        return date_nick

    # returns content of trip report

    def trip_raport_scraper(self):

        trip_raport_soup = self.soup.find_all('p')
        trip_raport_text = []
        for i in range(1, len(self.soup.find_all('p'))):
            paragraph = trip_raport_soup[i].text
            trip_raport_text.append(paragraph)
        return "".join(trip_raport_text)


# assigning generator to a variable
URL_generator = func_URL_generator()

# passing as argument first list of generated links
link_to_scrape_generator(next(URL_generator))


for url in range(2):
    print(link_to_scrape_generator(next(URL_generator)))


