#!/usr/bin/python3

from datetime import date, datetime
from jinja2 import Environment, FileSystemLoader
import xml.etree.ElementTree as ET

tree = ET.parse('xml')
root = tree.getroot()

talks = []

for day in root.iter('day'):

    year = date.fromisoformat(day.attrib['date']).year

    if day.attrib['index'] == '1':
        day_name = 'Sat'
    elif day.attrib['index'] == '2':
        day_name = 'Sun'

    for room in day:
        room_name = room.attrib['name']

        for talk in room.iter('event'):
            new_talk = {
                'room': room_name,
                'start': '%s %s' % (day_name, talk.find('start').text),
                'title': talk.find('title').text,
                'track': talk.find('track').text,
                'slug': talk.find('slug').text,
            }

            persons = []

            for person in talk.find('persons').iter('person'):
                persons.append(person.text)

            new_talk['persons'] = ', '.join(persons)

            if talk.find('attachments'):
                for link in talk.find('attachments'):
                    new_talk['slides'] = link.attrib['href']

            for link in talk.find('links'):
                if 'WebM' in link.text:
                    new_talk['webm'] = link.attrib['href']
                elif 'mp4' in link.text or 'mp4' in link.attrib['href']:
                    new_talk['mp4'] = link.attrib['href']
                elif 'Slides' in link.text or 'Presentation' in link.text:
                    new_talk['slides'] = link.attrib['href']

            talks.append(new_talk)

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

template = env.get_template('index.html.j2')

output = template.render(generate_time=datetime.strftime(datetime.utcnow(),
                                                         "%d %B %Y %H:%M"),
                         talks=talks, year=year)

with open('index.html', 'w') as html:
    html.write(output)
