import os
from pathlib import Path

import yaml
from adaptix import Retort


def load_config[T](config_type: type[T], path: str | Path | None = None) -> T:
    path = path or os.getenv("CONFIG_PATH")
    if path is None:
        msg = "Environment variable 'CONFIG_PATH' must be set."
        raise RuntimeError(msg)

    with open(path) as f:
        data = yaml.safe_load(f)

    retort = Retort(strict_coercion=False)
    return retort.load(data, config_type)  # type: ignore[no-any-return]
