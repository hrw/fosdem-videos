#!/usr/bin/python3

from datetime import date, datetime
from jinja2 import Environment, FileSystemLoader
import xml.etree.ElementTree as ET
import sys

xml_file = 'xml'
if len(sys.argv) > 1:
    xml_file = sys.argv[1]

tree = ET.parse(xml_file)
root = tree.getroot()

talks = []
show_webm = False
amount_slides = 0
amount_videos = 0

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

            talk_with_video = False
            persons = []

            for person in talk.find('persons').iter('person'):
                persons.append(person.text)

            new_talk['persons'] = ', '.join(persons)

            if talk.find('attachments'):
                for link in talk.find('attachments'):
                    new_talk['slides'] = link.attrib['href']
                    amount_slides += 1

            for link in talk.find('links'):
                if 'WebM' in link.text:
                    new_talk['webm'] = link.attrib['href']
                    talk_with_video = True
                    show_webm = True
                elif 'mp4' in link.text or 'mp4' in link.attrib['href']:
                    new_talk['mp4'] = link.attrib['href']
                    talk_with_video = True
                elif 'Slides' in link.text or 'Presentation' in link.text:
                    new_talk['slides'] = link.attrib['href']
                    amount_slides += 1

            talks.append(new_talk)
            if talk_with_video:
                amount_videos += 1

file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

template = env.get_template('index.html.j2')

output = template.render(generate_time=datetime.strftime(datetime.utcnow(),
                                                         "%d %B %Y %H:%M"),
                         talks=talks, year=year, show_webm=show_webm,
                         amount_talks=len(talks),
                         amount_slides=amount_slides,
                         amount_videos=amount_videos,
                         years=range(2015, 2023))

print(output)
print(f"Talks: {len(talks)} amount_slides: {amount_slides} "
      " amount_videos: {amount_videos}",
      file=sys.stderr)
