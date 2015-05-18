# -*- coding: utf-8 -*-
__author__ = 'Stanislav Filin'
from bs4 import BeautifulSoup
import requests
import sqlite3


class Scrapping:
    def __init__(self, url):
        self.url = url
        self.PARSE_BASE = {}
        self.page = 1

        print "\t===\tStart Scraping\t==="

    def parse(self, url=None):
        if not url:
            url = self.url
        print "\t -\t" + str(self.page) + " page"
        response = requests.get(url)
        soup = BeautifulSoup(response.text)
        div_element_list = soup.find_all('div', {'class': 'g-i-tile-i-title clearfix'})
        for div_element in div_element_list:
            element_name = div_element.find('a').getText().rstrip('\t\n').lstrip('\t\n')
            element_url = div_element.find('a').get('href')

            response_element = requests.get(element_url)
            soup_element = BeautifulSoup(response_element.text)
            if soup_element.find('span', {'itemprop': 'price'}):
                element_money = soup_element.find('span',
                                                  {'itemprop': 'price'}
                                                  ).getText().rstrip('\t\n').lstrip('\t\n')
            elif soup_element.find('meta', {'itemprop': 'priceCurrency'}):
                element_money = soup_element.find('meta',
                                                  {'itemprop': 'priceCurrency'}
                                                  ).getText().rstrip('\t\n').lstrip('\t\n')
            else:
                element_money = "None"
            if soup_element.find('div', {'class': 'detail-description'}):
                element_description = soup_element.find('div',
                                                        {'class': 'detail-description'}
                                                        ).getText().rstrip('\t\n').lstrip('\t\n')
            else:
                element_description = "None"
            if soup_element.find('a', {'class': 'responsive-img'}):
                element_img = soup_element.find('a',
                                                {'class': 'responsive-img'}
                                                ).get('href').rstrip('\t\n').lstrip('\t\n')
            else:
                element_img = "None"
            self.PARSE_BASE[element_name] = {
                'url': element_url,
                'money': element_money,
                'description': element_description,
                'img': element_img
            }

        if div_element_list:
            self.page += 1
            next_url = self.url + "page="+str(self.page) + "/"
            self.parse(next_url)
        else:
            return self.PARSE_BASE

    def export_sqlite(self, name):
        conn = sqlite3.connect('scraping.db')
        c = conn.cursor()
        c.execute("CREATE TABLE " + unicode(name) + " (name text, link text, money text, description text, img text)")
        for element in self.PARSE_BASE:
            c.execute("INSERT INTO " + unicode(name) + " VALUES ('" +
                      unicode(element) + "', '" +
                      unicode(self.PARSE_BASE[element]['url']) + "', '" +
                      unicode(self.PARSE_BASE[element]['money']) +"', '" +
                      unicode(self.PARSE_BASE[element]['description']) + "', '" +
                      unicode(self.PARSE_BASE[element]['img']) + "')"
                      )
        conn.commit()
        conn.close()

URL_LINK = "http://rozetka.com.ua/notebooks/c80004/filter/"
scrap = Scrapping(URL_LINK)
scrap.parse()
scrap.export_sqlite('notebooks')