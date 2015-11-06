#!/usr/bin/env python
# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""
Python module for installing/removing the KeychainMinder mechanism
from the authorization database. Only designed for 10.8+.

This can either be used as a standalone script or imported and used
in another Python script.
"""

import argparse
import plistlib
import os
import subprocess
import sys


KEYCHAIN_MINDER_MECHANISM = 'KeychainMinder:check,privileged'
SCREENSAVER_RULE = 'authenticate-session-owner-or-admin'
SCREENSAVER_PRETTY_RULE = 'use-login-window-ui'

AUTHENTICATE_RIGHT = 'authenticate'
LOGIN_DONE_RIGHT = 'system.login.done'
SCREENSAVER_RIGHT = 'system.login.screensaver'


def _GetRightData(right):
  """Get the current configuration for the requested right as a dict."""
  output = subprocess.check_output(
      ['/usr/bin/security', 'authorizationdb', 'read', right],
      stderr=subprocess.PIPE)
  data = plistlib.readPlistFromString(output)
  return data


def _SetRightData(right, data):
  """Update the configuration for the requested right."""
  data = plistlib.writePlistToString(data)
  p = subprocess.Popen(
      ['/usr/bin/security', 'authorizationdb', 'write', right],
      stdin=subprocess.PIPE,
      stderr=subprocess.PIPE)
  _, stderr = p.communicate(input=data)
  return stderr.count('YES') == 1


def InstallPlugin():
  """Install the plugin to both rules and update screensaver right."""
  for right in [AUTHENTICATE_RIGHT, LOGIN_DONE_RIGHT]:
    data = _GetRightData(right)
    mechanisms = data.get('mechanisms', [])
    if not mechanisms.count(KEYCHAIN_MINDER_MECHANISM):
      mechanisms.append(KEYCHAIN_MINDER_MECHANISM)
      data['mechanisms'] = mechanisms
      if _SetRightData(right, data):
        print '%s: Mechanism installed.' % right
      else:
        print '%s: Failed to install mechanism' % right
    else:
      print '%s: Mechanism already installed.' % right

 # taking out login lock screen replacement - ks
 # data = _GetRightData(SCREENSAVER_RIGHT)
 # if data.get('rule') != [SCREENSAVER_RULE]:
 #   data['rule'] = [SCREENSAVER_RULE]
 #   if _SetRightData(SCREENSAVER_RIGHT, data):
 #     print '%s: Rule updated.' % SCREENSAVER_RIGHT
 #   else:
 #     print '%s: Failed to update rule.' % SCREENSAVER_RIGHT
 # else:
 #   print '%s: Rule already correct.' % SCREENSAVER_RIGHT


def RemovePlugin(restore_screensaver=False):
  """Remove the plugin from both rules."""
  for right in [AUTHENTICATE_RIGHT, LOGIN_DONE_RIGHT]:
    data = _GetRightData(right)
    mechanisms = data.get('mechanisms', [])
    if mechanisms.count(KEYCHAIN_MINDER_MECHANISM):
      mechanisms.remove(KEYCHAIN_MINDER_MECHANISM)
      data['mechanisms'] = mechanisms
      if _SetRightData(right, data):
        print '%s: Mechanism removed.' % right
      else:
        print '%s: Failed to remove mechanism.' % right
    else:
      print '%s: Mechanism already removed.' % right

    if restore_screensaver:
 #     data = _GetRightData(SCREENSAVER_RIGHT)
  		print 'No Screensaver Changes made'
 #     if data.get('rule') != [SCREENSAVER_PRETTY_RULE]:
 #       data['rule'] = [SCREENSAVER_PRETTY_RULE]
 #       if _SetRightData(SCREENSAVER_RIGHT, data):
 #         print '%s: Rule updated.' % SCREENSAVER_RIGHT
 #       else:
 #         print '%s: Failed to update rule.' % SCREENSAVER_RIGHT
 #     else:
 #       print '%s: Rule already correct.' % SCREENSAVER_RIGHT


def CheckForRoot():
  if not os.geteuid() == 0:
    sys.exit('This script requires root privileges')


def ParseOptions():
  parser = argparse.ArgumentParser()
  group = parser.add_mutually_exclusive_group(required=True)
  group.add_argument(
      '--install', action='store_true', dest='install', help='Install plugin')
  group.add_argument(
      '--remove', action='store_true', dest='remove', help='Remove plugin')
  group.add_argument(
      '--restore_screensaver', action='store_true', dest='restore_screensaver',
      help='Restore \'pretty\' screensaver UI')
  return parser.parse_args()


def main(argv):
  CheckForRoot()
  options = ParseOptions()
  if options.install:
    InstallPlugin()
  elif options.remove:
    RemovePlugin(restore_screensaver=options.restore_screensaver)
  elif options.restore_screensaver:
    RemovePlugin(restore_screensaver=True)


if __name__ == '__main__':
  main(sys.argv)
