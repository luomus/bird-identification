from version import __version__

file_paths = ["version_info.txt", "version_info_analyze.txt", "app.ifp"]

version_parts = __version__.split(".")
major = version_parts[0]
minor = version_parts[1]
patch = version_parts[2]

for file_path in file_paths:
    with open(file_path, "r") as f:
        content = f.read()

    content = content.replace("{{ version }}", __version__)
    content = content.replace("{{ major }}", major)
    content = content.replace("{{ minor }}", minor)
    content = content.replace("{{ patch }}", patch)

    with open(file_path, "w") as f:
        f.write(content)
