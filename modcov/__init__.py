#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Use coverage data to check every module's code coverage."""
from __future__ import print_function, division

import argparse
import subprocess

import fnmatch

from cStringIO import StringIO

import coverage

__version__ = "0.0.1"


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
    return parser.parse_args()


def get_changed_files():
    """Get git last commit changed files"""

    out = subprocess.check_output(
        "git diff HEAD^ --name-only --diff-filter=ACM", shell=True)

    result = []

    for fn in out.splitlines():
        if fn.endswith(".py"):
            result.append(fn)

    return result


def _is_skip(exclude, fn):
    for p in exclude.split(","):
        if fnmatch.fnmatch(fn, p):
            return True

    return False


def main():
    """Run this tool and returns True if everything is ok."""
    ns = parse_cmd()

    if ns.version:
        print(__version__)
        return True

    cov = coverage.Coverage(ns.data_file, config_file=ns.config_file)
    cov.load()

    failed_list = []

    if ns.git:
        modules = get_changed_files()
    else:
        if ns.modules is None:
            print("Please specify modules")
            return False

        modules = ns.modules.split(",")

    for mod in modules:
        if ns.exclude and _is_skip(ns.exclude, mod):
            continue

        print("Measurementing coverage on", mod, end="\t...\t")
        buf = StringIO()

        covered = cov.report(mod, file=buf)

        if ns.fail_under and covered < float(ns.fail_under):
            print("%.1f/%.1f\tFAILED" % (covered, float(ns.fail_under)))
            failed_list.append(mod)
            print(buf.getvalue())
        else:
            print("%.1f/0\tPASSED" % covered)

    if failed_list:
        return False

    return True
