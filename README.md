[![Build Status](https://travis-ci.org/coldnight/modcov.svg?branch=master)](https://travis-ci.org/coldnight/modcov)
[![Code Coverage](https://codecov.io/github/coldnight/modcov/coverage.svg?branch=master)](https://codecov.io/gh/coldnight/modcov)

modcov
======

A tool to check every module's code coverage. Usually we run tests & measurement
code coverage for whole project. There is a question: some module will have a low
code coverage.

This tool use the exists coverage data to check every changed module's code coverage,
and exit with a non-zero status code if the module's code coverage less than specified.

## Install

```shell
$ pip install -U modcov
```

## Example

After tests & measurement code coverage:

```shell
$ modcov --fail-under=75 pkg/handler/demo.py
```

Check the modules that changed in last commit in git:

```shell
$ modcov --fail-under=75 --git
```

Exclude tests:

```shell
$ modcov --fail-under=75 --git --exclude=tests/*
```
