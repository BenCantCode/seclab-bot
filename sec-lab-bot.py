#!/usr/bin/env python3

import sys
import hmac
import curses
from time import time
from pyfiglet import Figlet

FIGLET_FONT = 'doh'
FIGLET_WIDTH = 256

CLOSED = 0
OPEN = 1

class NetworkException(Exception):
    pass

def network_trycatch(reqtype="open"):
    def decorator(fn):
        def inner():
            try:
                # conn = connect()
                fn(conn)
            #except something assertion-related:
                # raise NetworkException(' '.join(["Error response to", reqtype, "request"]))
            except:
                raise NetworkException(' '.join(["Failed to send", reqtype, "request"]))
            finally:
                pass # if conn: conn.close()
        return inner
    return decorator

def timestamp():
    """ Return an 8-byte timestamp in little-endian with second-resolution """
    return int.to_bytes(time().__trunc__(), 8, 'little')

@network_trycatch(reqtype="open")
def send_open_request(conn=None):
    pass # TODO

@network_trycatch(reqtype="close")
def send_close_request(conn=None):
    pass # TODO

"""
        TODO
    ************
    * bold     *
    * color    *
    * requests *
    ************
"""

def main(win):
    fig = Figlet(font=FIGLET_FONT, width=FIGLET_WIDTH)
    state = CLOSED
    win.addstr("Any key to toggle, Control-c to quit")
    while True:          
        try:                 
            key = win.getch()         
            if key != -1:
                win.clear()
                if state == CLOSED:
                    try:
                        send_open_request()
                        banner = fig.renderText('The Lab is\nOPEN :)')
                    except NetworkException as e:
                        print(e, file=sys.stderr)
                elif state == OPEN:
                    try:
                        send_close_request()
                        banner = fig.renderText('The Lab is\nCLOSED :(')
                    except NetworkException as e:
                        print(e, file=sys.stderr)
                win.addstr(banner)
                state ^= 1
        except KeyboardInterrupt:
            return

if __name__ == '__main__':
    curses.wrapper(main)
