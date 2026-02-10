from pathlib import Path
import sys
import re

if len(sys.argv) < 2:
    raise TypeError("Missing version number argument")

version = sys.argv[1]

if not re.compile("^\d+\.\d+\.\d+$").match(version):
    raise ValueError("Invalid version number {}".format(version))

path = Path("version.py")
path.write_text("__version__ = \"{}\"".format(version))

file_paths = ["app.spec", "version_info.txt", "version_info_analyze.txt", "app.ifp", "build_dmg.sh"]

version_parts = version.split(".")
major = version_parts[0]
minor = version_parts[1]
patch = version_parts[2]

for file_path in file_paths:
    with open(file_path, "r") as f:
        content = f.read()

    content = content.replace("{{ version }}", version)
    content = content.replace("{{ major }}", major)
    content = content.replace("{{ minor }}", minor)
    content = content.replace("{{ patch }}", patch)

    with open(file_path, "w") as f:
        f.write(content)
