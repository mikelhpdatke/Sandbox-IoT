import sys
import logging
import os
import subprocess
import time
from sniffer import Sniffer
from strace import Strace
from utils import Top

if __name__ == "__main__":
    logging.debug('This is a debug message')
    startTime = int(time.time())

    timeout = int(sys.argv[2]) or 5 #default 5s stop proc
    sniff = Sniffer(sys.argv[1])
    strace = Strace(sys.argv[1])
    top = Top()

    print('----')

    top.start()

    print('----')

    sniff.start()
    print('----')

    strace.start();
    print('----')
    # while (strace.proc.poll() and (startTime + timeout >= time.time())):
    #     print(startTime + timeout, time.time())
    #     continue

    sniff.stop();
    strace.stop();
    top.stop();