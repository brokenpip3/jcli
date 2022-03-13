# -*- coding: utf-8 -*-
# adjusted from https://raw.githubusercontent.com/mbovo/pdh/main/src/pdh/config.py

import yaml
import os
import sys
from typing import Any
from rich import print
from rich.prompt import Prompt
from appdirs import AppDirs

_APPNAME = "jcli"
_AUTHOR = "brokenpip3"
dirs = AppDirs(_APPNAME, _AUTHOR)

REQUIRED_KEYS = ["server", "user", "password"]


class Config(object):
    cfg = {}

    def __init__(self) -> None:
        super().__init__()
        self.cfg = {}

    def from_yaml(self, path, key: str = None) -> None:
        """Load configuration from a yaml file, store it directly or under the specified key (if any)"""

        with open(os.path.expanduser(path), "r") as f:
            o = yaml.safe_load(f.read())
        if key:
            self.cfg[key] = o
        else:
            self.cfg.update(o)

    def to_yaml(self, fileName: str) -> None:
        with open(os.path.expanduser(fileName), "w") as f:
            yaml.safe_dump(self.cfg, f)

    def validate(self) -> bool:
        for k in REQUIRED_KEYS:
            if k not in self.cfg.keys():
                return False
        return True

    def __getitem__(self, key: str) -> Any:
        return self.cfg[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.cfg[key] = value

    def __repr__(self) -> str:
        return repr(self.cfg)

    def __str__(self) -> str:
        return repr(self.cfg)

    def __contains__(self, key):
        return key in self.cfg


config = Config()
cdir = dirs.user_config_dir
cf = f"{cdir}/jcli.yaml"


def load_and_validate() -> dict:
    config.from_yaml(cf)
    if not config.validate():
        print(":attention: [red]Invalid or missing config, try jcli config[/red]")
        sys.exit(1)
    return config


def setup_config() -> None:
    if not os.path.exists(cdir):
        os.makedirs(cdir)
    else:
        print("Config dir already exist, check the configuration manually")
        sys.exit(1)

    sensibledata = ["password", "pass", "token", "auth"]
    print("Please insert the following config")
    for k in REQUIRED_KEYS:
        if k not in sensibledata:
            config[k] = Prompt.ask(f"Add Jenkins {k}")
        else:
            config[k] = Prompt.ask(f"Add Jenkins {k}", password=True)
    config.to_yaml(cf)
