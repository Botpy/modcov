#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Unit test"""
from __future__ import print_function, division, unicode_literals

import os
import sys
import unittest

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO

import mock

from modcov import parse_cmd, run, __version__

# pylint: disable=C0111


class ModcovTestCase(unittest.TestCase):
    def setUp(self):
        super(ModcovTestCase, self).setUp()

        self.out = StringIO()
        self.old_out = sys.stdout
        sys.stdout = self.out

        self.parser = parse_cmd()

        crt_path = os.path.abspath(os.path.dirname(__file__))
        tpl_path = os.path.join(crt_path, "coverage_data")

        self.data_file_path = os.path.join(crt_path, ".coverage")
        self.data_file_path = os.path.abspath(self.data_file_path)

        with open(tpl_path) as f:
            content = f.read().replace("{placeholder}",
                                       os.path.dirname(crt_path))

        with open(self.data_file_path, "w") as f:
            f.write(content)

    def tearDown(self):
        super(ModcovTestCase, self).tearDown()
        sys.stdout = self.old_out

    def test_run(self):
        ns = self.parser.parse_args(["modcov/__init__.py",
                                     "--data-file", self.data_file_path])
        run(ns)
        self.assertIn("/0.0\tPASSED", self.out.getvalue())
        self.assertNotIn("0.0/0.0\tPASSED", self.out.getvalue())

    def test_fail_under(self):
        ns = self.parser.parse_args(["modcov/__init__.py",
                                     "--fail-under", "75",
                                     "--data-file", self.data_file_path])
        run(ns)
        self.assertIn("/75.0\tFAILED", self.out.getvalue())
        self.assertNotIn("0.0/75.0\tFAILED", self.out.getvalue())

    def test_exclude(self):
        ns = self.parser.parse_args(["modcov/__init__.py",
                                     "--fail-under", "75",
                                     "--exclude", "modcov/*",
                                     "--data-file", self.data_file_path])
        run(ns)
        self.assertNotIn("__init__.py", self.out.getvalue())

    def test_git(self):
        with mock.patch("modcov.subprocess.check_output") as output:
            output.return_value = b"modcov/__init__.py"
            ns = self.parser.parse_args(["--git",
                                         "--fail-under", "75",
                                         "--data-file", self.data_file_path])
            run(ns)
            self.assertIn("__init__.py", self.out.getvalue())

    def test_version(self):
        ns = self.parser.parse_args(["--version", "--fail-under", "75",
                                     "--data-file", self.data_file_path])
        run(ns)
        self.assertIn(__version__, self.out.getvalue())

    def test_no_modules(self):
        ns = self.parser.parse_args(["--fail-under", "75",
                                     "--data-file", self.data_file_path])
        run(ns)
        self.assertIn("Please specify modules", self.out.getvalue())

    def test_skip(self):
        ns = self.parser.parse_args(["tests/__init__.py",
                                     "--fail-under", "75",
                                     "--data-file", self.data_file_path])
        run(ns)
        self.assertNotIn("tests/__init__.py", self.out.getvalue())
