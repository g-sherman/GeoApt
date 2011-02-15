# Copyright (C) 2008-2011 Gary Sherman
# Licensed under the terms of GNU GPL 2
from theme import *
class ThemeDatabase:
    """Schema for the theme database."""

    def __init__(self, db=None):
        self.db = db

    @classmethod
    def create_schema(cls, db):
        """Create the themes table in the theme database."""
        print "Creating schema in SQLITE3 database\n"
        cursor = db.cursor()
        cursor.execute("create table themes (id integer primary key autoincrement, name text, path text, parent_id int)")
        cursor.close()

    @classmethod
    def add_folder(cls, db, folder, parent_id=0):
        """Add a folder to the themes table.

        The folder is created and the parent_id is set to that of its
        parent. If it is a top-level folder, there is no parent and
        parent_id is set to 0 (the default).

        """
        print "Adding folder to database\n"
        cursor = db.cursor()
        cursor.execute("insert into themes (name, parent_id) values('%s', %i)" % (folder, parent_id))
        db.commit()
        return cursor.lastrowid

    @classmethod
    def add_theme(cls, db, theme_name, theme_path, parent_id):
        """Add a theme to the database.

        The name, path and parent_id are required to create a theme. Path
        is the full path to the location of the theme on disk.

        """
        print "Adding theme to database\n"
        cursor = db.cursor()
        cursor.execute("insert into themes (name, path, parent_id) values('%s','%s', %i)" % (theme_name, theme_path, parent_id))
        db.commit()
        return cursor.lastrowid

    @classmethod
    def folder_list(cls, db):
        """Create a list containing the theme folders."""
        cursor = db.cursor()
        # get the list of theme folders (rows with parent_id = 0)
        cursor.execute("select id, name from themes where parent_id = 0 order by name")
        folder_list = list()
        for row in cursor:
            folder_list.append(Theme(row[0], row[1]))
        cursor.close()
        return folder_list

    @classmethod
    def theme_list(cls, db):
        """Create a dict containing the theme folder and its themes."""
        cursor = db.cursor()
        # get the list of theme folders (rows with parent_id = 0)
        cursor.execute("select id, name from themes where parent_id = 0 order by name")
        theme_list = dict()
        theme_cursor = db.cursor()
        for row in cursor:
            print row
            theme_cursor.execute("select id, name, path from themes where parent_id = %s" % row[0])
            child_themes = list()
            for t_row in theme_cursor:
                child_themes.append(Theme(t_row[0], t_row[1], t_row[2]))
            theme_list[row[0]] = child_themes
        theme_cursor.close()
        cursor.close()
        return theme_list
