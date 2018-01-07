#!/usr/bin/env python
 
import sys
import os
from time import sleep
from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
h=datetime.now()
sched = Scheduler()
#sched.start()        
 
# define the function that is to be executed
# it will be executed in a thread by the scheduler
def my_job(text):
    print (text)
 
def main():
    # job = sched.add_date_job(my_job, datetime(2013, 8, 5, 23, 47, 5), ['text'])
    job = sched.add_interval_job(my_job, seconds=5, args=['text'])
    if h <  datetime.now() + timedelta(seconds=15):
        try:
            sched.start()  # start the scheduler
        except (KeyboardInterrupt, SystemExit):
    else:
        print('job done')



 