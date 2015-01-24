#!/usr/bin/env python3

""" This file contains main configuration of Data Analyzer Chart.
"""

from collections import namedtuple

TagRepr = namedtuple('Tag', ['name', 'text', 'title'])

TAGS = [TagRepr('c++', 'c++', 'cpp'),
        TagRepr('java', 'java', 'java'),
        TagRepr('perl', 'perl', 'perl'),
        TagRepr('python', 'python', 'python'),
        TagRepr('sap', 'sap', 'sap'),
        TagRepr('bash', 'bash', 'bash'),
        TagRepr('perl', 'perl', 'perl'),
        TagRepr('ruby', 'ruby', 'ruby'),
        TagRepr('javascript', 'javascript', 'javascript'),
        TagRepr('php', 'php', 'php'),
        TagRepr('1c', '1c', 'onec'),
        TagRepr('c#', 'c#', 'csharp'),
        # Databases...
        # Os...
        # Position...
       ]

TAG_NAMES = [tag.name for tag in TAGS]
