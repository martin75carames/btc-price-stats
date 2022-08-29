#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
analyse bitcoin price from CSV data based on blockchain.info's data (not 100% accurate, especially before 2010)
"""

# from __future__ import print_function
import datetime
import sys

import certifi
import urllib3
urllib3.disable_warnings()

import urllib3.contrib.pyopenssl
urllib3.contrib.pyopenssl.inject_into_urllib3()

import statistics as stats
from typing import List, AnyStr, Dict

# ---------------------------------------------------
# from bs4 import BeautifulSoup
# import urllib2
#
# url = 'http://www.thefamouspeople.com/singers.php'
# html = urllib2.urlopen(url)
# soup = BeautifulSoup(html)

# ---------------------------------------------------

# from bs4 import BeautifulSoup
# import urllib3
#
# http = urllib3.PoolManager()
#
# url = 'http://www.thefamouspeople.com/singers.php'
# response = http.request('GET', url)
# soup = BeautifulSoup(response.data)
# ---------------------------------------------------


def get_remote_data(url):

    # s = urllib2.urlopen(url).read()

    http_pm = urllib3.PoolManager(cert_reqs='CERT_REQUIRED',
                                  ca_certs=certifi.where())

    remote_response = http_pm.request('GET', url)

    date_str = str(datetime.datetime.now()).split()[0]

    local_file = 'btc-price-' + date_str + '.csv'

    with open(local_file, 'w') as data_file:
        data_file.write(remote_response.data.decode('utf-8'))

    return local_file


def get_local_data(local_file) -> List[AnyStr]:

    with open(local_file, 'r') as data_file:
        lines = data_file.readlines()

    return lines


def add_year_metadata(data_by_year):

    print('Average by Year')
    print('---------------\n')

    for year in sorted(data_by_year.keys()):

        year_prices = data_by_year[year][1]
        year_avg = stats.mean(year_prices)

        ratio = 0
        if year > 2009:
            last_year = max(y for y in data_by_year.keys() if y < year)
            if data_by_year[last_year][0] > 0:
                ratio = year_avg / data_by_year[last_year][0]

        data_by_year[year] = (year_avg, year_prices, ratio)

        increase = int(100 * (ratio - 1 if ratio > 0 else ratio))

        print('\t%s - OPEN %8s  --  CLOSE %8s\n' % (year, year_prices[0], year_prices[-1]))

        print('\t       Annual-AVG  %8s  --  Increase %6s%%\n' % (round(year_avg, 3), increase))
        print('\t       Prices: %s' % year_prices)
        print('\t       Points  %3s\n\n' % len(year_prices))

    return data_by_year


def parse_csv_contents(btc_prices_csv_lines):

    price_date     = None
    first_day      = None
    data_points_nr = 0
    sum_prices     = 0

    data_by_year = {
                        2009: (0, list(), 0),
                        2010: (0, list(), 0),
                        2011: (0, list(), 0),
                        2012: (0, list(), 0),
                        2013: (0, list(), 0),
                        2014: (0, list(), 0),
                        2015: (0, list(), 0),
                        2016: (0, list(), 0),
                        2017: (0, list(), 0),
                        2018: (0, list(), 0),
                        2019: (0, list(), 0),
                        2020: (0, list(), 0)
                    }                           # type: Dict[int]

    for i, line in enumerate(btc_prices_csv_lines[:]):

        if i == 0:
            # print('line 0: %s' % line)

            title_date, title_price = line.split(',')
            continue

        price, price_date, year = parse_csv_line(line)

        if first_day is None:
            first_day = price_date

        # print('by years: %s' % data_by_year.keys())
        # print('year: %s' % year)

        if year in data_by_year.keys():
            prices = data_by_year[year][1]

            # print('year: %s - prices: %s' % (year, prices))

            prices.append(price)
            data_by_year[year] = (None, prices, None)

        else:
            raise

        sum_prices += float(price)
        data_points_nr += 1

    last_day = price_date

    return data_by_year, data_points_nr, sum_prices, first_day, last_day


def parse_csv_line(line: str) -> (float, datetime, int):

    # print("Line: [%s]" % line)

    line = line.replace('\n', '')

    # print("Line: [%s]" % line)

    date_str, price = line.split(',')

    price = round(float(price), 1)

    # print("d: %s  --  p: %7s" % (date_str, price))

    year_str, month_str, daytime_str = date_str.split('-')
    day_str, time_str = daytime_str.split(' ') if ' ' in daytime_str else (daytime_str, '00:00:00')

    year = int(year_str)
    date = datetime.date(year, int(month_str), int(day_str))

    # print('date, price: (%s, %s)' % (date, price))

    return price, date, year


def get_biannual_metadata(data_by_year):

    biannual_data_by_year = \
            {2009: (0, list(), 0), 2010: (0, list(), 0), 2011: (0, list(), 0), 2012: (0, list(), 0),
             2013: (0, list(), 0), 2014: (0, list(), 0), 2015: (0, list(), 0), 2016: (0, list(), 0),
             2017: (0, list(), 0), 2018: (0, list(), 0), 2019: (0, list(), 0)}

    print('Biannual Averages by Year')
    print('-------------------------\n')

    for year in sorted(data_by_year.keys())[0:-1]:

        biannual_prices =   data_by_year[year  ][1] \
                          + data_by_year[year+1][1]

        biannual_avg = stats.mean(biannual_prices)

        ratio = 0
        if year > 2009:

            prev_year = max(y for y in biannual_data_by_year.keys() if y < year)

            if biannual_data_by_year[prev_year][0] > 0:
                ratio = biannual_avg / biannual_data_by_year[prev_year][0]

        biannual_data_by_year[year] = (biannual_avg, biannual_prices, ratio)

    return biannual_data_by_year


def main(local_file: str, shell_args: List[str]) -> None:

    print('\n\n** BTC price information **\n\n')

    btc_prices_csv_lines = get_local_data(local_file)

    data_by_year,                   \
        data_points_nr, sum_prices, \
        first_day, last_day         = parse_csv_contents(btc_prices_csv_lines)

    data_by_year = add_year_metadata(data_by_year)

    biannual_data_by_year = get_biannual_metadata(data_by_year)

    for year in sorted(data_by_year.keys())[0:-1]:

        biannual_avg = biannual_data_by_year[year][0]
        biannual_prices = biannual_data_by_year[year][1]
        ratio = biannual_data_by_year[year][2]

        increase = round(100 * (ratio - 1 if ratio > 0 else ratio), 1)

        print('\t%s - OPEN %8s  --  CLOSE %8s\n'                 % (year, biannual_prices[0], biannual_prices[-1]))
        print('\t       BiAnnual-AVG  %8s  --  Increase %6s%%\n' % (round(biannual_avg, 3), increase))
        print('\t       Prices: %s'                              % biannual_prices)
        print('\t       Points  %3s\n\n'                         % len(biannual_prices))

    print('----------------------------------------------------------------------------------------------------\n')

    print('\nPERIOD:\t[ %s  -->  %s ]\n' % (first_day, last_day or '--'))

    print('DAYS:          \t%s\n' % (last_day - first_day).days)
    print('DATA-POINTS:   \t%s\n' % data_points_nr)

    global_avg = sum_prices / float(data_points_nr)
    global_avg_view = round(global_avg, 2) if global_avg < 100 else int(global_avg)

    annual_averages = [round(data_by_year[year][0], 2)       if (data_by_year[year][0] < 100) else int(data_by_year[year][0]) for year in sorted(data_by_year.keys())]
    a_growth_rates  = [(int(100 * (data_by_year[year][2] - 1 if  data_by_year[year][2] > 0    else data_by_year[year][2])))   for year in sorted(data_by_year.keys())]

    biannual_averages = [round(biannual_data_by_year[year][0], 2)       if (biannual_data_by_year[year][0] < 100) else int(biannual_data_by_year[year][0]) for year in sorted(biannual_data_by_year.keys())[0:]]
    ba_growth_rates   = [(int(100 * (biannual_data_by_year[year][2] - 1 if  biannual_data_by_year[year][2] > 0    else biannual_data_by_year[year][2])))   for year in sorted(biannual_data_by_year.keys())[0:]]

    compound_annual_growth_rate = (annual_averages[-1] ** (1 / float(len(a_growth_rates)) )) - 1
    cagr_view = int(round(compound_annual_growth_rate, 2) * 100)

    print('Global Avg Price:            %6s'     % global_avg_view)
    print('Compound Annual Growth Rate: %6s%%  (%s --> %s)\n' % (cagr_view, first_day, last_day) )

    print('\n--------------------------------------------------\n')

    print('YEAR:            ', end='')
    for year in sorted(data_by_year.keys()):
        print('\t%10s' % year, end='')
    print()

    print('ANNUAL AVG:      ', end='')
    for avg in annual_averages:
        print('\t%10s' % avg,  end='')
    print()

    print('ANNUAL GROWTH:   ', end='')
    for a_growth_rate in a_growth_rates:
        print('\t%10s%%' % a_growth_rate, end='')
    print('\n')

    print('BIANNUAL AVG:    ', end='')
    for biannual_average in biannual_averages:
        print('\t%10s' % biannual_average,  end='')
    print()

    print('BIANNUAL GROWTH: ', end='')
    for ba_growth_rate in ba_growth_rates:
        print('\t%10s%%' % ba_growth_rate, end='')
    print('\n')

    print('----------------------------------------------------------------------------------------------------\n')

# ------------------------------------------------------------------------------------------
# -- M A I N   S E C T I O N
# ------------------------------------------------------------------------------------------

local_file_1 = 'btc-data-sept.csv'
local_file_2 = 'btc-price-sep-2018.csv'
local_file_3 = 'btc-price-nov-2018.csv'
local_file_4 = 'btc-price-dic-2018.csv'
local_file_5 = 'btc-price-apr-2019.csv'
local_file_6 = 'btc-price-13-june-2019.csv'
local_file_7 = 'btc-com--btc-price-2020-01-07.csv'
local_file_8 = 'data-points/btc-com--btc-price-2020-04-17--range-all.csv'

btc_prices_bitcoin_com_url     = "https://charts.bitcoin.com/btc/chart/price"
btc_prices_blockchain_info_url = "https://blockchain.info/charts/market-price?showDataPoints=false&timespan=all&show_header=true&daysAverageString=1&scale=0&format=csv&address="

if __name__ == "__main__":

    config_get = False

    if config_get:

        btc_prices_url = btc_prices_blockchain_info_url
        data_file = get_remote_data(btc_prices_url)

    else:
        data_file = local_file_8

    main(data_file, sys.argv[:])

