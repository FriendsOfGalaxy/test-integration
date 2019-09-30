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
BUILD_DIR = os.path.join('..', 'assets')


def _run(*args, **kwargs):
    kwargs.setdefault("check", True)
    kwargs.setdefault("capture_output", False)
    cmd = list(args)
    print('executing', cmd)
    return subprocess.run(cmd, **kwargs)


def load_version():
    manifest_location = os.path.join(config.SRC, 'manifest.json')
    with open(manifest_location, 'r') as f:
        return json.load(f)['version']


def package():
    """Setup env variable VERSION and """
    asset_paths = config.package(BUILD_DIR)
    return load_version()

    # # Alternatively - release with hub
    # _run('hub', 'release', 'create', version_tag,
    #     '-m', RELEASE_TITLE.format(version_tag),
    #     '-m', RELEASE_DESC.format(version_tag),
    #     '-a', " -a ".join(asset_paths)
    # )

def update_release_file():
    token = os.environ['GITHUB_TOKEN']
    user_repo_name = os.environ['USER_REPO_NAME']
    version_tag = load_version()

    assets = []
    for _, _, filename in os.walk(BUILD_DIR):
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
    print(data)
    with open(RELEASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    _run('git', 'status')
    _run('git', 'remote', 'set-url', 'origin', f'https://{FOG}:{token}@github.com/{user_repo_name}.git')
    _run('git', 'add', RELEASE_FILE)
    _run('git', 'commit', '-m', RELEASE_FILE_COMMIT_MESSAGE)


if __name__ == "__main__":
    task = sys.argv[1]
    if task == 'package':
        package()
    if task == 'update_release_file':
        update_release_file()
