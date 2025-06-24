"""Update distribution support data."""

import json
import pathlib

from distro_support import ubuntu


def update_ubuntu():
    ubuntu_data = pathlib.Path(ubuntu.__file__).with_suffix(".json")
    ubuntu_data.write_text(json.dumps(ubuntu.get_distro_info(), indent="  "))


if __name__ == "__main__":
    update_ubuntu()
