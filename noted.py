import os
from pynput import keyboard
from db import NoteDB
from shortcuts import shortcuts, hotkeys


class Noted:
    def __init__(self):
        self.db = NoteDB()
        self.active_note = self.db.new_note()
        self.index = self.db.last()
        self.cmd = False
        self.alt = False
        self.ctrl = False
        self.buffer = ""
        self.shortcut = ""
        self.cls()
        print("duly noted\n\n>", end=" ")

    def cls(self):
        os.system('cls' if os.name=='nt' else 'clear')

    def handle_shortcut(self):
        cut = hotkeys.get(self.shortcut)
        if cut is not None:
            self.shortcut = ""
            eval(cut)
        else:
            cut = shortcuts.get(self.shortcut)
            if cut is not None:
                self.active_note.append(cut)
            else:
                self.active_note.append(self.shortcut)
            self.cls()
            print(">>", self.active_note.text, end="", flush=True)

    def handle_alpha(self, key):
        if self.cmd or self.ctrl or self.alt and type(key) == keyboard.KeyCode:
            self.buffer = key.char.lower()
        elif type(key) == keyboard.KeyCode and key.char == ";":
            self.shortcut = ";"
        elif len(self.shortcut) > 0:
            if key == keyboard.Key.space:
                if len(self.shortcut) == 1:
                    self.active_note.append("; ")
                    self.shortcut = ""
                else:
                    self.handle_shortcut()
            elif type(key) == keyboard.KeyCode:
                self.shortcut += key.char
        else:
            if self.active_note is None:
                self.active_note = self.db.new_note()
            if key == keyboard.Key.space:
                self.active_note.append(" ")
            elif key == keyboard.Key.enter:
                self.active_note.append("\n")
            elif key == keyboard.Key.tab:
                self.active_note.append("\t")
            elif type(key) == keyboard.KeyCode:
                self.active_note.append(key.char)

    def on_press(self, key):
        self.index = self.db.notes.index(self.active_note)
        if (type(key) == keyboard.KeyCode or key == keyboard.Key.space
            or key == keyboard.Key.enter or key == keyboard.Key.tab):
            self.handle_alpha(key)
        elif type(key) == keyboard.Key:
            if key == keyboard.Key.ctrl:
                self.ctrl = True
            elif key == keyboard.Key.cmd:
                self.cmd = True
            elif key == keyboard.Key.alt:
                self.alt = True
            elif key == keyboard.Key.backspace:
                self.active_note.backspace()
            elif key == keyboard.Key.shift:
                pass
            elif key == keyboard.Key.esc:
                pass
            elif key == keyboard.Key.left or key == keyboard.Key.up:
                self.prev()
            elif key == keyboard.Key.right or key == keyboard.Key.down:
                self.next()
            else:
                pass
                # print('>{0}<'.format(key))
        else:
            print("None")
        # print(f"--{self.index}--")

    def on_release(self, key):
        # print('{0} released'.format(
        #     key))
        if self.cmd or self.ctrl or self.alt:
            if self.buffer == "s":
                self.save()
            elif self.buffer == "n":
                self.new_note()
            elif self.buffer == "t":
                self.recents()
            elif self.buffer == "x":
                self.delete_note(self.active_note.iid)
            elif self.buffer == "z":
                self.revert()
            elif self.buffer == "q":
                return self.quit()
        self.cmd = False
        self.ctrl = False
        self.alt = False
        if key == keyboard.Key.esc:
            # Stop listener
            return self.quit()

    def save(self):
        self.cls()
        print("save\n>>", self.active_note.text, end="", flush=True)
        self.db.save_note(self.active_note)
        self.db.save()

    def new_note(self):
        self.cls()
        print("new\n>>", end=" ", flush=True)
        self.active_note = self.db.new_note()

    def recents(self, num=5):
        self.cls()
        recents = self.db.recent(num)
        for note in recents:
            print(f"{note.text}\n")
        print(">> ", end="", flush=True)

    def delete_note(self, iid):
        self.cls()
        print("delete\n>>", end=" ", flush=True)
        self.db.remove(iid)
        self.active_note = self.db.new_note()

    def revert(self):
        self.cls()
        self.active_note = self.db.get(self.active_note.iid)
        print("revert\n>>", self.active_note.text, end="", flush=True)

    def quit(self):
        self.cls()
        print("\nquit")
        self.db.purge()
        self.db.save()
        return False

    def prev(self):
        if self.index > 0:
            self.index -= 1
        self.active_note = self.db.get(self.index)
        self.cls()
        print(f"{self.index+1}/{len(self.db)}: {self.active_note.text}", end="",
              flush=True)

    def next(self):
        if self.index < len(self.db)-1:
            self.index += 1
        self.active_note = self.db.get(self.index)
        self.cls()
        print(f"{self.index+1}/{len(self.db)}: {self.active_note.text}", end="",
              flush=True)


if __name__ == "__main__":
     noted = Noted()
     with keyboard.Listener(
        on_press=noted.on_press,
        on_release=noted.on_release) as listener:
        listener.join()
