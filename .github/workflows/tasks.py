"""Common tasks shared between all our forks"""

import os
import sys
import subprocess
from invoke import task

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
    return subprocess.run(cmd, **kwargs)


def load_version():
    manifest_location = os.path.join(config.SRC, 'manifest.json')
    with open(manifest_location, 'r') as f:
        return json.load(f)['version']


@task
def release(c, user_repo_name):
    version_tag = load_version()
    output = 'build'
    asset_filenames = config.deploy(output)
    asset_paths = [os.path.join(output, name) for name in asset_filenames]

    c.run(
        f'hub release create {version_tag}'
        f'-m {RELEASE_TITLE.format(version_tag)}\n{RELEASE_DESC.format(version_tag)}'
        f'-a {" -a ".join(asset_paths)}'
    )

    assets = []
    for filename in asset_filenames:
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

    token = os.environ['GITHUB_TOKEN']
    _run(f'git status')
    _run(f'git remote set-url origin https://{FOG}:{token}@github.com/{user_repo_name}.git')
    _run(f'git add {RELEASE_FILE}')
    _run(f'git commit -m {RELEASE_FILE_COMMIT_MESSAGE}')