#!/usr/bin/env python2.7
"""Installer for NuTermiNuX."""

import argparse
import datetime
import errno
import distutils.version
import glob
import logging
import os
import platform
import shutil
import subprocess
import sys

BREW = "brew"
BREWDIR = "/home/linuxbrew/.linuxbrew/bin"
CENTOS = "CentOS"
MIN_VERSION = "6.9"
NUTERMINUX = "NuTermiNuX"

HOME = os.environ["HOME"]
PYLINTRC = os.path.join(HOME, ".pylintrc")
VIMRC = os.path.join(HOME, ".vimrc")
VIMDIR = os.path.join(HOME, ".vim")
BASHRC = os.path.join(HOME, ".bashrc")
ZSHRC = os.path.join(HOME, ".zshrc")
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

def run_cmd(cmd, err=None, quiet=False):
  """Run the shell command and return err in case of a failure."""
  if not quiet:
    LOGGER.debug("Running %s", cmd)

  if err is None:
    err = "'%s' failed" % cmd

  ret = subprocess.call(cmd, shell=True)
  if ret:
    if not quiet:
      LOGGER.error("%s exited with %d code", cmd, ret)
      return err

  return None

def restore(rpath):
  """Restore the latest backup."""
  LOGGER.debug("Restoring %s", rpath)

  if os.path.islink(rpath):
    os.unlink(rpath)

  LOGGER.debug("Restoring the backup of %s", rpath)
  bkps = sorted(glob.glob("%s*.bkp" % rpath))
  if bkps:
    LOGGER.debug("Backups: %s", bkps)
    shutil.move(os.path.join(bkps[-1]), rpath)

def uninstall():
  """Restore old configuration."""
  LOGGER.info("Uninstalling %s", NUTERMINUX)

  LOGGER.info("Uninstalling linux%s", BREW)
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

  for lb_dir in [HOME, "/home/linuxbrew"]:
    lb_path = os.path.join(lb_dir, ".linuxbrew")
    if os.path.isdir(lb_path):
      shutil.rmtree(lb_path)

def force_symlink(dest_link, to_be_linked):
  """ln -sf file1 file2."""
  LOGGER.debug("Symlinking %s to %s", to_be_linked, dest_link)

  try:
    os.symlink(dest_link, to_be_linked)
  except OSError as exc:  # to_be_linked exists.
    if exc.errno == errno.EEXIST:
      try:
        os.remove(to_be_linked)
      except OSError as exc:
        if exc.errno == errno.EPERM:
          shutil.rmtree(to_be_linked)
      os.symlink(dest_link, to_be_linked)

def setup_nuterminux_config():
  """Setup NuTermiNuX configuration."""
  LOGGER.info("Setting up %s configuration", NUTERMINUX)

  dotfiles_dir = os.path.join(os.path.dirname(os.path.dirname(
      os.path.realpath(__file__))), "dotfiles")

  force_symlink(os.path.join(dotfiles_dir, "vim", "%s_vimrc"
                             % NUTERMINUX.lower()), VIMRC)
  force_symlink(os.path.join(dotfiles_dir, "vim", "dotvim"), VIMDIR)
  # force_symlink.symlink(os.path.join(dotfiles_dir, "bash", "%s_bashrc"
                                     # % NUTERMINUX.lower()), BASHRC)
  # force_symlink(os.path.join(dotfiles_dir, "zsh", "%s_zshrc"
                             # % NUTERMINUX.lower()), ZSHRC)
  force_symlink(os.path.join(dotfiles_dir, "py", "pylintrc"), PYLINTRC)

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
  LOGGER.debug("Backing up current config")

  backup(VIMRC)
  backup(VIMDIR)
  #backup(BASHRC)
  #backup(ZSHRC)
  backup(PYLINTRC)

def which(program):
  """which unix command."""
  def is_exe(fpath):
    """Check if fpath is executable."""
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

  fpath, _ = os.path.split(program)
  if fpath:
    if is_exe(program):
      return program
  else:
    for path in os.environ["PATH"].split(os.pathsep):
      exe_file = os.path.join(path, program)
      if is_exe(exe_file):
        return exe_file

  return None

def install_vim8():
  """Install latest version of vim using linuxbrew."""
  LOGGER.info("Installing vim 8")

  err = run_cmd("brew install vim", "vim installation failed")
  if err is not None:
    LOGGER.critical(err)
    sys.exit(1)

  msg = "Your vim plugins might not work as expected."

  nvm = "neovim"
  nvp = "%s python client" % nvm
  LOGGER.debug("Installing %s", nvp)
  err = run_cmd("pip3 install --upgrade %s" % nvm)
  if err is not None:
    LOGGER.warning("Failed installing %s. %s", nvp, msg)

  py2 = "python@2"
  LOGGER.debug("Installing the brewed version of %s", py2)
  err = run_cmd("brew install %s" % py2, "%s installation failed" % py2)
  if err is not None:
    LOGGER.warning("Failed %s installing %s. %s", BREW, py2, msg)

  ctags = "ctags"
  if which(ctags) is None:
    LOGGER.debug("Installing the brewed version of %s", ctags)
    err = run_cmd("brew install %s" % ctags, "%s installation failed" % ctags)
    if err is not None:
      LOGGER.warning("Failed %s installing %s. %s", BREW, ctags, msg)

def install_linuxbrew():
  """Install linuxbrew package manager."""
  LOGGER.debug("Checking if %s is already installed.", BREW)

  check = "brew --help >/dev/null 2>&1"
  err = run_cmd(check, quiet=True)
  if err is None:
    LOGGER.info("%s is already installed", BREW)
    return

  LOGGER.info("Installing linux%s", BREW)
  install = ('sh -c "$(curl -fsSL https://raw.githubusercontent.com/Linuxbrew/'
             'install/master/install.sh)"')
  err = run_cmd(install, "Linuxbrew install failed")
  if err is not None:
    LOGGER.critical(err)
    sys.exit(1)

  LOGGER.info("Setting up PATH. Your PATH is %s", os.environ.get("PATH"))
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

  #hello = "brew install hello"
  #_ = run_cmd(hello)

def centos_version():
  """Check OS is CentOS and CentOS version."""
  LOGGER.debug("Checking prerequisite %s version", CENTOS)

  linux_dist = platform.linux_distribution()
  if linux_dist[0].lower() != CENTOS.lower():
    LOGGER.critical("%s is supported only on %s", NUTERMINUX, CENTOS)
    sys.exit(1)

  if (distutils.version.StrictVersion(linux_dist[1]) <
      distutils.version.StrictVersion(MIN_VERSION)):
    LOGGER.warning("%s requires at least %s %s", NUTERMINUX, CENTOS,
                   MIN_VERSION)
    if query_yes_no("Do you want to 'yum update' (requires sudo)?"):
      err = run_cmd("sudo yum -y update", "yum update failed")
      if err is not None:
        LOGGER.critical(err)
        sys.exit(1)
    else:
      LOGGER.info("yum update is harmless and will not affect your build. "
                  "Consider running it again.")
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
  setup_nuterminux_config()

  LOGGER.info("Install successfull. Welcome to %s", NUTERMINUX)

if __name__ == "__main__":
  main()
