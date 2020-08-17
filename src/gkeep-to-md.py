import fire
from keep import Keep
from PyInquirer import prompt


class App:

    def __init__(self):
        self.keep = Keep()

    def _login(self, username):
        if username != '':
            self.keep.login(username, '')
            if self.keep.loggedIn:
                return

        qs = [
            {
                "type": "input",
                "message": "Enter username:",
                "name": "username"
            },
            {
                "type": "password",
                "message": "Enter password:",
                "name": "password"
            }
        ]

        a = prompt(qs)
        self.keep.login(a['username'], a['password'])

    def create(self, tag, outputfile, username=''):
        if not self.keep.loggedIn:
            self._login(username)

        self.keep.saveNotesToFile(self.keep.getNotesByTag(tag), outputfile)


if __name__ == "__main__":
    fire.Fire(App)
