#!/usr/bin/env python3

import sys
sys.path.append('..')
sys.path.append('.')
from vacan.web_interface import web

if __name__ == '__main__':
    web.start_server()
    
