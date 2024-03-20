"""Quantinuum Nexus API client."""

import os
from functools import reduce
from pathlib import Path
from typing import Annotated, Any, Dict

from click import ClickException
from colorama import Fore
from pydantic import BaseModel, BeforeValidator, ConfigDict

from .consts import CONFIG_FILE_NAME


class Config(BaseModel):
    """QNexus Configuration schema."""

    model_config = ConfigDict(coerce_numbers_to_str=True, extra="allow")
    project_name: Annotated[str, BeforeValidator(lambda v: None if v == "" else v)]
    optimization_level: int = 1
    protocol: str = "https"
    websockets_protocol: str = "wss"
    domain: str = "staging.myqos.com"

    def __str__(self) -> str:
        out: str = ""
        out += Fore.MAGENTA + "Current QNexus Environment: \n"
        for key, field in self.model_fields.items():
            required = "(Required)" if field.is_required() else ""
            value = getattr(self, key).__str__()
            out += f"{Fore.CYAN + key} = {Fore.GREEN + value} {Fore.LIGHTBLUE_EX + required}\n"
        return out
    
    @property
    def url(self) -> str:
        return f"{self.protocol}://{self.domain}"
    
    @property
    def websockets_url(self) -> str:
        return f"{self.websockets_protocol}://{self.domain}"


def get_config_file_paths():
    """Get paths of all configuration files in the current tree."""

    cwd = os.path.dirname(__file__)
    config_files = []
    tree = Path(cwd).parents
    for directory_name in tree:
        config_path = f"{directory_name}/{CONFIG_FILE_NAME}"
        directory_has_config = os.path.isfile(config_path)
        if directory_has_config:
            config_files.append(config_path)
    return config_files


def parse_config_file(path: str) -> Dict[str, Any]:
    """Read a config of key value pairs as a dict"""
    env_vars = {}
    with open(path, encoding="UTF-8") as myfile:
        for line in myfile:
            name, var = line.partition("=")[::2]
            env_vars[name.strip()] = var.strip()
    return env_vars


def get_config() -> Config:
    """Get config"""
    config_file_paths = get_config_file_paths()
    if len(config_file_paths) > 0:
        configs = [
            parse_config_file(config_file_path)
            for config_file_path in config_file_paths
        ]
        configs.reverse()  # Nearest directory takes precendence
        resolved_config = reduce(lambda a, b: dict(a, **b), configs)
        return Config(**resolved_config)

    raise ClickException(Fore.RED + f"No project found. {CONFIG_FILE_NAME} not found.")
