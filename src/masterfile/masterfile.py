# -*- coding: utf-8 -*-

# Part of the masterfile package: https://github.com/njvack/masterfile
# Copyright (c) 2017 Board of Regents of the University of Wisconsin System
# Written by Nate Vack <njvack@wisc.edu> at the Center for Healthy Minds
# at the University of Wisconsin-Madison.
# Released under MIT licence; see LICENSE at the package root.

from __future__ import absolute_import, unicode_literals

from itertools import chain
from os import path
import json
from glob import glob

import pandas as pd

from .vendor import attr
from .errors import Error


def load(path):
    return Masterfile.load_path(path)


@attr.s
class Masterfile(object):

    index_column = attr.ib()

    components = attr.ib()

    _pathname = attr.ib(default=None)

    _dataframes = attr.ib(default=attr.Factory(list))

    _dataframe_files = attr.ib(default=attr.Factory(list))

    _dictionaries = attr.ib(default=attr.Factory(list))

    errors = attr.ib(default=attr.Factory(list))

    __joined_data = attr.ib(default=None)

    @property
    def dataframe(self):
        if self.__joined_data is not None:
            return self.__joined_data
        self.__joined_data = pd.concat(
            self._dataframes,
            axis='columns',
            join='outer')
        self.__joined_data.index.name = self.index_column
        return self.__joined_data

    @property
    def df(self):
        return self.dataframe

    @classmethod
    def load_path(klass, pathname):
        """
        Initialize a Masterfile from pathname/settings.json, load all .csv
        data and dictionaries into it.
        TODO: Implement this.
        """
        json_data = klass._read_settings_json(pathname)
        mf = klass(**json_data)
        mf._pathname = pathname
        mf._load_all_data_files_into_dataframes()
        return mf

    @classmethod
    def _read_settings_json(klass, pathname):
        """
        load pathname/settings.json, parse it, and return a dict with its
        contents.
        """
        json_filename = path.join(pathname, "settings.json")
        return json.load(open(json_filename, 'r'))

    def _load_all_data_files_into_dataframes(self):
        self._dataframe_files = glob(path.join(self._pathname, "*csv"))
        self._add_data_files_to_dataframes()

    def _add_data_files_to_dataframes(self):
        dataframes, errors = self._load_data_files(self._dataframe_files)
        self._dataframes = list(chain(self._dataframes, dataframes))
        self.errors = list(chain(self.errors, errors))
        self.__joined_data = None  # Reset the memoized data

    def _load_data_files(self, filenames):
        dataframes = []
        errors = []
        for f in filenames:
            try:
                df = self._load_data_csv(f)
                dataframes.append(df)
            except LookupError as e:
                errors.append(Error(
                    code='E101',
                    location=f,
                    message='column {} not found'.format(self.index_column)))
        return (dataframes, errors)

    def _load_data_csv(self, filename):
        df = pd.read_csv(
            filename,
            index_col=False,
            dtype={self.index_column: str})
        df.set_index(self.index_column, inplace=True)
        return df

    def _load_dictionary_csv(self, filename):
        df = pd.read_csv(filename, index_col=False, dtype=str)
        return df
