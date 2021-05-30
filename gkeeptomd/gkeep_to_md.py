import argparse
import getpass
import json
import os
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


def _create_argument_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser()
    parser.add_argument('label', help='the label to search/save')
    parser.add_argument(
        'outfile', help='the (markdown) file to write the result to',
    )
    parser.add_argument(
        '--username', help='the username to use for login (only availble when\
        your password is saved already)',
    )
    parser.add_argument(
        '--save-login', action='store_true',
        help='login info will be saved, next time provide --username to login',
    )

    # TODO: implement
    parser.add_argument(
        '--no-archive', action='store_true',
        help='do notarchive notes that have been added to the markdown file',
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

    cached_state = _load_cache()
    if cached_state is not None:
        keep.restore(cached_state)

    print(f"Searching for label: {args['label']}")
    gknotes = keep.find(labels=[keep.findLabel(args['label'])])

    for note in gknotes:
        if isinstance(note, gkeepapi._node.List):
            # If it's a list make a todo list in md
            raise NotImplementedError
        else:
            # write to the markdown file
            raise NotImplementedError

    _save_cache(keep.dump())

    return 0
