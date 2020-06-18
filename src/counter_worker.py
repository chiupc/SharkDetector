#!/usr/bin/python3

import threading
import time
from counter import Counter
from datetime import datetime

class Counter_Worker(threading.Thread):
    def __init__(self, threadID, symbol, counter,endtime):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = Counter(symbol,counter)
    def run(self):
        print("Starting worker for " + self.symbol+' (' + self.counter + ')')
        timestampnow=datetime.now().timestamp()
        while timestampnow<endtime:
            self.counter.refresh_price()
            self.counter.refresh_volume()
            self.counter.detect_shark()
            timestampnow=datetime.now().timestamp()
            time.sleep(10)

threadLock = threading.Lock()
threads = []

# Create new threads
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# Start new Threads
thread1.start()
thread2.start()

# Add threads to thread list
threads.append(thread1)
threads.append(thread2)

# Wait for all threads to complete
for t in threads:
    t.join()
print ("Exiting Main Thread")