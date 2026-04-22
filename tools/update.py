"""Update distribution support data."""

import json
import pathlib

from distro_support import alpine, debian, devuan, ubuntu


def update(module):
    ubuntu_data = pathlib.Path(module.__file__).with_suffix(".json")
    ubuntu_data.write_text(json.dumps(module.get_distro_info(), indent="  ") + "\n")


if __name__ == "__main__":
    print("Updating Ubuntu data")
    update(ubuntu)
    print("Updating Debian data")
    update(debian)
    print("Updating Devuan data")
    update(devuan)
    print("Updating Alpine data")
    update(alpine)
