import sqlite3
import os
import Note as nt

class NoteDB:
    def __init__(self, filename="noted.db", schema_file="noted.sql"):
        new_db = False
        if not os.path.exists(filename):
            new_db = True
        self.conn = self.create_connection(filename)
        self.cursor = self.conn.cursor()
        if new_db:
            self.create_schema(schema_file)
        self.note_map = {}
        self.notes = self.read()
        self.sort()

    def close_connection(self):
        """Close the DB connection."""
        self.conn.close()

    def create_connection(self, filename):
        """Create a database connection to the SQLite database."""
        conn = None
        try:
            conn = sqlite3.connect(filename, check_same_thread=False)
        except sqlite3.Error as error:
            print(error)
        return conn

    def create_schema(self, schema_file):
        """Load the schema into the DB."""
        print('Setting up database')
        with open(schema_file, 'rt') as file:
            schema = file.read()
        self.conn.executescript(schema)
        self.conn.commit()

    def sort(self):
        self.notes.sort(key=(lambda n: n.updated))

    def save(self):
        self.conn.commit()

    def read(self):
        self.cursor.execute("select * from note")
        result = self.cursor.fetchall()
        if result is not None:
            notes = []
            for note in result:
                n = nt.Note(*note)
                n.decode()
                notes.append(n)
                self.note_map.update({n.iid:n})
            return notes
        else:
            return []

    def fetch(self, iid):
        self.cursor.execute(f"select * from note where id={iid}")
        result = self.cursor.fetchone()
        if result is not None:
            return nt.Note(*result)
        else:
            return None

    def get_by_id(self, iid):
        return self.note_map.get(iid)

    def get(self, index):
        try:
            return self.notes[index]
        except IndexError:
            return None

    def __len__(self):
        return len(self.notes)

    def last(self):
        return len(self.notes)-1

    def recent(self, num=5):
        start = self.last() - num
        if start < 0:
            start = 0
        return self.notes[start:-1]

    def remove(self, iid):
        self.note_map.pop(iid)
        self.cursor.execute(f"delete from note where id={iid}")

    def new_note(self):
        note = nt.Note()
        self.cursor.execute(f"insert into note (text, created, updated) values (\"{note.text}\", \"{note.created}\", \"{note.updated}\")")
        note.iid = self.cursor.lastrowid
        self.note_map.update({note.iid:note})
        self.notes.append(note)
        return note

    def save_note(self, note):
        note.encode()
        self.cursor.execute(f"update note set text=\"{note.text}\", created=\"{note.created}\", updated=\"{note.updated}\" where id={note.iid}")
        note.saved = True
        note.decode()
        self.sort()

    def purge(self):
        notes = self.read()
        for note in notes:
            if len(note.text) < 1:
                self.remove(note.iid)
        self.save()
