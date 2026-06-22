from pathlib import Path
import sys
import re

if len(sys.argv) < 3:
    raise TypeError("Missing arguments: version number and architecture")

version = sys.argv[1]
architecture = sys.argv[2]

if not re.compile("^\d+\.\d+\.\d+(-.*)?$").match(version):
    raise ValueError("Invalid version number {}".format(version))

if not re.compile(r"^[A-Za-z0-9_-]+$").match(architecture):
    raise ValueError("Invalid architecture {}".format(architecture))

path = Path("version.py")
path.write_text("__version__ = \"{}\"".format(version))

file_paths = ["app.spec", "version_info.txt", "version_info_analyze.txt", "app.ifp", "build_dmg.sh"]

version_parts = version.split(".")
major = version_parts[0]
minor = version_parts[1]
patch = version_parts[2].split("-")[0]

for file_path in file_paths:
    with open(file_path, "r") as f:
        content = f.read()

    content = content.replace("{{ version }}", version)
    content = content.replace("{{ major }}", major)
    content = content.replace("{{ minor }}", minor)
    content = content.replace("{{ patch }}", patch)
    content = content.replace("{{ architecture }}", architecture)

    with open(file_path, "w") as f:
        f.write(content)
