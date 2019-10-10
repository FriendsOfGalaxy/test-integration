import json


with open('manifest.json', 'r') as f:
    manifest = json.load(f)

currver = manifest['version']
major, minor = currver.split('.')

newver = '.'.join([major, str(int(minor) + 1)])
manifest['version'] = newver

with open('manifest.json', 'w') as f:
    json.dump(manifest, f, indent=4)

with open('plugin.py', 'w') as f:
    f.write(f"__version__ = '{newver}'")
