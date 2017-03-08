# -*- coding: utf-8 -*-
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

"""Write GWpy objects to HDF5 files
"""

try:
    import h5py
    HAVE_H5PY = True
except ImportError:
    HAVE_H5PY = False

from astropy.io.misc.hdf5 import is_hdf5 as identify_hdf5

from ..utils.deps import with_import

__author__ = 'Duncan Macleod <duncan.macleod@ligo.org>'


def open_hdf5(filename, mode='r'):
    """Wrapper to open a :class:`h5py.File` from disk, gracefully
    handling a few corner cases
    """
    import h5py
    if isinstance(filename, (h5py.Group, h5py.Dataset)):
        return filename
    elif isinstance(filename, file):
        return h5py.File(filename.name, mode)
    else:
        return h5py.File(filename, mode)
