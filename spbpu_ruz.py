import requests
from bs4 import BeautifulSoup
import re
import datetime

class Lesson:
    def __init__(self, name, time, type, groups, teacher, place):
        self.name = name
        self.time = time
        self.type = type
        self.groups = groups
        self.teacher = teacher
        self.place = place
    
    def __repr__(self):
        return self.name + ' at ' + self.time

def getRuz(date=''):
    if date:
        date = '?date=' + date
    s = requests.Session()
    with open('111.htm', 'w') as data:
        x = s.get('https://ruz.spbstu.ru/faculty/94/groups/34295' + date)
        data.write(x.content.decode('cp1251', errors='ignore'))

    with open('111.htm', 'r', encoding='cp1251', errors='ignore') as data:
        x = ''.join(data.readlines()).encode('cp1251', errors='ignore').decode('utf8', errors='ignore')
    ruz = []
    soup = BeautifulSoup(x, 'html.parser')
    week = soup.find_all('li', attrs={'class': 'schedule__day'})
    for day in week:
        daysoup = BeautifulSoup(str(day), 'html.parser')
        rday = []
        #daysoup.find('div').contents[0] # date
        dayofweek = 0
        for lesson in daysoup.find_all('li', attrs={'class': 'lesson'}):
            less = Lesson(*[None]*6)
            lessonsoup = BeautifulSoup(str(lesson), 'html.parser')
            for attr in lessonsoup.find_all('li'):
                attrsoup = BeautifulSoup(str(attr), 'html.parser')
                for div in attrsoup.find_all('div', attrs={'class': 'lesson__subject'}):
                    divsoup =  BeautifulSoup(str(div), 'html.parser')
                    tmp = divsoup.find_all('span')
                    less.name = tmp[5].contents[0]
                    if less.name[0].islower():
                        less.name = 'И' + less.name
                    less.time = tmp[1].contents[0] + tmp[2].contents[0] + tmp[3].contents[0]
                    
                less.type = attrsoup.find('div', attrs={'class': 'lesson__type'}).contents[0]
                less.groups = [i[2:-4] for i in re.findall('\">[0-9\/]{13}<\/a>', str(attrsoup.find_all('span', attrs={'class': 'lesson__group'})), re.M|re.I)]
                less.teacher = re.search('\">[А-Яа-я\-A-Za-z\s]+<\/span><\/a><\/div>', str(attrsoup.find('div', attrs={'class': 'lesson__teachers'}).contents[0])).group()[2:-17]
                spansoup = BeautifulSoup(str(attrsoup.find('div', attrs={'class': 'lesson__places'}).contents[0]), 'html.parser')
                span = spansoup.find_all('span')
                less.place = span[1].contents[0] + ', ' + span[6].contents[0] + span[7].contents[0]
            rday.append(less)
        ruz.append(rday.copy())
    ruz.append([])
    ruz.append([])
    return ruz

def getExtRuz(date=''):
    if not date:
        date = (datetime.datetime.now() - datetime.timedelta(days=datetime.datetime.now().weekday())).strftime('%Y-%m-%d')
    r = getRuz(date)
    d = datetime.datetime.strptime(date, '%Y-%m-%d')
    d -= datetime.timedelta(days=d.weekday())
    d += datetime.timedelta(days=7)
    [r.append(i) for i in getRuz(d.strftime('%Y-%m-%d'))]
    return r
