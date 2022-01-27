#!/usr/bin/env python3
""" SecLab Bot client """

import json
import sys
import os
import time
import curses
import logging
from typing import Optional
import requests
from pyfiglet import Figlet


LOG_FILE = 'files/client.log'
MAX_LOG_ENTRIES = 1024

API_USER = os.environ.get("API_USER")
API_PASS = os.environ.get("API_PASS")
API_URL = "https://cpsecurity.club/api/v1/status"
#API_URL = "http://localhost:3000/api/v1/status"

FIGLET_FONT = 'doh'
FIGLET_WIDTH = 154
FIGLET = Figlet(font=FIGLET_FONT, width=FIGLET_WIDTH)
BANNER_OPEN = FIGLET.renderText('Lab is OPEN :)'.strip())
BANNER_CLOSE = FIGLET.renderText('Lab is CLOSED :('.strip())

with open('fire.txt', 'r') as f:
    fire = f.read()

BANNER_FIRE = FIGLET.renderText(('Lab is\n').strip()) + fire

with open('coffee.txt', 'r') as c:
    coffee = c.read()

BANNER_COFFEE = FIGLET.renderText(('Out for\n').strip()) + coffee

STATE_CLOSED = 0
STATE_OPEN = 1

PRE_DEF_COLORS = {
    "open": "brightgreen",
    "closed": "red",
    "fire": "orange",
    "coffee": "8f7369"
}


def api_request(reqtype, statcolor: Optional[str] = None):
    """ Takes a request type (open, closed, etc.) and makes the request """
    logging.info("client sent " + reqtype + " request")
    if statcolor is None:
        if reqtype in PRE_DEF_COLORS:
            statcolor = PRE_DEF_COLORS[reqtype]
        else:
            statcolor = "purple"
    data = {"StatusName": reqtype, "StatusColor": statcolor}
    try:
        resp = requests.post(API_URL, json=data, auth=(API_USER, API_PASS))
    except:
        return False
    if resp.status_code != 200:
            return False
    return True


def ncurses_write(win, msg):
    """ Takes an ncurses screen and a string and writes to the screen """
    try:
        win.clear()
        win.addstr(msg, curses.A_BOLD)
    except Exception as exc:
        logging.warning("NCurses exception: " + str(exc))


def main(win):
    """ ncurses loop """
    logging.info("client init")

    state = STATE_CLOSED

    # ncurses init
    win.clear()
    curses.curs_set(0)
    win.nodelay(0)
    win.addstr("Use any key to toggle, or control-c to quit")
    win.refresh()
    success = True

    gotchar = 0

    while True:
        try:
            if not truncate_log():
                return
            ch = win.getch()  # block for keypress
            if time.time() - gotchar < 0.1:
                continue
            if ch == ord('f') and state == STATE_OPEN: # the lab is burning
                reqtype = "fire"
                success = api_request(reqtype)
                if success:
                    ncurses_write(win, BANNER_FIRE)
            elif ch == ord('c') and state == STATE_OPEN: # coffee mode
                reqtype = "coffee"
                success = api_request(reqtype)
                if success:
                    ncurses_write(win, BANNER_COFFEE)
            elif state == STATE_CLOSED:
                reqtype = "open"
                success = api_request(reqtype)
                if success:
                    ncurses_write(win, BANNER_OPEN)
            elif state == STATE_OPEN:
                reqtype = "closed"
                success = api_request(reqtype)
                if success:
                    ncurses_write(win, BANNER_CLOSE)
            if success:
                logging.info(reqtype + " request success")
                state ^= 1
            else:
                curses.flash()
                curses.beep()
                logging.warning(reqtype + " request failed")
            gotchar = time.time()
        except KeyboardInterrupt:
            logging.info("client exit")
            return


def show_help():
    """ Print help information """
    print("SecLab Bot usage: python3 sec-lab-bot.py")
    print()
    print("The following env vars are required for operation:")
    print("\tAPI_USER\t[api username]")
    print("\tAPI_PASS\t[api password]")
    print("Use any key to toggle open/close, or control-c to quit")


def truncate_log():
    """ Dump the log file if it's gotten too long """
    try:
        with open(LOG_FILE, 'w+') as log_file:
            if len(log_file.readlines()) > MAX_LOG_ENTRIES:
                log_file.write("")
        return True
    except:
        print("Error truncating log file")
        return False


if __name__ == '__main__':
    if "-h" in sys.argv or "--help" in sys.argv:
        show_help()
        sys.exit(0)

    logging.basicConfig(filename=LOG_FILE,
                        format='[%(asctime)s] %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p',
                        level=logging.DEBUG)

    curses.wrapper(main)
    logging.shutdown()
    sys.exit(0)
