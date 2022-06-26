import json
import os
import time
from datetime import datetime

import psutil
debug = True

def report_memory_usage(user):
    if debug:
        current_memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
        memory_report = {
            'user': user,
            'time': str(datetime.now()),
            'memory': current_memory_usage
        }
        print(json.dumps(memory_report, indent=1))
        with open(f'debug_info/memory_usage.json', 'a') as f:
            f.write(f'\n{memory_report}')

while True:
    report_memory_usage('test')
    time.sleep(10)