"""Common tasks shared between all our forks"""

import os
import sys
import json
import shlex
import pathlib
import subprocess
import urllib.request
from distutils.version import StrictVersion

sys.path.insert(0, '.github/workflow')
import config


GITHUB = 'https://github.com'
FOG = 'FriendsOfGalaxy'
FOG_EMAIL = 'FriendsOfGalaxy@gmail.com'

FOG_BASE_BRANCH = 'master'
PR_BRANCH = 'autoupdate'
PATHS_TO_EXCLUDE = ['README.md', 'current_version.json']

RELEASE_MESSAGE = "Release version {tag}\n\nVersion {tag}"
RELEASE_FILE ="current_version.json"
RELEASE_FILE_COMMIT_MESSAGE = "Updated current_version.json"
BUILD_DIR = os.path.join('..', 'assets')
RELEASE_INFO_FILE = os.path.join('..', 'release_info')


def _run(*args, **kwargs):
    cmd = list(args)
    if len(cmd) == 1:
        cmd = shlex.split(cmd[0])
    kwargs.setdefault("check", True)
    kwargs.setdefault("capture_output", True)
    kwargs.setdefault("text", True)
    print('executing', cmd)
    try:
        out = subprocess.run(cmd, **kwargs)
    except subprocess.CalledProcessError as e:
        print('><', e.output, e.stderr)
        raise
    if out.stdout:
        print('>>', out.stdout)
    return out


def _load_version():
    with open(config.MANIFEST_LOCATION, 'r') as f:
        return json.load(f)['version']


def _load_upstream_version():
    upstream = config.UPSTREAM
    if upstream.startswith(GITHUB):
        upstream_repo = upstream.split('/', 3)[-1]
        url = f'https://raw.githubusercontent.com/{upstream_repo}/{config.RELEASE_BRANCH}/{config.MANIFEST_LOCATION}'
    else:
        raise NotImplementedError('other services than github not supported')

    resp = urllib.request.urlopen(url)
    upstream_manifest = json.loads(resp.read().decode('utf-8'))
    return upstream_manifest['version']


def _fog_git_init(upstream=None):
    token = os.environ['GITHUB_TOKEN']
    repository = os.environ['REPOSITORY']
    origin = f'https://{FOG}:{token}@github.com/{repository}.git'

    _run(f'git config user.name {FOG}')
    _run(f'git config user.email {FOG_EMAIL}')
    _run(f'git remote set-url origin {origin}')
    if upstream is not None:
        _run(f'git remote add upstream {upstream}')


def _is_pr_open():
    proc = _run(f'hub pr list -s open -b {FOG_BASE_BRANCH} -h {PR_BRANCH}')
    print('pull requests:', proc.stdout, bool(proc.stdout))
    return bool(proc.stdout)  # empty output means no PR open


def _create_pr():
    version = _load_version()
    print('preparing pull-request for version', version)
    pr_title = f"Version {version}"
    pr_message = "Sync with the original repository"
    _run(
        f'hub pull-request --base {FOG}:{FOG_BASE_BRANCH} --head {FOG}:{PR_BRANCH} '
        f'-m "{pr_title}" -m "{pr_message}" --labels autoupdate'
    )


def _sync_pr(release_branch):
    """ Synchronize upstream changes to origin/PR_BRANCH
    """
    _run('git fetch upstream')

    try:
        _run(f'git checkout -b {PR_BRANCH} --track origin/{PR_BRANCH}')
    except subprocess.CalledProcessError:
        _run(f'git checkout -b {PR_BRANCH}')
        _run(f'git push -u origin {PR_BRANCH}')
    else:
        _run(f'git pull origin {PR_BRANCH}')

    print(f'merging latest release branch {release_branch}')
    _run(f'git merge --no-commit --no-ff upstream/{release_branch}')

    print('excluding reserved files')
    # reset .github/workflows content
    # _run('rm -r ./github/workflows/*.yml')
    _run(f'git checkout origin/{FOG_BASE_BRANCH} -- {" ".join(PATHS_TO_EXCLUDE)}')
    _run(f'git status')

    proc = _run(f'git commit -m "Merge upstream"')
    _run(f'git push origin {PR_BRANCH}')


def sync():
    """Started from master branch"""
    _fog_git_init(config.UPSTREAM)

    pr_branch_version = _load_version()
    upstream_version = _load_upstream_version()

    if StrictVersion(upstream_version) > StrictVersion(pr_branch_version):
        _sync_pr(config.RELEASE_BRANCH)
        if not _is_pr_open():
            _create_pr()
    else:
        print(f'No new version found in upstream {UPSTREAM} to be sync')


def release():
    """Setup env variable VERSION and """
    version_tag = _load_version()
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
    version_tag = _load_version()

    proc = _run(f'hub release show --show-downloads {version_tag}', text=True)
    lines = proc.stdout.split()
    zip_urls = [ln for ln in lines if ln.endswith('.zip')]

    assets = []
    for url in zip_urls:
        asset = {
            "browser_download_url": url,
            "name": url.split('/')[-1]
        }
        assets.append(asset)
    data = {
        "tag_name": version_tag,
        "assets": assets
    }
    with open(RELEASE_FILE, 'w') as f:
        json.dump(data, f, indent=4)

    _fog_git_init()

    _run(f'git add {RELEASE_FILE}')
    _run(f'git commit -m {RELEASE_FILE_COMMIT_MESSAGE}')
    _run(f'git push origin HEAD:{FOG_BASE_BRANCH}')


if __name__ == "__main__":
    task = sys.argv[1]

    if task == 'release':
        release()
    elif task == 'update_release_file':
        update_release_file()
    elif task == 'sync':
        sync()
    else:
        raise RuntimeError(f'unknown command {task}')
