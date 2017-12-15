# -*- coding: utf-8 -*-

from subprocess import Popen, PIPE
import re

project   = 'IREM-Jongle'
copyright = '2017, Georges Khaznadar'
author    = 'Georges Khaznadar'

# version et release sont déduits des tags de Git

p=Popen("git tag | grep -E 'v.*'", shell=True, stdout=PIPE)
out, _ = p.communicate()
release = max([version[1:] for version in out.strip().decode("utf-8").split("\n")])
version = re.match(r"([.0-9]*).*", release).group(1)

if __name__ == "__main__":
    print ("release = %s, version = %s" %(release, version))
