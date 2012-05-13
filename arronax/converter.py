#
# Unsettings - a configuration frontend for the Unity desktop environment
#
# Copyright (C) 2012 Florian Diesch <devel@florian-diesch.de>
#
# Homepage: http://www.florian-diesch.de/software/unsettings/
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#


class Validator(object):
    
    def validate(self, value):
        raise NotImplementedError


class RangeValidator(object):
    def __init__(self, minimum=None, maximum=None):
        """
        
        Arguments:
        - `minimum`:
        - `maximum`:
        """
        self.miminum = minimum
        self.maximum = maximum
        
    
    def validate(self, value):
        if self.minimum is not None and value < self.minimum:
            return False
        if self.maximum is not None and value > self.maximum:
            return False
        return True


class Converter(object):
    def convert(self, value):
        return value

    def rev_convert(self, value):
        return value

class FloatConverter(Converter):

    def __init__(self, factor=1.0, offset=0.0):
        self.factor=float(factor)
        self.offset=float(offset)
    
    def convert(self, value):
        return value * self.factor + self.offset

    def rev_convert(self, value):
        return (value - self.offset) / (self.factor * 1.0)


class IntConverter(Converter):
    
    def __init__(self, factor=1, offset=0):
        self.factor=factor
        self.offset=offset
    
    def convert(self, value):
        return int(value) * self.factor + self.offset

    def rev_convert(self, value):
        return (value - self.offset) / (self.factor * 1.0)

class DictConverter(object):
    def __init__(self, adict):
        self.dict = adict
        self.rev_dict = dict((v, k) for k,v in adict.iteritems())

    def convert(self, value):
        return self.dict.get(value, value)

    def rev_convert(self, value):
        return self.rev_dict.get(value, value)

class ListConverter(object):
    def convert(self, value):        
        return [x for x in value.splitlines() if x.strip() != '']

    def rev_convert(self, value):
        return "\n".join(value)
