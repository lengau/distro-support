# Distro Support

This is a small Python library for getting information about when various Linux
distributions are supported.

## Basic usage

```python
from datetime import date
import distro_support

bionic = distro_support.get_support_range("ubuntu", "18.04")
print(bionic.is_supported_on(date.today()))
print(bionic.is_esm_on(date.today()))
```

# Version scheme

This library's versioning scheme is purely based on release date. Breaking changes
will only come with a new year, but are unlikely.
