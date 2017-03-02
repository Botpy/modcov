#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""Main"""
import sys

from . import main

if __name__ == "__main__":
    if not main():
        sys.exit(2)
