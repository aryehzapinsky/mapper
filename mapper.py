#!/usr/bin/env python
""" This program maps Columbia's Directory of Courses """

__author__ = "Aryeh Zapinsky"

import threading, queue
import urllib.request as ur
import re
import sqlite3

 #queue_lock = threading.Lock()
links_to_process = queue.Queue()
num_worker_threads = 8
threads = []

conn = sqlite3.connect('columbia_map.db')
c = conn.cursor()

def create_table():
    c.execute("CREATE TABLE directory"
              "(title       TEXT)"
              "(epithet     TEXT)"
              "(call        TEXT)"
              "(day_time    TEXT)"
              "(location    TEXT)"
              "(points      TEXT)"
              "(approvals   TEXT)"
              "(instructor  TEXT)"
              "(type        TEXT)"
              "(description TEXT)"
              "(site        TEXT)"
              "(department  TEXT)"
              "(enrollment  TEXT)"
              "(subject     TEXT)"
              "(number      TEXT)"
              "(section     TEXT)"
              "(division    TEXT)"
              "(open        TEXT)"
              "(campus      TEXT)"
              "(key         TEXT)"
    )

def data_entry(html):
    c.execute()

    conn.commit()

site =  "http://www.columbia.edu"
directory_home = site + "/cu/bulletin/uwb/sel/subj-H.html"#"/cu/bulletin/uwb/home.html"

links_to_process.put(directory_home)

def worker():
    while not links_to_process.empty():
        url_link = links_to_process.get()
        #print (url_link)
        with ur.urlopen(url_link) as response:
            html = str(response.read())

            # checks to see if course or directory
            pattern = re.compile("[0-9]{4}-[0-9]{5}-[0-9]{3}")
            if pattern.search(url_link):
                html.find
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


def main():
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

        # stop workers
        for t in threads:
            t.join()

        # close database
        #c.close()
        #conn.close()

if __name__ == '__main__':
    main()
