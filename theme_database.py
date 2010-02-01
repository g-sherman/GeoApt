# Schema for the theme database
class ThemeDatabase:
    def __init__(self, db=None):
      self.db = db

    @classmethod
    def create_schema(self, db):
        print "Creating schema in SQLITE3 database\n"
        db.exec_("create table themes (id int primary key, name text, path text)")
