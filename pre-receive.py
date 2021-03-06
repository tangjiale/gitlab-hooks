#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Time    : 2020-02-20 19:26
# @Author  : tangjiale
# @Site    :
# @File    : pre-receive.py
# @Software: PyCharm
from datetime import datetime
import subprocess
import sys
import re
import codecs
import logging
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
# 设置日志输出
logging.basicConfig(
    filename="/var/log/gitlab/custom_hooks/hooks.log",
    level=logging.INFO,
    format="%Y-%m-%d %H:%M:%S %p",
    datefmt="%(asctime)s - %(levelname)s - %(message)s"
)


# pre-receive Trigger
class ReceiveTrigger(object):

    def __init__(self):
        # 格式：type(功能模块)：message
        self.pattern = "(feat|fix|test|refactor|docs|style|chroe|perf|revert|ci|build)\\(.*\\):( ).*"
        # GMT格式：Fri Feb 21 15:16:07 2020 +0800
        self.gmt_format = '%a %b %d %H:%M:%S %Y +0800'
        # 需要验证的分支,多个用|间隔
        self.branch = "dev"
        # 删除/新增 时的commitId
        self.base_commit_id = "0000000000000000000000000000000000000000"

    # 推送成功返回消息文本
    @staticmethod
    def push_success_back():
        print("push success！！！")
        sys.exit(0)

    # 格式检查推送消息失败返回
    @staticmethod
    def push_style_fail_back():
        print("##################################################################")
        print("##                                                              ##")
        print("## push message style check failed!                             ##")
        print("##                                                              ##")
        print("## type must be one of [feat,fix,docs,style,refactor,test,chore,##")
        print("## perf,revert,ci,build]                                        ##")
        print("## Example:                                                     ##")
        print("##   feat(user): add the user login.                            ##")
        print("##                                                              ##")
        print("##################################################################")
        sys.exit(1)

    # 消息长度检查推送消息失败返回
    @staticmethod
    def push_message_len_fail_back():
        print("#########################################")
        print("##                                     ##")
        print("## push message length check failed!   ##")
        print("##                                     ##")
        print("## message must be more 5 and less 100 ##")
        print("##                                     ##")
        print("#########################################")
        sys.exit(1)

    # 获取提交的git信息
    def get_git_push_info(self):
        # 获取提交的git信息<old-value> <new-value> <ref-name>:<旧的commitId><新的commitId><引用名称>
        old_value, new_value, ref_name = sys.stdin.readline().strip().split(' ')
        logging.debug("git提交信息：", sys.stdin.readline().strip())
        branch = str(ref_name).split("/")[2]
        if old_value == self.base_commit_id or new_value == self.base_commit_id:
            self.push_success_back()
        # 验证指定分支，去掉则验证所有分支
        # elif branch in self.branch:
            self.get_push_info(old_value, new_value)
        else:
            self.push_success_back()

    # 获取推送消息
    def get_push_info(self, old_value, new_value):
        """
        git show命令获取push作者，时间， 提交的日志，以及文件列表
        文件的路径为相对于版本库根目录的一个相对路径
        """
        rev = subprocess.Popen('git rev-list ' + new_value, shell=True, stdout=subprocess.PIPE)
        _revList = rev.stdout.readlines()
        _revList = [x.strip() for x in _revList]
        # 查找从上次提交old_value之后还有多少次提交，即本次push提交的object列表
        index_old = _revList.index(old_value.encode("utf-8"))
        push_list = _revList[:index_old]
        # 循环获取每次提交的文件列表
        for pObject in push_list:
            p = subprocess.Popen('git show ' + pObject.decode("utf-8"), shell=True, stdout=subprocess.PIPE)
            pipe = p.stdout.readlines()
            # pipe = [x.strip() for x in pipe]
            # push_author = pipe[1].decode("utf-8").strip("Author:").strip()
            # push_time = pipe[2].decode("utf-8").strip("Date:").strip()
            # push_msg = pipe[4].decode("utf-8").strip()
            # 获取文件列表
            # self.fileList.extend(['/'.join(fileName.split("/")[1:]) for fileName in pipe if
            #                       fileName.startswith("+++") and not fileName.endswith("null")])
            result_pipe = self.parse_pipe(pipe)
            push_msg = result_pipe["push_msg"]
            print("推送时间:", datetime.strptime(result_pipe["push_time"], self.gmt_format))
            print("推送作者:", result_pipe["push_author"])
            print("推送日志信息:", push_msg)
            logging.debug("推送日志信息：", push_msg)
            # 判断如果是Merge或者Revert开头的测排除验证
            if not push_msg.startswith("Merge") | push_msg.startswith("Revert"):
                # 验证消息格式
                if re.match(self.pattern, push_msg, re.M | re.I):
                    # 验证message信息字符长度范围
                    msg_arr = push_msg.split(":")
                    if 5 < len(msg_arr[1]) < 100:
                        continue
                    else:
                        self.push_message_len_fail_back()
                else:
                    self.push_style_fail_back()
        self.push_success_back()

    # 解析提交信息
    @staticmethod
    def parse_pipe(pipe):
        result = {}
        print("pipe= %s" % pipe)
        for x in pipe:
            temp = x.strip().decode("utf-8", "ignore")
            if temp.startswith("Author"):
                result["push_author"] = temp.strip("Author:").strip()
            elif temp.startswith("Date"):
                result["push_time"] = temp.strip("Date:").strip()
        result["push_msg"] = pipe[pipe.index(b"\n") + 1].decode("utf-8").strip()
        return result


if __name__ == "__main__":
    receive = ReceiveTrigger()
    receive.get_git_push_info()
