# Google Keep notes to markdown

> Get notes from google keep and save them to a markdown file

## Installation

Close this repository
```bash
$ git clone git@github.com:twanh/gkeep-to-md
```

`cd` into the cloned directory
```bash
$ cd gkeep-to-md/
```

Install using pip
```bash
$ pip install .
```

Now you can use `gkeeptomd`

```bash
$ gkeeptomd --help
```
or use
```bash
$ python -m gkeeptomd --help
```


## Usage:

> `gkeeptomd` requires you to be logged in to google keep. It will ask you for your credentials when using it. It is recommended to use an app password from google, see [their support](https://support.google.com/accounts/answer/185833?hl=en).


```console
usage: gkeeptomd [-h] [--username USERNAME] [--save-login] [--search-archive]
                 [--no-archive] [--heading-level HEADING_LEVEL] [--verbose]
                 label outfile

Get notes from google keep and save them to a markdown file

positional arguments:
  label                 the label to search/save (if "*" then all notes will
                        be saved)
  outfile               the (markdown) file to write the result to

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME   the username to use for login (only availble when your
                        password is saved already)
  --save-login          login info will be saved, next time provide --username
                        to login
  --search-archive      include archived notes in the search
  --no-archive          do not archive notes that have been added to the
                        markdown file
  --heading-level HEADING_LEVEL
                        the heading level to use for the markdown headings
                        (default: 3)
  --verbose             turn on verbose mode
```

#### Example usage

Save all notes with label `saveme` to file `notes.md`

```
$ gkeeptomd saveme notes.md
```

### Label

The label you want to search for. When using `'*'` all your notes will be saved.

### Save login and `--username`

You can save your credentials by using the `--save-login` flag.

This will use `keyring` to store the google keep token so you do not need to use your password again.

However: when you want to use the tool again, you need to provide the `--username` flag with your username, this way you can have multiple accounts saved.

### Heading level

By default all note titles will have be a heading 3 (`###` in markdown), this can be changed using the `--heading-level` flag.

For example: `--heading-level 5` would make all headings `#####`

### No archive

By default notes that are saved will be archived to avoid duplication. You can turn off the archiving using the `--no-archive` flag.


### Search archive

Saved notes are archived by default, however sometimes you want to get those notes as well, that can be done using the `--search-archive` flag.
