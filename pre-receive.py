#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020-02-20 19:26
# @Author  : jiale
# @Site    : 
# @File    : pre-receive.py
# @Software: PyCharm
from datetime import datetime
import subprocess
import sys
import re


# pre-receive Trigger
class ReceiveTrigger(object):

    def __init__(self):
        self.pattern = "(feat|fix|test|refactor|docs|style|chroe)\(.*\):.*"
        # GMT格式：Fri Feb 21 15:16:07 2020 +0800
        self.gmt_format = '%a %b %d %H:%M:%S %Y +0800'
        # 需要验证的分支,多个用|间隔
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
        # 获取提交的git信息<old-value> <new-value> <ref-name>:<旧的commitId><新的commitId><引用名称>
        old_value, new_value, ref_name = sys.stdin.readline().strip().split(' ')
        branch = str(ref_name).split("/")[2]
        if old_value == self.base_commit_id or new_value == self.base_commit_id:
            self.pushSuccessBack()
        elif branch in self.branch:
            self.getPushInfo(old_value, new_value)
        else:
            self.pushSuccessBack()

    # 获取推送消息
    def getPushInfo(self, old_value, new_value):
        """
        git show命令获取push作者，时间， 提交的日志，以及文件列表
        文件的路径为相对于版本库根目录的一个相对路径
        """
        rev = subprocess.Popen('git rev-list ' + new_value, shell=True, stdout=subprocess.PIPE)
        revList = rev.stdout.readlines()
        revList = [x.strip() for x in revList]
        # 查找从上次提交old_value之后还有多少次提交，即本次push提交的object列表
        indexOld = revList.index(old_value.encode("utf-8"))
        pushList = revList[:indexOld]
        # 循环获取每次提交的文件列表
        for pObject in pushList:
            p = subprocess.Popen('git show ' + pObject.decode("utf-8"), shell=True, stdout=subprocess.PIPE)
            pipe = p.stdout.readlines()
            pipe = [x.strip() for x in pipe]
            print("pipe=%s" % pipe)
            push_author = pipe[1].decode("utf-8").strip("Author:").strip()
            push_time = pipe[2].decode("utf-8").strip("Date:").strip()
            push_msg = pipe[4].decode("utf-8").strip()
            # 获取文件列表
            # self.fileList.extend(['/'.join(fileName.split("/")[1:]) for fileName in pipe if
            #                       fileName.startswith("+++") and not fileName.endswith("null")])
            print("推送时间:", datetime.strptime(push_time, self.gmt_format))
            print("推送作者:", push_author)
            print("推送日志信息:", push_msg)
            if re.match(self.pattern, push_msg, re.M | re.I):
                print("push success!message=%s" % push_msg)
                sys.exit(0)
            else:
                self.pushFailBack()


if __name__ == "__main__":
    receive = ReceiveTrigger()
    receive.getGitPushInfo()
