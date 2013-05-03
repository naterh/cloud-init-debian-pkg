# vi: ts=4 expandtab
#
#    Copyright (C) 2012 Yahoo! Inc.
#
#    Author: Joshua Harlow <harlowja@yahoo-inc.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License version 3, as
#    published by the Free Software Foundation.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

DEF_MERGE_TYPE = 'replace'
MERGE_TYPES = ('append', 'prepend', DEF_MERGE_TYPE,)


class Merger(object):
    def __init__(self, merger, opts):
        self._merger = merger
        # Affects merging behavior...
        self._method = DEF_MERGE_TYPE
        for m in MERGE_TYPES:
            if m in opts:
                self._method = m
                break
        # Affect how recursive merging is done on other primitives
        self._recurse_str = 'recurse_str' in opts
        self._recurse_dict = 'recurse_dict' in opts
        self._recurse_array = 'recurse_array' in opts

    def __str__(self):
        return ('ListMerger: (method=%s,recurse_str=%s,'
                'recurse_dict=%s,recurse_array=%s)') % (self._method,
                                                        self._recurse_str,
                                                        self._recurse_dict,
                                                        self._recurse_array)

    def _on_tuple(self, value, merge_with):
        return tuple(self._on_list(list(value), merge_with))

    def _on_list(self, value, merge_with):
        if (self._method == 'replace' and
            not isinstance(merge_with, (tuple, list))):
            return merge_with

        # Ok we now know that what we are merging with is a list or tuple.
        merged_list = []
        if self._method == 'prepend':
            merged_list.extend(merge_with)
            merged_list.extend(value)
            return merged_list
        elif self._method == 'append':
            merged_list.extend(value)
            merged_list.extend(merge_with)
            return merged_list

        def merge_same_index(old_v, new_v):
            if isinstance(new_v, (list, tuple)) and self._recurse_array:
                return self._merger.merge(old_v, new_v)
            if isinstance(new_v, (str, basestring)) and self._recurse_str:
                return self._merger.merge(old_v, new_v)
            if isinstance(new_v, (dict)) and self._recurse_dict:
                return self._merger.merge(old_v, new_v)
            # Otherwise leave it be...
            return old_v

        # Ok now we are replacing same indexes
        merged_list.extend(value)
        common_len = min(len(merged_list), len(merge_with))
        for i in xrange(0, common_len):
            merged_list[i] = merge_same_index(merged_list[i], merge_with[i])
        return merged_list
