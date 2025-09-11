import os
import itertools
from typing import NamedTuple, Callable

import vdf
from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString
from ruamel.yaml.comments import CommentedMap

output_path = os.path.join(os.getenv('GITHUB_WORKSPACE') or '.', 'dota2')

Converter = Callable[[dict], dict[str, str]]

class Rule(NamedTuple):
    name: str
    encoding: str
    converter: Converter

def converter_v1() -> Converter:
    return lambda data: data['lang']['Tokens']

def converter_v2(key: str) -> Converter:
    return lambda data: data[key]

rules = [
    Rule('game/dota/resource/localization/abilities_english.txt', 'utf-8', converter_v1()),
    Rule('game/dota/resource/localization/dota_english.txt', 'utf-8', converter_v1()),
    Rule('game/dota/resource/localization/teamfandom_english.txt', 'utf-8', converter_v1()),

    Rule('game/dota_addons/tutorial_basics/panorama/localization/addon_english.txt', 'utf-8-sig', converter_v2('dota')),
    Rule('game/dota_addons/npx_2019/resource/addon_english.txt', 'utf-8-sig', converter_v1()),
    Rule('game/dota_addons/hero_demo/resource/addon_english.txt', 'utf-8-sig', converter_v1()),
]

def main():
    for rule in rules:
        print(rule.name)
        with open(rule.name, 'r', encoding=rule.encoding) as input_file:
            data = vdf.load(input_file)
            data = rule.converter(data)

            result = CommentedMap({
                k: LiteralScalarString(v)
                for k, v in data.items()
                if not has_uncommon_control_char(v)
            })
            for key in itertools.islice(result, 1, None):
                result.yaml_set_comment_before_after_key(key, before='\n')
            yaml = YAML()
            output_name = os.path.join(output_path, rule.name + '.yaml')
            os.makedirs(os.path.dirname(output_name), exist_ok=True)
            with open(output_name, 'w', encoding=rule.encoding) as output_file:
                yaml.dump(result, output_file)

_CONTROL_CHARS = set(
    "\x00\x01\x02\x03\x04\x05\x06\x07"
    "\x08"
    "\x0b"
    "\x0c"
    "\x0e\x0f"
    "\x10\x11\x12\x13\x14\x15\x16\x17"
    "\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f"
    "\x7f"
)

def has_uncommon_control_char(s: str) -> bool:
    return any(c in _CONTROL_CHARS for c in s)

if __name__ == "__main__":
    main()
