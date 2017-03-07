#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Use coverage data to check every module's code coverage."""
from __future__ import print_function, division, unicode_literals

import os
import sys
import argparse
import subprocess

import fnmatch

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import coverage

__version__ = "0.0.3"


def parse_cmd():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("modules", metavar="MOD1.py,MOD2.py",
                        nargs="?",
                        default=None,
                        help="Modules to measurement")
    parser.add_argument("-d", "--data-file", default=".coverage",
                        help="Data file of coverage")

    parser.add_argument("-c", "--config-file", default=".coveragerc",
                        help="Config file of coverage")

    parser.add_argument("-g", "--git", action="store_const", const=True,
                        default=False,
                        help="Use git last commit changed files as modules")

    parser.add_argument("-e", "--exclude",
                        metavar="MOD1.py,MOD1*",
                        help="Pattern list to exclude")

    parser.add_argument("--fail-under", action="store", default=None,
                        metavar="MIN",
                        help="Exit with status of 2 if any module's coverage "
                        "is less than MIN")
    parser.add_argument("-v", "--version", action="store_const", const=True,
                        default=False,
                        help="Print version number and exit")
    return parser


def get_changed_files():
    """Get git last commit changed files"""

    out = subprocess.check_output(
        "git diff HEAD^ --name-only --diff-filter=ACM", shell=True)

    result = []

    for fn in out.splitlines():
        if fn.endswith(b".py"):
            result.append(fn.decode("utf8"))

    return result


def _is_skip(excludes, fn):
    for p in excludes:
        if fnmatch.fnmatch(fn, p):
            return True

    return False


def _is_empty(fn):
    """Returns True if the file is empty"""
    return os.stat(fn).st_size == 0


def run(ns):
    """Run this tool and returns True if everything is ok.

    :type ns: :class:`argparse.Namespace`
    """
    if ns.version:
        print(__version__)
        return True

    cov = coverage.Coverage(ns.data_file, config_file=ns.config_file)
    cov.load()

    failed_list = []

    cov_exclude = cov.get_option("run:omit") or []
    if ns.exclude:
        excludes = cov_exclude + ns.exclude.split(",")
    else:
        excludes = cov_exclude

    if ns.git:
        modules = get_changed_files()
    else:
        if ns.modules is None:
            print("Please specify modules")
            return False

        modules = ns.modules.split(",")

    for mod in modules:
        if _is_empty(mod):
            continue

        if excludes and _is_skip(excludes, mod):
            continue

        print("Measurementing coverage on", mod, end="\t...\t")
        buf = StringIO()

        covered = cov.report(mod, file=buf)

        if ns.fail_under:
            fail_under = float(ns.fail_under)
        else:
            fail_under = 0

        print("%.1f/%.1f" % (covered, fail_under), end="\t")

        if fail_under and covered < fail_under:
            print("FAILED")
            failed_list.append(mod)
            print(buf.getvalue())
        else:
            print("PASSED")

    if failed_list:
        return False

    return True


def main():
    parser = parse_cmd()
    if not run(parser.parse_args()):
        sys.exit(2)
