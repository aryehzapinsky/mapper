#!/usr/bin/env python
""" This program maps Columbia's Directory of Courses """

__author__ = "Aryeh Zapinsky"

import threading, queue
import urllib.request as ur

queue_lock = threading.Lock()
links_to_process = queue.Queue()
num_worker_threads = 8
threads = []

site =  "http://www.columbia.edu"
directory_home = site + #"/cu/bulletin/uwb/home.html"

links_to_process.put(directory_home)

def worker():
    while not links_to_process.empty():
        url_link = links_to_process.get()
        print (url_link)
        with ur.urlopen(url_link) as response:
            html = str(response.read())
            parsing = html.split('"')
            dirty_words = ["subject", "_text"]
            subjs = [x for x in parsing if "subj" in x
                     and all(i not in x for i in dirty_words)]
            #print (matching)
            for suffix in subjs:
                print("||" + suffix)
                midfix = "/cu/bulletin/uwb/"
                if midfix not in suffix:
                    suffix = midfix + suffix
                links_to_process.put(site+suffix)
                #print(site+suffix)

    print("|||WORKING|||")
    return 1


def main():
    for i in range(num_worker_threads):
        t = threading.Thread(target=worker)
        t.start()
        threads.append(t)

        # stop workers
        for t in threads:
            t.join()

if __name__ == '__main__':
    main()
