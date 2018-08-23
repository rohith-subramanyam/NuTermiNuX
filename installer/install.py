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
PYLINTRC = os.path.join(HOME, ".pylintrc")
PROFILE = os.path.join(HOME, ".profile")
BPROFILE = os.path.join(HOME, ".bash_profile")
ZPROFILE = os.path.join(HOME, ".zprofile")

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
    LOGGER.error("%s exited with %d code", cmd, ret)
    return err

  return None

def restore(rpath):
  """Restore the latest backup."""
  if os.path.islink(rpath):
    os.unlink(rpath)
  LOGGER.debug("Restoring %s", rpath)
  bkps = sorted(glob.glob("%s*.bkp" % rpath))
  if bkps:
    LOGGER.debug("backups: %s", bkps)
    shutil.move(os.path.join(bkps[-1]), rpath)

def uninstall():
  """Restore old configuration."""
  LOGGER.info("Uninstalling linuxbrew")
  uninstall_brew = ('ruby -e "$(curl -fsSL https://raw.githubusercontent.com/'
                    'Homebrew/install/master/uninstall)"')
  _ = run_cmd(uninstall_brew, "Uninstalling brew failed")

  restore(VIMRC)
  restore(VIMDIR)
  restore(BASHRC)
  restore(ZSHRC)
  restore(PYLINTRC)

  if os.path.isfile(PROFILE):
    remove_profile = "sed -i '/linuxbrew/d' %s" % PROFILE
    _ = run_cmd(remove_profile)
  if os.path.isfile(BPROFILE):
    remove_bprofile = "sed -i '/linuxbrew/d' %s" % BPROFILE
    _ = run_cmd(remove_bprofile)
  if os.path.isfile(ZPROFILE):
    remove_zprofile = "sed -i '/linuxbrew/d' %s" % ZPROFILE
    _ = run_cmd(remove_zprofile)

def setup_terminux_config():
  """Setup terminux configuration."""
  dotfiles_dir = os.path.join(os.path.dirname(os.path.dirname(
      os.path.realpath(__file__))), "dotfiles")
  os.symlink(os.path.join(dotfiles_dir, "vim", "terminux_vimrc"), VIMRC)
  os.symlink(os.path.join(dotfiles_dir, "vim", "vim"), VIMDIR)
  #os.symlink(os.path.join(dotfiles_dir, "bash", "terminux_bashrc"), BASHRC)
  #os.symlink(os.path.join(dotfiles_dir, "zsh", "terminux_zshrc"), ZSHRC)
  os.symlink(os.path.join(dotfiles_dir, "py", "pylintrc"), PYLINTRC)

def backup(bpath):
  """Backup existing user configuration."""
  if not os.path.exists(bpath):
    return
  LOGGER.info("Backing up %s", bpath)
  bkp_path = "%s.%s.bkp" % (bpath, datetime.datetime.now().strftime(
      "%Y-%m-%d_%H:%M:%S"))
  shutil.move(bpath, bkp_path)

def backup_current_config():
  """Backup user's current configuration."""
  backup(VIMRC)
  backup(VIMDIR)
  #backup(BASHRC)
  #backup(ZSHRC)
  backup(PYLINTRC)

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

  for lb_dir in [HOME, "/home/linuxbrew"]:
    lb_path = os.path.join(lb_dir, ".linuxbrew")
    if os.path.isdir(lb_path):
      os.environ["PATH"] = "%s%s%s%s%s" % (os.path.join(lb_path, "bin"),
                                           os.pathsep,
                                           os.path.join(lb_path, "sbin"),
                                           os.pathsep, os.environ.get("PATH"))

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
