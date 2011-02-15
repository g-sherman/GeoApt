# Copyright (C) 2008-2011 Gary Sherman
# Licensed under the terms of GNU GPL 2
class Theme:
    """Simple theme object."""
    def __init__(self, id=None, name=None, path=None):
        self.name = name
        self.path = path
        self.id = id
