# -*- coding: utf-8 -*-
from __future__ import print_function

from subprocess import Popen, PIPE
import re

project   = u'IREM-Jongle'
copyright = u'2017, Georges Khaznadar'
author    = u'Georges Khaznadar'
version   = u'0.1'
release   = u'0.1'

p=Popen("git tag | grep -E 'v.*'", shell=True, stdout=PIPE)
out, _ = p.communicate()
release = unicode(max([version[1:] for version in out.strip().split("\n")]))
version = re.match(r"([.0-9]*).*", release).group(1)

if __name__ == "__main__":
    print ("release = %s, version = %s" %(release, version))
