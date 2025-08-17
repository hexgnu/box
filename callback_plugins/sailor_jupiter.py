#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sailor Jupiter themed Ansible callback plugin
Makes your Ansible output magical! ✨⚡🌸
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
    Sailor Jupiter themed output callback plugin
    """
    
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'sailor_jupiter'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.sparkles = ['✨', '⚡', '🌸', '🌹', '💚', '⭐', '🌟', '💫']
        self.attacks = [
            "Supreme Thunder!",
            "Sparkling Wide Pressure!",
            "Jupiter Thunder Crash!",
            "Jupiter Oak Evolution!",
            "Flower Hurricane!",
            "Jupiter Coconut Cyclone!"
        ]
        self.task_count = 0
        
    def _print_sparkle_line(self, length=80):
        """Print a line of magical sparkles"""
        line = ' '.join(random.choice(self.sparkles) for _ in range(length // 3))
        self._display.display(stringc(line, 'bright green'))
        
    def _print_jupiter_banner(self, msg, color='bright green'):
        """Print a Sailor Jupiter themed banner"""
        width = 80
        
        # Sparkle border
        sparkle_border = '⚡' + '═' * (width - 2) + '⚡'
        
        self._display.display(stringc(sparkle_border, 'yellow'))
        
        # Add sparkles to the message
        sparkled_msg = f"✨ {msg} ✨"
        centered_msg = sparkled_msg.center(width)
        self._display.display(stringc(centered_msg, color))
        self._display.display(stringc(sparkle_border, 'yellow'))

    def v2_playbook_on_start(self, playbook):
        """Called when the playbook starts"""
        self._display.display("")
        
        # Sailor Jupiter ASCII art
        art = """
            ⚡️✨ SAILOR JUPITER SYSTEM CONFIG ✨⚡️
                      
                    ╭──────────╮
                   │ ◉   ⚡   ◉ │
                  ╱ ╲          ╱ ╲
                 │   ╲  🌹   ╱   │
                │  ●    ><    ●  │
                │    ╲  ‿  ╱    │
                 ╲     ──     ╱
                  ╲__________╱
                   │  ⚡⚡  │
                 ╭─┴──────┴─╮
                │ MAKOTO KINO │
                 ╲___________╱
        """
        
        for line in art.split('\n'):
            if '⚡' in line:
                self._display.display(stringc(line, 'yellow'))
            elif '●' in line or '◉' in line:
                self._display.display(stringc(line, 'bright green'))
            elif 'MAKOTO' in line or 'SAILOR' in line:
                self._display.display(stringc(line, 'bright green'))
            else:
                self._display.display(stringc(line, 'white'))
            time.sleep(0.02)
        
        self._display.display("")
        self._print_jupiter_banner("Protected by Jupiter, Guardian of Thunder!", 'bright green')
        
        # Random attack announcement
        attack = random.choice(self.attacks)
        self._display.display("")
        self._display.display(stringc(f"        ⚡ {attack} ⚡", 'yellow'))
        self._display.display("")

    def v2_playbook_on_play_start(self, play):
        """Called when a play starts"""
        name = play.get_name().strip()
        if name:
            self._print_jupiter_banner(f"🌸 PLAY: {name} 🌸", 'bright cyan')
        else:
            self._print_jupiter_banner("🌸 INITIATING PLAY 🌸", 'bright cyan')
        
        # Add some sparkles
        self._print_sparkle_line(40)

    def v2_playbook_on_task_start(self, task, is_conditional):
        """Called when a task starts"""
        task_name = task.get_name().strip()
        self.task_count += 1
        
        # Add sparkle effects periodically
        if self.task_count % 5 == 0:
            sparkles = ' '.join(random.choice(self.sparkles) for _ in range(10))
            self._display.display(stringc(sparkles, 'bright magenta'))
        
        prefix = "⚡ "
        if is_conditional:
            prefix = "🌸 [CONDITIONAL] "
            
        msg = f"{prefix}{task_name}"
        self._display.display(stringc(msg, 'cyan'))

    def v2_runner_on_ok(self, result):
        """Called when a task succeeds"""
        host = result._host.get_name()
        task = result._task.get_name()
        
        if result.is_changed():
            symbol = "✨"
            color = 'bright yellow'
            status = "TRANSFORMED"
        else:
            symbol = "💚"
            color = 'bright green'
            status = "PROTECTED"
            
        msg = f"  {symbol} [{status}] {host} | {task}"
        self._display.display(stringc(msg, color))

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Called when a task fails"""
        host = result._host.get_name()
        task = result._task.get_name()
        
        if ignore_errors:
            symbol = "🌙"
            color = 'yellow'
            status = "MOON HEALING"
        else:
            symbol = "💔"
            color = 'bright red'
            status = "NEEDS HEALING"
            
        msg = f"  {symbol} [{status}] {host} | {task}"
        self._display.display(stringc(msg, color))
        
        if 'msg' in result._result:
            error_msg = result._result['msg']
            self._display.display(stringc(f"    Evil Energy Detected: {error_msg}", 'red'))

    def v2_runner_on_skipped(self, result):
        """Called when a task is skipped"""
        host = result._host.get_name()
        task = result._task.get_name()
        
        msg = f"  🌙 [PASSED BY] {host} | {task}"
        self._display.display(stringc(msg, 'bright black'))

    def v2_playbook_on_stats(self, stats):
        """Called at the end of the playbook with stats"""
        self._display.display("")
        self._print_jupiter_banner("✨ TRANSFORMATION COMPLETE ✨", 'bright green')
        
        hosts = sorted(stats.processed.keys())
        for host in hosts:
            stat = stats.summarize(host)
            
            # Build status line with Sailor Jupiter themes
            status_parts = []
            if stat['ok'] > 0:
                status_parts.append(stringc(f"💚 PROTECTED={stat['ok']}", 'bright green'))
            if stat['changed'] > 0:
                status_parts.append(stringc(f"✨ TRANSFORMED={stat['changed']}", 'yellow'))
            if stat['failures'] > 0:
                status_parts.append(stringc(f"💔 FAILED={stat['failures']}", 'red'))
            if stat['skipped'] > 0:
                status_parts.append(stringc(f"🌙 SKIPPED={stat['skipped']}", 'cyan'))
                
            status_line = " | ".join(status_parts)
            self._display.display(f"  [{host}]: {status_line}")
        
        # Epic finale with sparkles
        self._display.display("")
        for _ in range(3):
            self._print_sparkle_line(60)
            time.sleep(0.05)
            
        # Final Sailor Jupiter message
        self._display.display("")
        self._display.display(stringc("    🌸 'In the name of Jupiter, I'll punish you!' 🌸", 'bright green'))
        self._display.display(stringc("         ⚡ System Configuration Complete! ⚡", 'yellow'))
        self._display.display("")