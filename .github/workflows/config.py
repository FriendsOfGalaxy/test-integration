import os
import shutil

# -------- consts ---------

# url of original repository from github
UPSTREAM = 'https://github.com/FriendsOfGalaxyTester/test-integration'
# branch to be checked for new updates
RELEASE_BRANCH = 'master'
# integration source directory, where the manifest.json is placed; relative to root repo dir
SRC = '.'

# --------- jobs -----------

def build():
    pass


def pack(output):
    """Generate zip assests in output path."""
    if os.path.exists(output):
        shutil.rmtree(output)
    os.makedirs(output)

    zip_names = ['windows', 'macos']
    for zip_name in zip_names:
        asset = os.path.join(output, zip_name)
        shutil.make_archive(asset, 'zip', root_dir=SRC, base_dir='.')
