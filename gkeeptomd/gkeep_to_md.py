import argparse
import getpass
import json
import os
import re
import sys
from typing import Any
from typing import Optional
from typing import Sequence

import gkeepapi
import keyring
from appdirs import user_cache_dir

from gkeeptomd import __author__
from gkeeptomd import __version__
from gkeeptomd import app_name

PASSWORD_TOKEN = 'gkeep-to-md-gkeep-password'
CACHE_FILE_NAME = 'gkeepnotes.json'

LINK_RE = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'  # noqa: E501

DEFAULT_HEADING_LEVEL = 3


def _create_argument_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser()
    parser.add_argument('label', help='the label to search/save')
    parser.add_argument(
        'outfile',
        help='the (markdown) file to write the result to',
    )

    parser.add_argument(
        '--username',
        help='the username to use for login (only availble when\
        your password is saved already)',
    )
    parser.add_argument(
        '--save-login',
        action='store_true',
        help='login info will be saved, next time provide --username to login',
    )

    parser.add_argument(
        '--search-archive',
        action='store_true',
        help='include archived notes in the search',
    )

    parser.add_argument(
        '--no-archive',
        action='store_true',
        help='do not archive notes that have been added to the markdown file',
    )

    parser.add_argument(
        '--heading-level',
        default=3,
        type=int,
        help='the heading level to use for the markdown headings (default: 3)',
    )

    return parser


def _get_login() -> tuple[str, str]:

    print('Please login with your google information, it is recommended to use\
          an app password!')
    username = input('Username: ').strip()
    password = getpass.getpass('Password (input hidden): ')

    return username, password


def _load_cache() -> Optional[dict[str, Any]]:

    # TODO: Implement verbose mode
    print('Checking if state is saved')

    cache_file_path = os.path.join(
        user_cache_dir(
            app_name, __author__, __version__,
        ), CACHE_FILE_NAME,
    )
    if os.path.isfile(cache_file_path):
        print('Found cache')
        with open(cache_file_path, 'r') as f:
            state = json.load(f)
        return state

    print('No cache file found')
    return None


def _save_cache(state: Any) -> None:

    cache_file_path = os.path.join(
        user_cache_dir(
            app_name, __author__, __version__,
        ), CACHE_FILE_NAME,
    )

    # If the cache dir does not exist create it
    if not os.path.isdir(os.path.dirname(cache_file_path)):
        print('Making the cache dir')
        os.makedirs(os.path.dirname(cache_file_path))

    # Write the state
    print('Saving cache')
    with open(cache_file_path, 'w') as f:
        json.dump(state, f)


def _list_note_to_markdown(note: gkeepapi._node.List) -> str:
    '''Turns a google keep list to a markdown list'''

    if not note.title:  # type: ignore
        heading = f'{"#" * DEFAULT_HEADING_LEVEL} <empty title>'
    else:
        # type: ignore
        heading = f'{"#" * DEFAULT_HEADING_LEVEL} {note.title}\n\n'

    body = ''

    for list_item in note.items:
        text = list_item.text
        checked = list_item.checked
        new_line = f'{"- [x] " if checked else "- [ ] "} {text}\n'
        body += new_line

        for sub_item in list_item.subitems:
            s_text = sub_item.text
            s_checked = sub_item.checked
            s_new_line = f'  {"- [x] " if s_checked else "- [ ] "} {s_text}\n'
            body += s_new_line

    return heading + body + '\n'


def _create_md_link_from_re(match: re.Match) -> str:
    return f'[{match.group()}]({match.group()})'


def _text_note_to_markdown(note: gkeepapi._node.Node) -> str:

    # type: ignore
    heading = f'{"#" * DEFAULT_HEADING_LEVEL} {note.title or "<empty>"}\n\n'

    body: str = note.text
    body = re.sub(LINK_RE, _create_md_link_from_re, body)

    return heading + body + '\n'


def main(argv: Optional[Sequence[str]] = None) -> int:

    if argv is None:
        argv = sys.argv[1:]

    parser = _create_argument_parser()
    args = vars(parser.parse_args(argv))
    keep = gkeepapi.Keep()

    if args['username'] is not None:
        token = keyring.get_password(PASSWORD_TOKEN, args['username'])
        if token is None:
            print(
                f"No saved password found for username: {args['username']}, ",
                'please run without --username flag to login',
            )
            return 1

        print('Logging you in...')
        try:
            keep.resume(args['username'], token)
        except gkeepapi.exception.LoginException:
            print(
                'Could not log you in, please try again without the',
                ' --username flag',
            )
            return 1
    else:
        username, password = _get_login()
        print('Logging you in')
        try:
            keep.login(username, password)
        except gkeepapi.exception.LoginException:
            print('Could not log you in!')
            return 1

        if args['save_login']:
            token = keep.getMasterToken()
            keyring.set_password(PASSWORD_TOKEN, username, token)

    print('Logged in successfully!')

    # XXX: Global const
    if args['heading_level'] != 3:
        global DEFAULT_HEADING_LEVEL
        DEFAULT_HEADING_LEVEL = args['heading_level']

    cached_state = _load_cache()
    if cached_state is not None:
        keep.restore(cached_state)

    keep.sync()

    print(f"Searching for label: {args['label']}")

    extra_options = {}
    if not args['search_archive']:
        extra_options['archived'] = False

    gknotes = keep.find(
        labels=[keep.findLabel(args['label'])], **extra_options,
    )

    markdown = ''

    for note in gknotes:

        if isinstance(note, gkeepapi._node.List):
            # If it's a list make a todo list in md
            markdown += _list_note_to_markdown(note)
        else:
            markdown += _text_note_to_markdown(note)

        if not args['no_archive']:
            print('Archiving note')
            note.archived = True

    keep.sync()

    with open(args['outfile'], 'a') as f:
        f.write(markdown)

    _save_cache(keep.dump())

    return 0
