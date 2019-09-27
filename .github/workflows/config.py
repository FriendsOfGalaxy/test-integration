import os
import shutil

# -------- consts ---------

SRC = '.'  # repo root


# --------- jobs -----------

def build():
    pass


def deploy(output):
    """Generate zip assests in output path."""

    if os.path.exists(output):
        shutil.rmtree(output)
    os.makedirs(output)

    zip_names = ['windows', 'macos']
    for zip_name in zip_names:
        asset = os.path.join(output, zip_name)
        shutil.make_archive(asset, 'zip', root_dir=SRC, base_dir='.')

    return [n + '.zip' for n in zip_names]
