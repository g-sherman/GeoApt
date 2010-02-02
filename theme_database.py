# Schema for the theme database
class ThemeDatabase:
    def __init__(self, db=None):
      self.db = db

    @classmethod
    def create_schema(self, db):
        print "Creating schema in SQLITE3 database\n"
        db.exec_("create table themes (id int primary key, name text, path text)")

    @classmethod
    def add_folder(self, db, folder, parent_id=0):
        print "Adding folder to database\n"
        cursor = db.cursor()
        cursor.execute("insert into themes (name) values('%s')" % folder)
        db.commit()
        return cursor.lastrowid
