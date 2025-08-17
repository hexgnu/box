#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Matrix-style Ansible callback plugin
Makes your Ansible output look like you're in The Matrix
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import random
import time
import sys
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import stringc

class CallbackModule(CallbackBase):
    """
    Matrix-style output callback plugin
    """
    
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'matrix'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.matrix_chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ01"
        self.colors = ['green', 'bright green', 'white']
        self.task_count = 0
        
    def _print_matrix_line(self, length=80):
        """Print a line of Matrix rain"""
        line = ''.join(random.choice(self.matrix_chars) for _ in range(length))
        color = random.choice(self.colors)
        self._display.display(stringc(line, color))
        
    def _print_banner(self, msg, color='bright green'):
        """Print a l33t banner"""
        width = 80
        border = "=" * width
        
        # Random Matrix rain before banner
        for _ in range(2):
            self._print_matrix_line()
            time.sleep(0.01)
            
        self._display.display(stringc(border, 'green'))
        
        # Convert to l33t speak
        l33t_msg = msg.replace('E', '3').replace('e', '3')
        l33t_msg = l33t_msg.replace('A', '4').replace('a', '4')
        l33t_msg = l33t_msg.replace('S', '5').replace('s', '5')
        l33t_msg = l33t_msg.replace('O', '0').replace('o', '0')
        l33t_msg = l33t_msg.replace('I', '1').replace('i', '1')
        l33t_msg = l33t_msg.replace('T', '7').replace('t', '7')
        
        centered_msg = l33t_msg.center(width)
        self._display.display(stringc(centered_msg, color))
        self._display.display(stringc(border, 'green'))
        
        # More Matrix rain after
        for _ in range(2):
            self._print_matrix_line()
            time.sleep(0.01)

    def v2_runner_on_start(self, host, task):
        """Called when a task starts executing"""
        self.task_count += 1
        
        # Matrix effect every few tasks
        if self.task_count % 3 == 0:
            for _ in range(3):
                self._print_matrix_line()
                time.sleep(0.02)

    def v2_playbook_on_start(self, playbook):
        """Called when the playbook starts"""
        self._display.display("")
        ascii_art = """
        ███╗   ███╗ █████╗ ████████╗██████╗ ██╗██╗  ██╗
        ████╗ ████║██╔══██╗╚══██╔══╝██╔══██╗██║╚██╗██╔╝
        ██╔████╔██║███████║   ██║   ██████╔╝██║ ╚███╔╝ 
        ██║╚██╔╝██║██╔══██║   ██║   ██╔══██╗██║ ██╔██╗ 
        ██║ ╚═╝ ██║██║  ██║   ██║   ██║  ██║██║██╔╝ ██╗
        ╚═╝     ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝
                    4N51BL3 PL4YB00K 3X3CU710N
        """
        for line in ascii_art.split('\n'):
            self._display.display(stringc(line, 'bright green'))
            time.sleep(0.05)
        
        self._display.display("")
        self._print_banner("W3LC0M3 70 7H3 M47R1X", 'bright green')
        self._display.display("")

    def v2_playbook_on_play_start(self, play):
        """Called when a play starts"""
        name = play.get_name().strip()
        if name:
            self._print_banner(f"1N171471Z1NG PL4Y: {name}", 'bright cyan')
        else:
            self._print_banner("1N171471Z1NG PL4Y", 'bright cyan')

    def v2_playbook_on_task_start(self, task, is_conditional):
        """Called when a task starts"""
        task_name = task.get_name().strip()
        
        # Add Matrix rain effect randomly
        if random.random() > 0.7:
            self._print_matrix_line()
            
        prefix = "▶ [7A5K] "
        if is_conditional:
            prefix = "▶ [C0ND1710N4L] "
            
        msg = f"{prefix}{task_name}"
        self._display.display(stringc(msg, 'cyan'))

    def v2_runner_on_ok(self, result):
        """Called when a task succeeds"""
        host = result._host.get_name()
        task = result._task.get_name()
        
        if result.is_changed():
            symbol = "✓✓"
            color = 'bright yellow'
            status = "CH4NG3D"
        else:
            symbol = "✓"
            color = 'bright green'
            status = "0K"
            
        msg = f"  {symbol} [{status}] {host} | {task}"
        self._display.display(stringc(msg, color))
        
        # Random Matrix char at the end
        if random.random() > 0.8:
            trail = ''.join(random.choice(self.matrix_chars) for _ in range(20))
            self._display.display(stringc(f"    {trail}", 'dark gray'))

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Called when a task fails"""
        host = result._host.get_name()
        task = result._task.get_name()
        
        if ignore_errors:
            symbol = "⚠"
            color = 'yellow'
            status = "1GN0R3D"
        else:
            symbol = "✗"
            color = 'bright red'
            status = "F41L3D"
            
        msg = f"  {symbol} [{status}] {host} | {task}"
        self._display.display(stringc(msg, color))
        
        # Error details in Matrix style
        if 'msg' in result._result:
            error_msg = result._result['msg']
            self._display.display(stringc(f"    3RR0R: {error_msg}", 'red'))

    def v2_runner_on_skipped(self, result):
        """Called when a task is skipped"""
        host = result._host.get_name()
        task = result._task.get_name()
        
        msg = f"  ⊘ [5K1PP3D] {host} | {task}"
        self._display.display(stringc(msg, 'bright black'))

    def v2_playbook_on_stats(self, stats):
        """Called at the end of the playbook with stats"""
        self._display.display("")
        self._print_banner("3X3CU710N C0MPL373", 'bright green')
        
        hosts = sorted(stats.processed.keys())
        for host in hosts:
            stat = stats.summarize(host)
            
            # Build status line with l33t speak
            status_parts = []
            if stat['ok'] > 0:
                status_parts.append(stringc(f"0K={stat['ok']}", 'bright green'))
            if stat['changed'] > 0:
                status_parts.append(stringc(f"CH4NG3D={stat['changed']}", 'yellow'))
            if stat['failures'] > 0:
                status_parts.append(stringc(f"F41L3D={stat['failures']}", 'red'))
            if stat['skipped'] > 0:
                status_parts.append(stringc(f"5K1PP3D={stat['skipped']}", 'cyan'))
                
            status_line = " | ".join(status_parts)
            self._display.display(f"  [{host}]: {status_line}")
        
        # Epic Matrix rain finale
        self._display.display("")
        for _ in range(5):
            self._print_matrix_line()
            time.sleep(0.02)
            
        # Final message
        self._display.display("")
        self._display.display(stringc("7H3 M47R1X H45 Y0U...", 'bright green'))
        self._display.display("")