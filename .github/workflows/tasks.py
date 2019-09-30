"""Common tasks shared between all our forks"""

import os
import json
import sys
import subprocess

sys.path.insert(0, '.github/workflow')
import config


RELEASE_TITLE = "Release version {}"
RELEASE_DESC = "Version {}"
RELEASE_FILE ="current_version.json"
RELEASE_FILE_COMMIT_MESSAGE = "Updated current_version.json"
FOG = 'FriendsOfGalaxy'



def _run(*args, **kwargs):
    kwargs.setdefault("check", True)
    kwargs.setdefault("capture_output", False)
    cmd = list(args)
    # print('executing', cmd)
    return subprocess.run(cmd, **kwargs)


def load_version():
    manifest_location = os.path.join(config.SRC, 'manifest.json')
    with open(manifest_location, 'r') as f:
        return json.load(f)['version']


def release():
    token = os.environ['GITHUB_TOKEN']
    user_repo_name = os.environ['USER_REPO_NAME']

    version_tag = load_version()

    # parent dir in case SRC is curr dir
    output = os.path.join('..', 'build')
    print('preparing deploy files')
    asset_paths = config.deploy('../build')

    _run(
        f'hub release create {version_tag}'
        f'-m {RELEASE_TITLE.format(version_tag)}\n{RELEASE_DESC.format(version_tag)}'
        f'-a {" -a ".join(asset_paths)}'
    )

    assets = []
    for filename in os.path.basename(asset_paths):
        print(filename)
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

    _run(f'git status')
    _run(f'git remote set-url origin https://{FOG}:{token}@github.com/{user_repo_name}.git')
    _run(f'git add {RELEASE_FILE}')
    _run(f'git commit -m {RELEASE_FILE_COMMIT_MESSAGE}')


if __name__ == "__main__":
    task = sys.argv[1]
    if task == 'release':
        release()