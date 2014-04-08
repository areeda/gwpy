# coding=utf-8
# Copyright (C) Duncan Macleod (2014)
#
# This file is part of GWpy.
#
# GWpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWpy.  If not, see <http://www.gnu.org/licenses/>.

"""Read events from an Omicron-format ROOT file.
"""

import sys

if sys.version_info[0] < 3:
    range = xrange

from astropy.io import registry

from glue.lal import LIGOTimeGPS

from ROOT import TChain

from .. import lsctables
from ... import version

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'
__version__ = version.version

OMICRON_COLUMNS = ['search', 'peak_time', 'peak_time_ns',
                   'start_time', 'start_time_ns',
                   'stop_time', 'stop_time_ns', 'duration',
                   'central_freq', 'peak_frequency',
                   'flow', 'fhigh', 'bandwidth',
                   'snr', 'amplitude', 'confidence']


def sngl_burst_from_root(tchain, columns=OMICRON_COLUMNS):
    """Build a `SnglBurst` from a ROOT `TChain`.

    Parameters
    ----------
    tchain : `ROOT.TChain`
        the ROOT object from which to read.
    columns : `list`
        a `list` of valid `LIGO_LW` column names to load.

    Returns
    -------
    burst : :class:`~glue.ligolw.lsctables.SnglBurst`
        a `SnglBurst` with attributes populated from the ROOT data.
    """
    t = lsctables.SnglBurst()
    t.search = u'omicron'

    # parse frequency data
    flow = tchain.fstart
    fhigh = tchain.fend
    if 'flow' in columns:
        t.flow = flow
    if 'fhigh' in columns:
        t.fhigh = fhigh
    if 'bandwidth' in columns:
        t.bandwidth = fhigh-flow
    if 'central_freq' in columns:
        t.central_freq = tchain.frequency
    if 'peak_frequency' in columns:
        t.peak_frequency = tchain.frequency

    # parse time data
    peak_time = LIGOTimeGPS(tchain.time)
    if 'time' in columns or 'peak_time' in columns:
        t.peak_time = peak_time.seconds
    if 'time' in columns or 'peak_time_ns' in columns:
        t.peak_time_ns = peak_time.nanoseconds
    start_time = LIGOTimeGPS(tchain.tstart)
    if 'start_time' in columns:
        t.start_time = start_time.seconds
    if 'start_time_ns' in columns:
        t.start_time_ns = start_time.nanoseconds
    stop_time = LIGOTimeGPS(tchain.tend)
    if 'stop_time' in columns:
        t.stop_time = stop_time.seconds
    if 'stop_time_ns' in columns:
        t.stop_time_ns = stop_time.nanoseconds
    if 'duration' in columns:
        t.duration = float(stop_time - start_time)

    # others
    if 'snr' in columns:
        t.snr = tchain.snr
    if 'amplitude' in columns:
        t.amplitude = tchain.snr ** 2 / 2.
    if 'confidence' in columns:
        t.confidence = tchain.snr

    return t


def table_from_root(filename, columns=OMICRON_COLUMNS):
    """Build a `SnglBurstTable` from events in an Omicron ROOT file.
    """
    # read ROOT file
    tree = TChain('triggers')
    tree.Add(filename)

    # generate output
    out = lsctables.New(lsctables.SnglBurstTable, columns=columns)
    append = out.append

    # iterate over events
    nevents = tree.GetEntries()
    for i in range(nevents):
        tree.GetEntry()
        burst = sngl_burst_from_root(tree, columns=columns)
        append(burst)

    return out


def identify_omicron(*args, **kwargs):
    """Determine an input object as an Omicron-format ROOT file.
    """
    fp = args[1]
    if isinstance(fp, file):
        fp = fp.name
    # identify string
    if (isinstance(fp, (unicode, str)) and
            fp.endswith('root') and
            'omicron' in fp.lower()):
        return True
        # identify cache object
    else:
        return False


registry.register_reader('omicron', lsctables.SnglBurstTable, table_from_root)
registry.register_identifier('omicron', lsctables.SnglBurstTable,
                             identify_omicron)