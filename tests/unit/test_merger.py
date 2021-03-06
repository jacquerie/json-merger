# -*- coding: utf-8 -*-
#
# This file is part of Inspirehep.
# Copyright (C) 2016 CERN.
#
# Inspirehep is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Inspirehep is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Inspirehep; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Test merger corner cases that are unlikely to appear as usage scenarios."""

from __future__ import absolute_import, print_function


import pytest


from json_merger.config import DictMergerOps, UnifierOps
from json_merger.conflict import Conflict, ConflictType
from json_merger.errors import MergeError
from json_merger.merger import Merger


def test_merge_bare_int_lists():
    r = [1, 2, 3]
    h = [1, 2, 3, 4]
    u = [1, 2, 5]

    m = Merger(r, h, u,
               DictMergerOps.FALLBACK_KEEP_HEAD,
               UnifierOps.KEEP_ONLY_UPDATE_ENTITIES)
    m.merge()
    assert m.merged_root == [1, 2, 5]


def test_merge_bare_str_lists():
    r = ['1', '2', '3']
    h = ['1', '2', '3', '4']
    u = ['1', '2', '5']

    m = Merger(r, h, u,
               DictMergerOps.FALLBACK_KEEP_HEAD,
               UnifierOps.KEEP_ONLY_UPDATE_ENTITIES)
    m.merge()
    assert m.merged_root == ['1', '2', '5']


def test_merge_nested_lists():
    r = [[1], [2], [3]]
    h = [[1], [2], [3], [4]]
    u = [[1], [2], [5]]

    m = Merger(r, h, u,
               DictMergerOps.FALLBACK_KEEP_HEAD,
               UnifierOps.KEEP_ONLY_UPDATE_ENTITIES)
    m.merge()

    assert m.merged_root == [[1], [2], [5]]


def test_merge_root_is_not_list():
    r = 'randomstring'
    h = [[1], [2, 3], [5]]
    u = [[1], [2, 3], [5]]

    m = Merger(r, h, u,
               DictMergerOps.FALLBACK_KEEP_HEAD,
               UnifierOps.KEEP_ONLY_UPDATE_ENTITIES)
    m.merge()
    # Here the lists are aligned as entities and lists of entities.
    assert m.merged_root == [[1], [2, 3], [5]]


def test_merge_list_with_string():
    r = 'somerandomvalue'
    h = [1, 2, 3]
    u = 'a given string'

    m = Merger(r, h, u,
               DictMergerOps.FALLBACK_KEEP_HEAD,
               UnifierOps.KEEP_ONLY_UPDATE_ENTITIES)
    with pytest.raises(MergeError) as excinfo:
        m.merge()

    assert m.merged_root == [1, 2, 3]
    assert len(excinfo.value.content) == 1
    assert excinfo.value.content[0] == Conflict(ConflictType.SET_FIELD, (),
                                                'a given string')
