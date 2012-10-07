"""

UpdateRepo.py

  Commits updates in a local directory to a github repo

  You can arbitrarily more subdirectories and files of any kind.

  All of them will get added.

  Old directories and files do not get deleted on the repo.
  So if there are things you explicitly want to go away
  you will need to do that manually. 

  Sun Sep 30 09:13:35 EDT 2012 

  Bob Coggeshall 

  re_novalabs (at) cogwheel.com


"""

LocalDir = r'C:\Users\drogg\Desktop\GitNovaLabs'
RepoName = 'LaserCut'
GitSSH = 'git@github.com:nova-labs-tools'
RepoOwner = 'nova-labs-tools'
GitBinPath =   'c:\\Program\\\ Files\\Git\\bin\\'
GitUserName = '"Nova Labs Laser PC"'
GitUserEmail = '"info@nova-labs.org"'

import os
import sys
import subprocess
import shlex
import re
from colorama import Fore, Back, Style
from colorama import init as colorama_init
from time import gmtime, strftime



Red = Style.BRIGHT  + Fore.RED 
Green = Style.BRIGHT  + Fore.GREEN

def Exit():
  "Pause window and allow human to read results"
  try:
    i = input('\nPress enter to close window->:')
  except:
    pass
  os._exit(0)
  return 0 # not reached


# Git requires us to make initial contact via ssh
def LogIntoGit():
  "Log into Git "
  # we need to supply a token to git
  DoCmd('ssh git@github.com',1)
  return 1

def Chdir(dir):
  " Change to directory dir. Exit fail, otherwise return 1 Colorized messages "
  print '\n-----\n' + Green + 'chdir ' + dir
  try:
    os.chdir(dir)
  except OSError as e:
    print Red + "ERROR %s: %s" % ('chdir('+LocalDir+'):', e.strerror)
    Exit()
  return 1

def DoCmd(cmd,ignore_exit_code=0):
  " Execute command cmd. Exit on fail. Otherwise, return exit code Colorized messages"
  print '\n-----\n' + Green + cmd
  try:
    exitcode = subprocess.call(shlex.split(cmd),shell=True)

  except OSError as e:
    print Red + "ERROR %s: %s" % (cmd, e.strerror)
    Exit()

  except CalledProcessError,e:
    print Red + "ERROR %s: %s" % (cmd,e)
    Exit()

  if ignore_exit_code == 0 and exitcode != 0:
    print Red + cmd + ' ERROR: Exit Code: ' + repr(exitcode) + ' there might be a problem. See above'
    Exit()
  
  return exitcode


def AddToRepo():
  try:
    cmd = shlex.split('bash -c find .')
    findproc = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  except OSError as e:
    print Red + "ERROR %s: %s" % (cmd, e.strerror)
    Exit()

  except CalledProcessError,e:
    print Red + "ERROR %s: %s" % (cmd,e)
    Exit()

  for line in iter(findproc.stdout.readline,''):
    l = line.rstrip()
    if (re.match('./.git',l) is None):
      DoCmd('git add ' + l)
  return

def CheckIntoRepo():
  DoCmd('git config user.name ' + GitUserName)
  DoCmd('git config user.email ' + GitUserEmail)
  DoCmd('git remote rm origin')
  DoCmd('git remote add origin ' + GitSSH + '/' + RepoName + '.git')
  DoCmd('git commit -vam \'Update\'',ignore_exit_code=1)
  DoCmd('git push origin',ignore_exit_code=1)

def sethpath():
  "put bash utils in execute path ahead of everything so we don't get the wrong 'find', f'rinstance"
  path = os.environ['PATH'] + ':' + GitBinPath
  path = GitBinPath + ':' + path
  os.environ['PATH'] = path


  ##
 ## 
##  START HERE
##    
# colorized output fix
colorama_init(autoreset=True)
timestr = strftime("%d-%b-%Y-%H%M", gmtime())

oldsuf = '-precheck-in-' + timestr

# go to dir , remove work copy, save off local copy of repo
Chdir(LocalDir)
DoCmd('mv ' + RepoName + ' ' + RepoName + oldsuf)

# get on git, check out current copy
LogIntoGit()
DoCmd('git clone git@github.com:/' + RepoOwner + '/' + RepoName + '.git')
Chdir(RepoName + oldsuf)
# overlay our copy on git's
# couple of side-effects to note: This  copy always updates everything. Shouldn't be a problem unless someone checks in a bad copy.
# OK because we can always recover an old version
# Also, this will check in new directories and files, but it won't get rid of old ones. So there will need to be some
# periodic hand-cleaning
DoCmd('tar cvf ../tmp.tar --exclude  .git .')
Chdir('..')
Chdir(RepoName)
DoCmd('tar xf ../tmp.tar')
AddToRepo()
CheckIntoRepo()
Chdir('..')
DoCmd('rm  tmp.tar')
Exit()
