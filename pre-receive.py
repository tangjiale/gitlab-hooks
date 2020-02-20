#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020-02-20 19:26
# @Author  : jiale
# @Site    : 
# @File    : pre-receive.py
# @Software: PyCharm
import subprocess
import sys
import fileinput

# 读取用户试图更新的所有引用
for line in fileinput.input():
    print("pre-receive: Trying to push ref: %s" % line)
    temp = subprocess.getoutput("git show f3c1e52036ec2dd4f55efe0cabfd2f09fd834e92")
    log = temp.split("\n")
    for l in log:
        print("xxx=" + l)
# 放弃推送
sys.exit(1)
