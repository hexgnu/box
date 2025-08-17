#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Matrix notification callback plugin for Ansible
Sends playbook execution events to a Matrix room
"""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
    callback: matrix_notifier
    type: notification
    short_description: Send Ansible events to Matrix room
    description:
      - This callback plugin sends notifications about playbook executions to a Matrix room
      - Supports authentication via access token
      - Sends formatted messages with task status and results
    version_added: "2.0"
    requirements:
      - matrix-nio Python library (pip install matrix-nio)
      - Configured Matrix homeserver and room ID
    options:
      homeserver:
        description: Matrix homeserver URL
        env: MATRIX_HOMESERVER
        default: https://matrix.org
        type: str
      access_token:
        description: Matrix access token for authentication
        env: MATRIX_ACCESS_TOKEN
        required: true
        type: str
      room_id:
        description: Matrix room ID to send messages to
        env: MATRIX_ROOM_ID
        required: true
        type: str
      notify_on_start:
        description: Send notification when playbook starts
        env: MATRIX_NOTIFY_START
        default: true
        type: bool
      notify_on_success:
        description: Send notification on successful tasks
        env: MATRIX_NOTIFY_SUCCESS
        default: false
        type: bool
      notify_on_failure:
        description: Send notification on failed tasks
        env: MATRIX_NOTIFY_FAILURE
        default: true
        type: bool
      notify_on_complete:
        description: Send summary when playbook completes
        env: MATRIX_NOTIFY_COMPLETE
        default: true
        type: bool
'''

import os
import json
import time
import socket
import getpass
from datetime import datetime
from ansible.plugins.callback import CallbackBase
from ansible.utils.color import stringc

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

class CallbackModule(CallbackBase):
    """
    Matrix notification callback plugin
    """
    
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'matrix_notifier'
    CALLBACK_NEEDS_WHITELIST = True

    def __init__(self):
        super(CallbackModule, self).__init__()
        self.disabled = False
        self.playbook_name = None
        self.start_time = None
        self.hostname = socket.gethostname()
        self.username = getpass.getuser()
        self.task_results = {
            'ok': 0,
            'changed': 0,
            'failed': 0,
            'skipped': 0,
            'unreachable': 0
        }
        self.failed_tasks = []
        
    def set_options(self, task_keys=None, var_options=None, direct=None):
        """Set options from environment variables or ansible.cfg"""
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)
        
        # Get configuration from environment or ansible.cfg
        self.homeserver = os.getenv('MATRIX_HOMESERVER', 'https://matrix.org')
        self.access_token = os.getenv('MATRIX_ACCESS_TOKEN')
        self.room_id = os.getenv('MATRIX_ROOM_ID')
        
        # Notification preferences
        self.notify_on_start = os.getenv('MATRIX_NOTIFY_START', 'true').lower() == 'true'
        self.notify_on_success = os.getenv('MATRIX_NOTIFY_SUCCESS', 'false').lower() == 'true'
        self.notify_on_failure = os.getenv('MATRIX_NOTIFY_FAILURE', 'true').lower() == 'true'
        self.notify_on_complete = os.getenv('MATRIX_NOTIFY_COMPLETE', 'true').lower() == 'true'
        
        # Validate requirements
        if not HAS_REQUESTS:
            self._display.warning('Matrix callback disabled: requests library not installed')
            self.disabled = True
            return
            
        if not self.access_token or not self.room_id:
            self._display.warning('Matrix callback disabled: MATRIX_ACCESS_TOKEN and MATRIX_ROOM_ID required')
            self.disabled = True
            return
            
        # Clean up room ID format if needed
        if not self.room_id.startswith('!'):
            self._display.warning(f'Invalid room ID format: {self.room_id}. Room IDs should start with !')
            self.disabled = True

    def _send_message(self, message, formatted_message=None):
        """Send a message to the Matrix room"""
        if self.disabled:
            return
            
        url = f"{self.homeserver}/_matrix/client/r0/rooms/{self.room_id}/send/m.room.message"
        
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        # Prepare message body
        body = {
            'msgtype': 'm.text',
            'body': message
        }
        
        # Add formatted message if provided (HTML)
        if formatted_message:
            body['format'] = 'org.matrix.custom.html'
            body['formatted_body'] = formatted_message
        
        try:
            response = requests.post(url, json=body, headers=headers, timeout=10)
            if response.status_code not in [200, 201]:
                self._display.warning(f'Failed to send Matrix message: {response.status_code} - {response.text}')
        except Exception as e:
            self._display.warning(f'Error sending Matrix message: {str(e)}')

    def _format_duration(self, seconds):
        """Format duration in human-readable format"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            return f"{seconds/60:.1f}m"
        else:
            return f"{seconds/3600:.1f}h"

    def v2_playbook_on_start(self, playbook):
        """Called when the playbook starts"""
        if self.disabled or not self.notify_on_start:
            return
            
        self.playbook_name = os.path.basename(playbook._file_name)
        self.start_time = time.time()
        
        # Plain text message
        message = f"🚀 Ansible Playbook Started\n"
        message += f"📋 Playbook: {self.playbook_name}\n"
        message += f"🖥️ Host: {self.hostname}\n"
        message += f"👤 User: {self.username}\n"
        message += f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # HTML formatted message
        formatted = f"<h4>🚀 Ansible Playbook Started</h4>"
        formatted += f"<ul>"
        formatted += f"<li><b>Playbook:</b> <code>{self.playbook_name}</code></li>"
        formatted += f"<li><b>Host:</b> {self.hostname}</li>"
        formatted += f"<li><b>User:</b> {self.username}</li>"
        formatted += f"<li><b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>"
        formatted += f"</ul>"
        
        self._send_message(message, formatted)

    def v2_runner_on_ok(self, result):
        """Called when a task succeeds"""
        if result.is_changed():
            self.task_results['changed'] += 1
        else:
            self.task_results['ok'] += 1
            
        if self.disabled or not self.notify_on_success:
            return
            
        host = result._host.get_name()
        task = result._task.get_name()
        
        if result.is_changed():
            status_emoji = "✨"
            status_text = "CHANGED"
        else:
            status_emoji = "✅"
            status_text = "OK"
            
        message = f"{status_emoji} Task {status_text}: {task} on {host}"
        self._send_message(message)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        """Called when a task fails"""
        if not ignore_errors:
            self.task_results['failed'] += 1
            
        host = result._host.get_name()
        task = result._task.get_name()
        
        # Store failed task info
        error_msg = result._result.get('msg', 'Unknown error')
        self.failed_tasks.append({
            'host': host,
            'task': task,
            'error': error_msg,
            'ignored': ignore_errors
        })
        
        if self.disabled or not self.notify_on_failure:
            return
            
        # Build error message
        message = f"❌ Task FAILED: {task} on {host}\n"
        message += f"Error: {error_msg}"
        
        # HTML formatted message with more details
        formatted = f"<h4>❌ Task Failed</h4>"
        formatted += f"<ul>"
        formatted += f"<li><b>Task:</b> {task}</li>"
        formatted += f"<li><b>Host:</b> {host}</li>"
        formatted += f"<li><b>Error:</b> <code>{error_msg}</code></li>"
        
        if 'stderr' in result._result and result._result['stderr']:
            formatted += f"<li><b>Stderr:</b> <pre>{result._result['stderr']}</pre></li>"
            
        formatted += f"</ul>"
        
        if ignore_errors:
            message += "\n(Error ignored)"
            formatted += "<p><i>Error was ignored</i></p>"
        
        self._send_message(message, formatted)

    def v2_runner_on_skipped(self, result):
        """Called when a task is skipped"""
        self.task_results['skipped'] += 1

    def v2_runner_on_unreachable(self, result):
        """Called when a host is unreachable"""
        self.task_results['unreachable'] += 1
        
        if self.disabled or not self.notify_on_failure:
            return
            
        host = result._host.get_name()
        task = result._task.get_name()
        
        message = f"🔌 Host UNREACHABLE: {host} during task: {task}"
        self._send_message(message)

    def v2_playbook_on_stats(self, stats):
        """Called at the end of the playbook with stats"""
        if self.disabled or not self.notify_on_complete:
            return
            
        # Calculate duration
        duration = time.time() - self.start_time if self.start_time else 0
        duration_str = self._format_duration(duration)
        
        # Determine overall status
        if self.task_results['failed'] > 0 or self.task_results['unreachable'] > 0:
            status_emoji = "❌"
            status_text = "FAILED"
            status_color = "#FF0000"
        elif self.task_results['changed'] > 0:
            status_emoji = "✨"
            status_text = "CHANGED"
            status_color = "#FFA500"
        else:
            status_emoji = "✅"
            status_text = "SUCCESS"
            status_color = "#00FF00"
        
        # Build summary message
        message = f"{status_emoji} Ansible Playbook {status_text}\n"
        message += f"📋 Playbook: {self.playbook_name}\n"
        message += f"⏱️ Duration: {duration_str}\n"
        message += f"\n📊 Results:\n"
        message += f"  ✅ OK: {self.task_results['ok']}\n"
        message += f"  ✨ Changed: {self.task_results['changed']}\n"
        message += f"  ❌ Failed: {self.task_results['failed']}\n"
        message += f"  ⏭️ Skipped: {self.task_results['skipped']}\n"
        message += f"  🔌 Unreachable: {self.task_results['unreachable']}"
        
        # HTML formatted message
        formatted = f"<h3 style='color: {status_color}'>{status_emoji} Ansible Playbook {status_text}</h3>"
        formatted += f"<ul>"
        formatted += f"<li><b>Playbook:</b> <code>{self.playbook_name}</code></li>"
        formatted += f"<li><b>Duration:</b> {duration_str}</li>"
        formatted += f"</ul>"
        
        formatted += f"<h4>📊 Results Summary</h4>"
        formatted += f"<table>"
        formatted += f"<tr><td>✅ OK:</td><td>{self.task_results['ok']}</td></tr>"
        formatted += f"<tr><td>✨ Changed:</td><td>{self.task_results['changed']}</td></tr>"
        formatted += f"<tr><td>❌ Failed:</td><td>{self.task_results['failed']}</td></tr>"
        formatted += f"<tr><td>⏭️ Skipped:</td><td>{self.task_results['skipped']}</td></tr>"
        formatted += f"<tr><td>🔌 Unreachable:</td><td>{self.task_results['unreachable']}</td></tr>"
        formatted += f"</table>"
        
        # Add failed tasks details if any
        if self.failed_tasks:
            message += "\n\n⚠️ Failed Tasks:"
            formatted += f"<h4>⚠️ Failed Tasks</h4><ul>"
            
            for task_info in self.failed_tasks:
                ignored_text = " (ignored)" if task_info['ignored'] else ""
                message += f"\n  • {task_info['task']} on {task_info['host']}{ignored_text}"
                formatted += f"<li><b>{task_info['task']}</b> on {task_info['host']}{ignored_text}<br/>"
                formatted += f"<code>{task_info['error']}</code></li>"
                
            formatted += "</ul>"
        
        # Add host summary
        hosts_summary = []
        for host in sorted(stats.processed.keys()):
            host_stats = stats.summarize(host)
            if host_stats['failures'] > 0 or host_stats['unreachable'] > 0:
                host_status = "❌"
            elif host_stats['changed'] > 0:
                host_status = "✨"
            else:
                host_status = "✅"
            hosts_summary.append(f"{host_status} {host}")
        
        if hosts_summary:
            message += f"\n\n🖥️ Hosts: {', '.join(hosts_summary)}"
            formatted += f"<h4>🖥️ Host Status</h4>"
            formatted += f"<p>{', '.join(hosts_summary)}</p>"
        
        self._send_message(message, formatted)