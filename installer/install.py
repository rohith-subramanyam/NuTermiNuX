#!/usr/bin/env python2.7
"""Installer for terminux."""

import argparse
import datetime
import distutils.version
import glob
import logging
import os
import platform
import shutil
import subprocess
import sys


CENTOS = "CentOS"
MIN_VERSION = "6.9"
NUTERMINUX = "NuTermiNuX"
BREWDIR = "/home/linuxbrew/.linuxbrew/bin"
HOME = os.environ["HOME"]
BASHRC = os.path.join(HOME, ".bashrc")
VIMRC = os.path.join(HOME, ".vimrc")
VIMDIR = os.path.join(HOME, ".vim")
ZSHRC = os.path.join(HOME, ".zshrc")
logging.basicConfig(
    format="%(asctime)s %(name)s %(lineno)d %(levelname)-8s %(message)s",
    level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

def query_yes_no(question, default="no"):
  """Ask a yes/no question via raw_input() and return their answer.

  "question" is a string that is presented to the user.
  "default" is the presumed answer if the user just hits <Enter>.
      It must be "yes" (the default), "no" or None (meaning
      an answer is required of the user).

  The "answer" return value is True for "yes" or False for "no".
  """
  valid = {"yes": True, "y": True, "ye": True,
           "no": False, "n": False}
  if default is None:
    prompt = " [y/n] "
  elif default == "yes":
    prompt = " [Y/n] "
  elif default == "no":
    prompt = " [y/N] "
  else:
    raise ValueError("invalid default answer: '%s'" % default)

  while True:
    sys.stdout.write("%s%s" % (question, prompt))
    choice = raw_input().lower()
    if default is not None and choice == '':
      return valid[default]
    elif choice in valid:
      return valid[choice]
    else:
      sys.stdout.write("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")

def run_cmd(cmd, err=None):
  """Run the shell command and return err in case of a failure."""
  LOGGER.debug("Running %s", cmd)

  if err is None:
    err = "'%s' failed" % cmd

  ret = subprocess.call(cmd, shell=True)
  if ret:
    return err

  return None

def restore_file(file_path):
  """Restore the latest backup."""
  LOGGER.debug("Restoring %s", file_path)
  bkps = sorted(glob.glob("%s*.bkp" % file_path))
  if bkps:
    LOGGER.debug("backups: %s", bkps)
    shutil.move(os.path.join(bkps[-1]), file_path)

def uninstall():
  """Restore old configuration."""
  restore_file(VIMRC)
  restore_file(VIMDIR)
  restore_file(BASHRC)
  restore_file(ZSHRC)

def setup_terminux_config():
  """Setup terminux configuration."""
  dotfiles_dir = os.path.join(os.path.dirname(os.path.dirname(
      os.path.realpath(__file__))), "dotfiles")
  os.symlink(os.path.join(dotfiles_dir, "vim", "terminux_vimrc"), VIMRC)
  #os.symlink(os.path.join(dotfiles_dir, "bash", "terminux_bashrc"), BASHRC)
  #os.symlink(os.path.join(dotfiles_dir, "zsh", "terminux_zshrc"), ZSHRC)

def backup_file(file_path):
  """Backup existing user configuration."""
  if not os.path.exists(file_path):
    return
  LOGGER.info("Backing up %s", file_path)
  bkp_file_path = "%s.%s.bkp" % (file_path,
                                 datetime.datetime.now().strftime(
                                     "%Y-%m-%d_%H:%M:%S"))
  shutil.move(file_path, bkp_file_path)

def backup_current_config():
  """Backup user's current configuration."""
  backup_file(VIMRC)
  backup_file(VIMDIR)
  backup_file(BASHRC)
  backup_file(ZSHRC)

def install_vim8():
  """Install latest version of vim using linuxbrew."""
  err = run_cmd("brew install vim", "vim installation failed")
  if err is not None:
    LOGGER.critical(err)
    sys.exit(1)

def install_linuxbrew():
  """Install linuxbrew package manager."""
  check = "brew --help >/dev/null 2>&1"
  err = run_cmd(check)
  if err is None:
    LOGGER.info("brew already installed")
    return

  install = ('sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/'
             'install/master/install.sh)"')
  err = run_cmd(install, "Linuxbrew install failed")
  if err is not None:
    LOGGER.critical(err)
    sys.exit(1)

  path1 = ('test -d ~/.linuxbrew && PATH="${HOME}/.linuxbrew/bin:${HOME}/'
           '.linuxbrew/sbin:${PATH}"')
  _ = run_cmd(path1)

  path2 = ('test -d /home/linuxbrew/.linuxbrew && PATH="/home/linuxbrew/'
           '.linuxbrew/bin:/home/linuxbrew/.linuxbrew/sbin:${PATH}"')
  _ = run_cmd(path2)

  bash = ('test -r ~/.bash_profile && echo "export PATH=\'$(brew --prefix)/bin'
          ':$(brew --prefix)/sbin\'":\'"$PATH"\' >> ~/.bash_profile')
  _ = run_cmd(bash)

  prof = ('echo "export PATH=\'$(brew --prefix)/bin:$(brew --prefix)/sbin\'":'
          '\'"$PATH"\' >> ~/.profile')
  _ = run_cmd(prof)

  zprof = ('echo "export PATH=\'$(brew --prefix)/bin:$(brew --prefix)/sbin\'":'
           '\'"$PATH"\' >> ~/.zprofile')
  _ = run_cmd(zprof)

  hello = "brew install hello"
  _ = run_cmd(hello)

def centos_version():
  """Check OS is CentOS and CentOS version."""
  linux_dist = platform.linux_distribution()
  if linux_dist[0].lower() != CENTOS.lower():
    LOGGER.critical("%s is supported only on %s", NUTERMINUX, CENTOS)
    sys.exit(1)

  if (distutils.version.StrictVersion(linux_dist[1]) <
      distutils.version.StrictVersion(MIN_VERSION)):
    logging.warning("%s requires at least %s %s", NUTERMINUX, CENTOS,
                    MIN_VERSION)
    if query_yes_no("Do you want to 'yum update' (requires sudo)?"):
      err = run_cmd("sudo yum -y update", "yum update failed")
      if err is not None:
        LOGGER.critical(err)
        sys.exit(1)
    else:
      sys.exit(0)

def main():
  """main function."""
  parser = argparse.ArgumentParser()
  parser.add_argument('--uninstall', action='store_true',
                      help="Uninstall NuTermiNuX")
  args = parser.parse_args()
  if args.uninstall:
    uninstall()
    return

  # Install.
  centos_version()
  install_linuxbrew()
  install_vim8()
  backup_current_config()
  setup_terminux_config()

if __name__ == "__main__":
  main()
