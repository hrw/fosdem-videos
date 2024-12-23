#!/usr/bin/python3
# SPDX-License-Identifier: MIT

from datetime import date, datetime, timezone
from jinja2 import Environment, FileSystemLoader
import xml.etree.ElementTree as ET
import sys


def get_year_data(xml_root):

    for day in root.iter('day'):

        year_data["year"] = date.fromisoformat(day.attrib['date']).year

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
                    'year': year_data["year"],
                }

                talk_with_video = False
                persons = []

                for person in talk.find('persons').iter('person'):
                    persons.append(person.text)

                new_talk['persons'] = ', '.join(persons)

                for link in talk.find('links'):
                    if link.attrib['href'].endswith('webm'):
                        new_talk['webm'] = link.attrib['href']
                        talk_with_video = True
                        year_data["show_webm"] = True
                    elif link.attrib['href'].endswith('mp4'):
                        new_talk['mp4'] = link.attrib['href']
                        talk_with_video = True
                        year_data["show_mp4"] = True
                    elif 'Slides' in link.text or 'Presentation' in link.text:
                        new_talk['slides'] = link.attrib['href']

                try:
                    for link in talk.find('attachments'):
                        new_talk['slides'] = link.attrib['href']
                except TypeError:
                    # <attachments> are in 2020+
                    pass


                if 'slides' in new_talk:
                    year_data["amounts"]["slides"] += 1

                year_data["talks"].append(new_talk)
                if talk_with_video:
                    year_data["amounts"]["videos"] += 1

    return year_data


if len(sys.argv) == 1:
    print("Give me some XML files to parse.")
    exit(1)

xml_files_to_parse = sys.argv[1:]

year_data = {"year": 0, "talks": [], "show_webm": False, "show_mp4": False,
             "amounts": {"talks": 0, "slides": 0, "videos": 0}}

for xml_file in xml_files_to_parse:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    year_data = get_year_data(root)

if len(xml_files_to_parse) > 1:
    multiple_years = True
    year = f"Years: 2012 - {year_data['year']}"
else:
    multiple_years = False
    year = f"Year: {year_data['year']}"


file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

template = env.get_template('index.html.j2')

page_title = f"FOSDEM"

if not multiple_years:
    page_title += " " + str(year_data["year"])

page_title += " schedule with links to slides and videos"

output = template.render(generate_time=datetime.strftime(
                            datetime.now(timezone.utc), "%d %B %Y %H:%M"),
                         talks=year_data["talks"], year=year_data["year"],
                         show_webm=year_data["show_webm"],
                         show_mp4=year_data["show_mp4"],
                         multiple_years=multiple_years,
                         git_repo="fosdem-videos",
                         amount_talks=len(year_data["talks"]),
                         amount_slides=year_data["amounts"]["slides"],
                         amount_videos=year_data["amounts"]["videos"],
                         page_title=page_title,
                         years=range(2012, date.today().year + 1))

print(output)
print(f"{year} "
      f"Talks: {len(year_data['talks'])} "
      f"Slides: {year_data['amounts']['slides']} "
      f"Videos: {year_data['amounts']['videos']}",
      file=sys.stderr)
