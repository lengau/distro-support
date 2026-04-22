"""Update distribution support data."""

import json
import pathlib

from distro_support import alpine, debian, devuan, rhel, ubuntu


def update(module):
    data_path = pathlib.Path(module.__file__).with_suffix(".json")
    data_path.write_text(
        json.dumps(module.get_distro_info(), indent="  ", sort_keys=True) + "\n"
    )


if __name__ == "__main__":
    print("Updating Ubuntu data")
    update(ubuntu)
    print("Updating Debian data")
    update(debian)
    print("Updating Devuan data")
    update(devuan)
    print("Updating Alpine data")
    update(alpine)
    print("Updating RHEL data")
    update(rhel)
