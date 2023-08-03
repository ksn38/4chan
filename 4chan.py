from collections import OrderedDict, Counter
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import asyncio
import time
from datetime import date


today = str(date.today())

async def parser(section):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
    t_dict = OrderedDict()

    url = 'https://boards.4chan.org/' + section + '/'
    flags = []

    for i in range(90):
        response = requests.get(url, headers=headers).text
        parsed_html = bs(response, 'lxml')
        t = parsed_html.find_all('span', {'class': 'flag'})

        for i in t:
            flags.append(str(i).split('"')[3])
        await asyncio.sleep(300)
        
    countries = pd.read_csv('data/countries.csv')
    countries_2021 = countries[['Country Name', '2021']]
    countries_4chan = pd.DataFrame(Counter(flags).items(), columns=["Country Name", "num"])
    out = pd.merge(countries_4chan, countries_2021, how='left', on='Country Name')
    out['res'] = out['num']/out['2021']
    out.drop("2021", axis=1, inplace=True)
    out.sort_values(by=['res'], ascending=False).to_csv('data/' + section + '/' + today + '.csv', index=False, encoding='utf-8')


ioloop = asyncio.get_event_loop()
tasks = [
    ioloop.create_task(parser('int')),
    ioloop.create_task(parser('pol'))
]
ioloop.run_until_complete(asyncio.wait(tasks))
ioloop.close()
