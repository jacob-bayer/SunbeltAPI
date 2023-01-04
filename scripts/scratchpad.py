#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 17 17:54:48 2022

@author: jacob
"""

import queue
import threading
import time

q = queue.Queue()
stop_event = threading.Event()

sent = """This sentence will be printed one word at a time. 
          Send a KeyboardInterrupt to stop."""
words = sent.split()
        
def add_a_word_to_queue(words):
    for word in words:
        q.put(word)
        print("ADDER: Word added. Sleeping 10 secs.")
        if stop_event.is_set():
            print("ADDER: Event is set. Breaking.")
            break
        time.sleep(5)
        
def process_queue():
    while not stop_event.is_set():
        word = q.get()
        print("PROCESSOR:", word)
        print("PROCESSOR: Length of remaining queue", len(q.queue))
        time.sleep(10)
        if stop_event.is_set():
            print("PROCESSOR: Event is set. Breaking")
            
queue_adding_thread = threading.Thread(name = 'queue_adding_thread',
                                       target = add_a_word_to_queue,
                                       args = [words],
                                       daemon = True)
queue_working_thread = threading.Thread(name = 'queue_working_thread',
                                        target = process_queue,
                                       daemon = True)
try:
    queue_adding_thread.start()
    queue_working_thread.start()
    queue_working_thread.join()
except KeyboardInterrupt:
    stop_event.set()

