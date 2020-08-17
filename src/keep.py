import gkeepapi
import keyring
import os
import json
from validators import url as isUrl

# PW:


class MD:

    @staticmethod
    def h3(text):
        return f'### {text} \n'

    @staticmethod
    def link(text, url):
        return f'[{text}]({url})\n'

    @staticmethod
    def text(text):
        return f"{text}\n"


class Keep:

    def __init__(self):
        self.keep = gkeepapi.Keep()
        self.loggedIn = False
        self.cacheFilename = 'statefile.json'

    def getCache(self) -> dict:
        # This function assumes that the cache exists!
        with open(self.cacheFilename, 'r') as f:
            state = json.load(f)
            return state

    def _cacheExists(self) -> bool:
        if os.path.exists(self.cacheFilename):
            return True

        return False

    def loadCache(self) -> None:
        self.keep.restore(self.getCache())

    def saveCache(self) -> None:
        state = self.keep.dump()
        with open(self.cacheFilename, 'w') as f:
            json.dump(state, f)

    def login(self, username: str, password: str) -> None:
        # Check if there is a saved token!
        token = keyring.get_password("gkeep-token", username)
        # If there is a token saved login using the token
        if token:
            # print('Token found and used')
            if self._cacheExists():
                # print('Using cache')
                self.keep.resume(username, token, state=self.loadCache())
            else:
                self.keep.resume(username, token)
                self.saveCache()

            self.loggedIn = True
            return

        # Login using the username and password if there is no token
        if self._cacheExists():
            # print("Logging in using cache")
            self.loggedIn = self.keep.login(
                username, password, state=self.loadCache())
        else:
            self.loggedIn = self.keep.login(
                username, password)
            self.saveCache()

        if not self.loggedIn:
            # TODO: raise error
            # print("Could not login!")
            return

        # Save the token if the loggin was successful
        token = self.keep.getMasterToken()
        keyring.set_password('gkeep-token', username, token)

    def getNotesByTag(self, tag: str) -> list:
        return self.keep.find(labels=[self.keep.findLabel(tag)])

    def noteToMd(self, note):
        mdNote = ''
        # If the text is an url, then it is a saved weblink
        if isUrl(note.text.split('\n')[0]):
            print('found url')
            mdNote += MD.h3(note.title)
            mdNote += MD.link(note.title, note.text.split('\n')[0])
            mdNote += MD.text(note.text.split('\n')[1])
        else:  # Just a regular note
            mdNote += MD.h3(note.title)
            mdNote += MD.text(note.text)
        return mdNote

    def saveNotesToFile(self, notes: list, filename: str) -> None:
        with open(filename, 'a+') as f:
            for note in notes:
                if not note.archived:
                    f.write(self.noteToMd(note))
                    note.archived = True
        self.keep.sync()
