# -*- coding: utf-8 -*-

# Part of the masterfile package: https://github.com/njvack/masterfile
# Copyright (c) 2018 Board of Regents of the University of Wisconsin System
# Written by Nate Vack <njvack@wisc.edu> at the Center for Healthy Minds
# at the University of Wisconsin-Madison.
# Released under MIT licence; see LICENSE at the package root.

"""
The masterfile annotator.

This class takes the a dictionary and a masterfile, and can "annotate"
dataframes' series with the metadata from the dictionary, so you can do things
like:

df = mf.dataframe
df.t1_ourMeasure.contact
{
    'ourMeasure': 'Jordan Smith'
}
"""

from __future__ import absolute_import, unicode_literals

from collections import defaultdict

from masterfile.vendor import attr


@attr.s
class Annotator(object):

    masterfile = attr.ib()

    dictionary = attr.ib()

    error_list = attr.ib(default=attr.Factory(list))

    @classmethod
    def from_masterfile(klass, mf):
        return klass.new(masterfile=mf, dictionary=mf.dictionary)

    def annotate_masterfile(self):
        self.annotate_dataframe(self.masterfile.dataframe)

    def annotate_dataframe(self, df):
        for series_name, series in df.iteritems():
            self.annotate_series(series)

    def make_series_annotations(self, series_name):
        """
        Create a dictionary of annotations for a series, of the format:
        {
            dictionaryColumn: {componentName_componentValue: dictionaryValue}
            ...
        }
        So if your dictionary has a timepoint t1 with the long_name "Time 1",
        you'll get:
        {
            'long_name': {'timepoint_t1': 'Time 1'}
            ...
        }
        I'm not very happy with this code, it's ugly as hell, but I don't have
        a clear way to clean it up.
        """
        d = defaultdict(dict)
        components = self.masterfile.components
        for comp, val in match_column_components(components, series_name):
            label = '{}_{}'.format(comp, val)
            component_annotations = self.dictionary.annotations_for(comp, val)
            for ann_label, ann_value in component_annotations.items():
                d[ann_label][label] = ann_value
        return d

    def annotate_series(self, series):
        annotations = self.make_series_annotations(series.name)
        for attribute, values in annotations.items():
            series._metadata.append(attribute)
            setattr(series, attribute, values)


def match_column_components(components, column_name):
    ccs = column_name.split('_')
    return zip(components, ccs)
