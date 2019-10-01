"""Common tasks shared between all our forks"""

import os
import shlex
import pathlib
import json
import sys
import subprocess

sys.path.insert(0, '.github/workflow')
import config


RELEASE_MESSAGE = "Release version {tag}\n\nVersion {tag}"
RELEASE_FILE ="current_version.json"
RELEASE_FILE_COMMIT_MESSAGE = "Updated current_version.json"
FOG = 'FriendsOfGalaxy'
FOG_EMAIL = 'FriendsOfGalaxy@gmail.com'
BUILD_DIR = os.path.join('..', 'assets')
RELEASE_INFO_FILE = os.path.join('..', 'release_info')


def _run(*args, **kwargs):
    cmd = list(args)
    if len(cmd) == 1:
        cmd = shlex.split(cmd[0])
    kwargs.setdefault("check", True)
    kwargs.setdefault("capture_output", False)
    print('executing', cmd)
    try:
        out = subprocess.run(cmd, **kwargs)
    except subprocess.CalledProcessError as e:
        print(e.output)
        raise
    return out


def load_version():
    manifest_location = os.path.join(config.SRC, 'manifest.json')
    with open(manifest_location, 'r') as f:
        return json.load(f)['version']


def release():
    """Setup env variable VERSION and """
    version_tag = load_version()
    config.package(BUILD_DIR)

    asset_cmd = []
    _, _, filenames = next(os.walk(BUILD_DIR))
    for filename in filenames:
        asset_cmd.append('-a')
        asset_cmd.append(str(pathlib.Path(BUILD_DIR).absolute() / filename))

    # Create and upload github tag and release
    _run('hub', 'release', 'create', version_tag,
        '-m', RELEASE_MESSAGE.format(tag=version_tag),
        *asset_cmd
    )

def update_release_file():
    token = os.environ['GITHUB_TOKEN']
    user_repo_name = os.environ['USER_REPO_NAME']
    version_tag = load_version()

    assets = []
    _, _, filenames = next(os.walk(BUILD_DIR))
    for filename in filenames:
        url = f"https://github.com/{user_repo_name}/releases/download/{version_tag}/{filename}"
        asset = {
            "browser_download_url": url,
            "name": filename
        }
        assets.append(asset)

    data = {
        "tag_name": version_tag,
        "assets": assets
    }
    with open(RELEASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    _run(f'git config user.email {FOG_EMAIL}')
    _run(f'git config user.name {FOG}')
    _run(f'git remote set-url origin https://{FOG}:{token}@github.com/{user_repo_name}.git')

    _run(f'git status')
    _run(f'git config --list')
    _run("git log --graph --pretty=format:'%Cred%h%Creset -%C(yellow)%d%Creset %s %Cgreen(%cr) %C(bold blue)<%an>%Creset' --abbrev-commit --date=relative")

    _run(f'git add {RELEASE_FILE}')
    _run(f'git commit -m {RELEASE_FILE_COMMIT_MESSAGE}')
    _run(f'git push origin master')


if __name__ == "__main__":
    task = sys.argv[1]

    if task == 'release':
        release()
    elif task == 'update_release_file':
        update_release_file()
    else:
        raise RuntimeError('unknown command' + task)
