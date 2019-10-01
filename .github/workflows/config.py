import os
import shutil

# -------- consts ---------

# paths relative to repository root
SRC = '.'
MANIFEST_LOCATION = 'manifest.json'

UPSTREAM = 'https://github.com/FriendsOfGalaxyTester/test-integration'
RELEASE_BRANCH = 'master'  # branch to be checked for new updates


# --------- jobs -----------

def build():
    pass


def package(output):
    """Generate zip assests in output path."""

    if os.path.exists(output):
        shutil.rmtree(output)
    os.makedirs(output)

    zip_names = ['windows', 'macos']
    for zip_name in zip_names:
        asset = os.path.join(output, zip_name)
        shutil.make_archive(asset, 'zip', root_dir=SRC, base_dir='.')
