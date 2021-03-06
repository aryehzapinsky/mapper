#!/usr/bin/env python3
""" This program maps Columbia's Directory of Courses """

__author__ = "Aryeh Zapinsky"

import threading, queue
import urllib.request as ur
from urllib.error import URLError
import re
import sqlite3
import sys
import os.path

'''
drop_directory_table function that drops table
'''
def drop_directory_table(connection):
    curse = connection.cursor()
    curse.execute("DROP TABLE IF EXISTS directory")
    curse.close()

'''
create_directory_table function that creates table
'''
def create_directory_table(connection):
    curse = connection.cursor()
    curse.execute("CREATE TABLE IF NOT EXISTS directory"
              "(title      TEXT,"
              "epithet     TEXT,"
              "call        TEXT,"
              "day_time    TEXT,"
              "location    TEXT,"
              "points      TEXT,"
              "approvals   TEXT,"
              "instructor  TEXT,"
              "style       TEXT,"
              "description TEXT,"
              "site        TEXT,"
              "department  TEXT,"
              "enrollment  TEXT,"
              "subject     TEXT,"
              "number      TEXT,"
              "section     TEXT,"
              "division    TEXT,"
              "open_to     TEXT,"
              "campus      TEXT,"
              "note        TEXT,"
              "key         TEXT)"
    )
    curse.close()

'''
data_entry function that processes the course and enters into database
html = html from urlopen
'''
def data_entry(connection, html):
    title = html[html.find("+1>") + len("+1>"):]
    title = title.split("<")[0]
    #print(title)
    epithet = html[html.find("+2>") + len("+2>"):]
    epithet = epithet.split("<")[0]
    #print(epithet)

    # Separate entries of the HTML table of the directory
    tag = re.compile('[A-Z]{4}>(.+?)</td>')
    fields = re.findall(tag, html)
    try:
        call = (fields[fields.index("Call Number")+1])
    except ValueError:
        call = "N/A: Couldn't find data"
    try:
        data = (fields[fields.index("Day &amp; Time<br>Location")+1]).split("<br>")
        day_time = data[0]
        location = data[1]
    except ValueError:
        day_time = "N/A: Couldn't find data"
        location = "N/A: Couldn't find data"
    try:
        points = (fields[fields.index("Points")+1])
    except ValueError:
        points = "N/A: Couldn't find data"
    try:
        approvals = (fields[fields.index("Approvals Required")+1])
    except ValueError:
        approvals = "N/A: Couldn't find data"
    try:
        instructor = (fields[fields.index("Instructor")+1])
    except ValueError:
        instructor = "N/A: Couldn't find data"
    try:
        style = (fields[fields.index("Type")+1])
    except ValueError:
        style = "N/A: Couldn't find data"
    try:
        description = (fields[fields.index("Course Description")+1])
    except ValueError:
        description = "N/A: Couldn't find data"
    try:
        site = (fields[fields.index("Web Site")+1])
    except ValueError:
        site = "N/A: Couldn't find data"
    try:
        department = (fields[fields.index("Department")+1])
    except ValueError:
        department= "N/A: Couldn't find data"
    try:
        enrollment = (fields[fields.index("Enrollment")+1])
    except ValueError:
        enrollment = "N/A: Couldn't find data"
    try:
        subject = (fields[fields.index("Subject")+1])
    except ValueError:
        subject = "N/A: Couldn't find data"
    try:
        number = (fields[fields.index("Number")+1])
    except ValueError:
        number = "N/A: Couldn't find data"
    try:
        section = (fields[fields.index("Section")+1])
    except ValueError:
        section = "N/A: Couldn't find data"
    try:
        division = (fields[fields.index("Division")+1])
    except ValueError:
        division = "N/A: Couldn't find data"
    try:
        open_to = (fields[fields.index("Open To")+1])
    except ValueError:
        open_to = "N/A: Couldn't find data"
    try:
        campus = (fields[fields.index("Campus")+1])
    except ValueError:
        campus = "N/A: Couldn't find data"
    try:
        note = (fields[fields.index("Note")+1])
    except ValueError:
        note = "N/A: Couldn't find data"
    try:
        key = (fields[fields.index("Section key")+1])
    except ValueError:
        key = "N/A: Couldn't find data"

    curse = connection.cursor()
    curse.execute("INSERT INTO directory"
              "(title, epithet, call, day_time, location, points, approvals, instructor, style, description, site, department, enrollment, subject, number, section, division, open_to, campus, note, key)"
              "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (title, epithet, call, day_time, location, points, approvals, instructor, style, description, site, department, enrollment, subject, number, section, division, open_to, campus, note, key)
    )
    connection.commit()
    curse.close()


'''
worker function that handles the courses
'''
def worker(links_to_process, conn, site):
    while not links_to_process.empty():
        url_link = links_to_process.get()
        #print (url_link)
        try:
            response = ur.urlopen(url_link)
        except URLError as e:
            if hasattr(e, 'reason'):
                print('We failed to reach a server.')
                print('Reason: ', e.reason)
            elif hasattr(e, 'code'):
                print('The server couldn\'t fulfill the request.')
                print('Error code: ', e.code)
        else:
            html = str(response.read())

            # checks to see if course or directory
            pattern = re.compile("[0-9]{4}-[0-9]{5}-[0-9]{3}")
            # PROCESS COURSE
            if pattern.search(url_link):
                data_entry(conn, html)
            # Add course or link to be followed
            else:
                parsing = html.split('"')
                subjs = [x for x in parsing
                         if any (i in x for i in ["subj-", "subj/"])
                         and "_text" not in x]
                for suffix in subjs:
                    # print(suffix[suffix.find("subj/") + len("subj/"):])
                    midfix = "/cu/bulletin/uwb/"
                    if midfix not in suffix:
                        suffix = midfix + suffix
                    links_to_process.put(site+suffix)

'''
test fucntion to check that database has all the courses.
Prints out the entries of the directory table
'''
def test(connection):
    print("||About to execute SQLite command||")
    curse = connection.cursor()
    curse.execute('SELECT title FROM directory')
    data = curse.fetchall()
    """
    for row in data:
        print(*row)
    """
    curse.close()
    return data

def start():

    num_worker_threads = 8
    threads = []

    conn = sqlite3.connect('columbia_map.db', check_same_thread = False)

    site =  "http://www.columbia.edu"
    directory_home = site + "/cu/bulletin/uwb/sel/subj-H.html"
    # just H subdirectory "/cu/bulletin/uwb/sel/subj-H.html"
    # whole directory "/cu/bulletin/uwb/home.html"

    links_to_process = queue.Queue()
    links_to_process.put(directory_home)

    #drop_directory_table(conn)
    #print("Creating the table if it does not already exist.")
    create_directory_table(conn)

    if not os.path.isfile("columbia_map.db"):

        print("Walking through the interwebs")
        for i in range(num_worker_threads):
            t = threading.Thread(target=worker, args=(links_to_process, conn, site))
            t.start()
            threads.append(t)

            # stop workers
            for t in threads:
                t.join()

    data = test(conn)
    # close database
    conn.close()
    return data

if __name__ == '__main__':
    print(start())
    ends = [x[0] for x in start()]
    for end in ends:
        print(end)
