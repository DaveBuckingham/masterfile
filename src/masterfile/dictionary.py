# -*- coding: utf-8 -*-

# Part of the masterfile package: https://github.com/njvack/masterfile
# Copyright (c) 2018 Board of Regents of the University of Wisconsin System
# Written by Nate Vack <njvack@wisc.edu> at the Center for Healthy Minds
# at the University of Wisconsin-Madison.
# Released under MIT licence; see LICENSE at the package root.

"""
This contains the Dictionary class.

Dictionaries are CSV files, living in the dictionary/ directory. Multiple
dictionaries may apply to a masterfile.

There are two required columns in a dictionary CSV: 'component' and
'short_name' which will both be used to validate the columns in the
masterfile data files. Other columns will be added to the metadata in
masterfiles' columns, as so:

Dictionary:

component,short_name,contact
timepoint,t1,
measure,ourMeas,Leslie Smith
...

API:
>>> mf.df['t1_ourMeas'].contact
[('ourMeas', 'Leslie Smith')]
"""

from __future__ import absolute_import, unicode_literals

from os import path
from glob import glob

import pandas as pd

from masterfile import masterfile
from masterfile import errors
from masterfile.vendor import attr


@attr.s
class Dictionary(object):

    mf = attr.ib()

    components = attr.ib()

    dictionary_path = attr.ib(default=None)

    error_list = attr.ib(default=attr.Factory(list))

    _candidate_files = attr.ib(default=attr.Factory(list))

    _loaded_files = attr.ib(default=attr.Factory(list))

    _unprocessed_dataframes = attr.ib(default=attr.Factory(list))

    _loaded_dataframes = attr.ib(default=attr.Factory(list))

    @property
    def dataframe(self):
        pass

    @property
    def df(self):
        return self.dataframe

    @classmethod
    def load_for_masterfile(klass, mf):
        dictionary_path = path.join(mf.root_path, 'dictionary')
        d = klass(mf, mf.components, dictionary_path)
        return d

    def _find_candidate_files(self):
        self._candidate_files = glob(path.join(self.dictionary_path, '*csv'))

    def _read_unprocessed_dataframes(self):
        self._unprocessed_dataframes = []
        for f in self._candidate_files:
            df = None
            try:
                df = masterfile.read_csv_no_alterations(f)
            except IOError as e:
                self.error_list.append(errors.FileReadError(
                    locations=[f],
                    message='unable to read dictionary file {}'.format(f),
                    root_exception=e
                ))
            self._unprocessed_dataframes.append(df)
