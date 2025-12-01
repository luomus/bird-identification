from version import __version__

file_paths = ["version_info.txt", "version_info_analyze.txt", "app.ifp"]

for file_path in file_paths:
    with open(file_path, "r") as f:
        content = f.read()

    content = content.replace("{{ version }}", __version__)

    with open(file_path, "w") as f:
        f.write(content)
