# -*- coding: utf-8 -*-

import urllib.request
import urllib.parse
import threading
import sublime
import json
import time
import re

from .. import common, log, TabsView
from .  import config

_res_re = re.compile(r'<td><a href="#" id="result"><input type="hidden" value="(.*)"><input type="hidden" value="(\d{4,})"><input type="hidden" id="submitTime" value="(\d+)">((\d+)/(\d+)|点击查看)</a></td>')
_isw_re = re.compile(r'<td><a href="showproblem\?id=\d{4,}">\d{4,}</a></td>\s*<td>([a-zA-Z ]*)</td>')

res_url = config.root_url + '/allmysubmits'
det_url = config.root_url + '/showresult'

result_link = {
    'Accept':                                                           'Accepted',
    'Wrong_Answer':                                                     'Wrong Answer',
    'compile_error':                                                    'Compile Error',
    'monitor_time_limit_exceeded9(超时)':                               'Time Limit Exceeded',
    'monitor_segment_error(段错误,爆内存或爆栈?)':                      'Runtime Error',
    'monitor_file_name_error(你的文件名出错了?)':                       'File Name Error',
    'monitor_memory_limit_exceeded':                                    'Memory Limit Exceeded',
    'monitor_SIGFPE_error(算术运算错误,除数是0?浮点运算出错？溢出？)':  'SIGFPE Error',
    'monitor_time_limit_exceeded14(超时,没用文件操作或者你的程序崩溃)': 'Output Limit Exceeded'
    # monitor_invalid_syscall_id                          Restrict Function
    # 测评机出错--无法清空沙箱或者无法复制文件.in到沙箱   No Data
}

class ResultThreading(threading.Thread):
    def __init__(self, opener, view):
        self.opener  = opener
        self.view    = view
        self.result  = None
        threading.Thread.__init__(self)

    def new_file(self):
        return self.view.window().new_file()


    def getName(self, st):
        if st[:3] == 'goc':
            st = st[3:]
        try:
            if len(st) >= 26 and st[:26] == 'monitor_invalid_syscall_id':
                return 'Restrict Function'
            if len(st) >= 21 and st[:21] == '测评机出错--无法清空沙箱或者无法复制文件':
                return 'No Data'
            return result_link[st]
        except:
            return st

    def separate(self, result):
        temp = result.split(';')
        result = []
        for item in temp:
            result.append(item.split(':'))
        result = result[:-1]
        return result

    def print_compile_info(self, view, compile):
        view.add_line('Compile INFO :')
        view.add_line(compile.replace('\r', '\n'))

    def print_head(self, view, head):
        tot_len = 0
        for i in range(0, 4):
            tot_len += len(head[i])+2
        view.add_line('-'*(tot_len+5))
        view.add_line('| %s | %s | %s | %s |' % (head[0], head[1], head[2], head[3]))
        view.add_line('%s%s%s' % ('|', '-'*(tot_len+3), '|'))

    def printer(self, result, problem, score, compile_info=None):
        result = self.separate(result)
        fix     = [0       ,  0     , 3     , 3       ]
        head    = ['Result', 'Score', 'Time', 'Memory']
        max_len = [len(head[i]) for i in range(0, 4)]
        for item in result:
            root_result = self.getName(item[0])
            if root_result != 'Accepted':
                break
        log.info('Status: %s %s' % (root_result, score))
        for item in result:
            item[0] = self.getName(item[0])
            item[2] = item[2].replace('不可用', 'NaN')
            item[3] = item[3].replace('不可用', 'NaN')
            for i in range(0, 4):
                max_len[i] = max(max_len[i], len(item[i])+2)
        for i in range(0, 4):
            head[i] = head[i].center(max_len[i] + fix[i])
        for item in result:
            item[0] = item[0].center(max_len[0])
            item[1] = item[1].rjust (max_len[1])
            item[2] = item[2].rjust (max_len[2])
            item[3] = item[3].rjust (max_len[3])
        view = TabsView.SmojResultView('Result')
        view.create_view()
        view.add_line('Problem ID : %s' % str(problem))
        view.add_line(common.getFiglet(root_result))
        if compile_info:
            self.print_compile_info(view, compile_info)
        view.add_line('Result        -> %s <-' % score)
        self.print_head(view, head)
        for item in result:
            view.add_line('| %s | %-3s | %s ms | %s KB |' % (item[0], item[1], item[2], item[3]))
        view.add_line('-%s-%s-%s-%s-' % ((len(head[0])+2)*'-', (len(head[1])+2)*'-', (len(head[2])+2)*'-', (len(head[3])+2)*'-'))

    def wait_judge(self):
        name, problem, stamp, score = None, None, None, None
        while True:
            sublime.status_message('Waiting for judging...')
            r = urllib.request.Request(url=res_url, headers=common.headers)
            response = self.opener.open(r)
            tmp = response.read()
            html = ''
            while tmp:
                html += tmp.decode()
                tmp = response.read()
            m = _isw_re.search(html)
            if name is None:
                match = _res_re.search(html)
                name    = match.group(1)
                problem = match.group(2)
                stamp   = match.group(3)
            if m.group(1) == 'done':
                match = _res_re.search(html)
                score = match.group(4)
                break
            time.sleep(1)
        return name, problem, stamp, score


    def run(self):
        name, problem, stamp, score = self.wait_judge()
        sublime.status_message('Loading result...')
        values = {'submitTime':stamp, 'pid':problem, 'user': name}
        r = urllib.request.Request(url=det_url, data=urllib.parse.urlencode(values).encode(), headers=common.headers)
        response = self.opener.open(r)
        result = json.loads(response.read().decode())
        if result['result'] == 'OI_MODE':
            sublime.status_message('This is an OI-MODE problem')
            self.result = True
            return None
        compile_info = None
        try:
            compile_info = result['compileInfo'][0]
        except:
            pass
        self.printer(result['result'].replace('\n', ''), problem, score, compile_info)
