#!/usr/bin/env python3

""" This file contains main configuration of Data Analyzer Chart.
"""

from collections import namedtuple

TagRepr = namedtuple('Tag', ['name', 'text', 'title'])

TAGS = [TagRepr('c++', 'c++', 'cpp'),
        TagRepr('java', 'java', 'java'),
        TagRepr('python', 'python', 'python'),
        TagRepr('sap', 'sap', 'sap'),
        TagRepr('bash', 'bash', 'bash'),
        TagRepr('perl', 'perl', 'perl'),
        TagRepr('ruby', 'ruby', 'ruby'),
        TagRepr('javascript', 'javascript', 'javascript'),
        TagRepr('php', 'php', 'php'),
        TagRepr('1c', '1c', 'onec'),
        TagRepr('c#', 'c#', 'csharp'),

        TagRepr('algol','algol','algol'),
        TagRepr('ada','ada','ada'),
        TagRepr('basic','basic','basic'),
        TagRepr('cobol','cobol','cobol'),
        TagRepr('lisp','lisp','lisp'),
        TagRepr('erlang','erlang','erlang'),
        TagRepr('go','go','go'),
        TagRepr('groovy','groovy','groovy'),
        TagRepr('haskell','haskell','haskell'),
        TagRepr('lua','lua','lua'),
        TagRepr('matlab','matlab','matlab'),
        TagRepr('pascal','pascal','pascal'),
        TagRepr('rust','rust','rust'),
        TagRepr('scala','scala','scala'),
        TagRepr('smalltalk','smalltalk','smalltalk'),
        TagRepr('swift','swift','swift'),
        TagRepr('R','r','R'),
        TagRepr('sql','sql','sql'),
        TagRepr('VBA','vba','vba'),
        # Databases...
        # Os...
        # Position...
       ]

TAG_NAMES = [tag.name for tag in TAGS]
