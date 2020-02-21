#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020-02-20 19:26
# @Author  : jiale
# @Site    : 
# @File    : pre-receive.py
# @Software: PyCharm
import subprocess
import sys
import re
from datetime import datetime


# pre-receive Trigger
class Trigger(object):

    def __init__(self):
        self.pattern = "(feat|fix|test|refactor|docs|style|chroe)\(.*\):.*"
        # GMT格式：Fri Feb 21 15:16:07 2020 +0800
        self.gmt_format = '%a %b %d %H:%M:%S %Y +0800'
        # 需要验证的分支多个用|间隔
        self.branch = "dev|master"
        # 删除/新增 时的commitId
        self.base_commit_id = "0000000000000000000000000000000000000000"

    def pushSuccessBack(self):
        print("push success!")
        sys.exit(0)

    # 推送消息失败返回
    def pushFailBack(self):
        print("##################################################################")
        print("##                                                              ##")
        print("## push message style check failed!                             ##")
        print("##                                                              ##")
        print("## type must be one of [feat,fix,docs,style,refactor,test,chore]##")
        print("##                                                              ##")
        print("## Example:                                                     ##")
        print("##   feat(user): add the user login.                            ##")
        print("##                                                              ##")
        print("##################################################################")
        sys.exit(1)

    # 获取提交的git信息
    def getGitPushInfo(self):
        oldObject, newObject, ref = sys.stdin.readline().strip().split(' ')
        branch = str(ref).split("/")[2]
        if oldObject == self.base_commit_id or newObject == self.base_commit_id:
            self.pushSuccessBack()
        elif branch in self.branch:
            self.getPushInfo(oldObject, newObject)
        else:
            self.pushSuccessBack()

    # 获取推送消息
    def getPushInfo(self, old_object, new_object):
        """
        git show命令获取push作者，时间， 提交的日志，以及文件列表
        文件的路径为相对于版本库根目录的一个相对路径
        """
        rev = subprocess.Popen('git rev-list ' + new_object, shell=True, stdout=subprocess.PIPE)
        revList = rev.stdout.readlines()
        revList = [x.strip() for x in revList]
        # 查找从上次提交self.oldObject之后还有多少次提交，即本次push提交的object列表
        indexOld = revList.index(old_object.encode("utf-8"))
        pushList = revList[:indexOld]
        # 循环获取每次提交的文件列表
        for pObject in pushList:
            p = subprocess.Popen('git show ' + pObject.decode("utf-8"), shell=True, stdout=subprocess.PIPE)
            pipe = p.stdout.readlines()
            pipe = [x.strip() for x in pipe]
            pushAuthor = pipe[1].decode("utf-8").strip("Author:").strip()
            pushTime = pipe[2].decode("utf-8").strip("Date:").strip()
            pushMsg = pipe[4].decode("utf-8").strip()
            # 获取文件列表
            # self.fileList.extend(['/'.join(fileName.split("/")[1:]) for fileName in pipe if
            #                       fileName.startswith("+++") and not fileName.endswith("null")])
            print("推送时间:", datetime.strptime(pushTime, self.gmt_format))
            print("推送作者:", pushAuthor)
            print("推送日志信息:", pushMsg)
            if re.match(self.pattern, pushMsg, re.M | re.I):
                print("push success!message=%s" % pushMsg)
                sys.exit(0)
            else:
                self.pushFailBack()


if __name__ == "__main__":
    t = Trigger()
    t.getGitPushInfo()
