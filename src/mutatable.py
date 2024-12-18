import random
import re
from typing import Dict

from mutatable_strings import *


class Mutatable:
    def __init__(self, type: str, value: str):
        self.type = type
        self.value = value
        self.sub_mutatables: Dict[str, Mutatable] = {}
        self.detect_required_sub_mutatables()

    def detect_required_sub_mutatables(self) -> None:
        """
        Detect placeholders like [$INTx], [$ACTIONx], etc., in the value
        and map them dynamically using the 'mapping' list.
        """
        matches = re.findall(r'\[\$(\w+)\]', self.value)

        for match in matches:
            if match not in self.sub_mutatables:  # Ensure no duplicate processing
                for placeholder, mutatable_type, options in mapping:
                    if match.startswith(placeholder):
                        self.sub_mutatables[match] = Mutatable(mutatable_type, random.choice(options))
                        break
                else:
                    raise RuntimeError(f"Unknown placeholder type: {match}")

    def mutate(self):
        """
        Mutate the sub-mutatables by randomly replacing or mutating them.
        """
        for key, sub_mutatable in list(self.sub_mutatables.items()):
            if random.random() < 0.2:  # 20% chance to replace the sub-mutable
                if key.startswith("INT"):
                    self.sub_mutatables[key] = Mutatable("int", random.choice(ints))
                elif key.startswith("ACTION"):
                    self.sub_mutatables[key] = Mutatable("action", random.choice(actions))
                elif key.startswith("DIR"):
                    self.sub_mutatables[key] = Mutatable("direction", random.choice(directions))
                elif key.startswith("IF"):
                    self.sub_mutatables[key] = Mutatable("if", random.choice(ifs))
            else:
                sub_mutatable.mutate()  # Recursively mutate existing sub-mutatables

    def __str__(self):
        result = self.value
        placeholders = re.findall(r'\[\$(\w+)\]', self.value)

        # Replace all placeholders using the sub-mutatables map
        for placeholder in placeholders:
            if placeholder in self.sub_mutatables:
                result = result.replace(f"[${placeholder}]", str(self.sub_mutatables[placeholder]), 1)
            else:
                raise RuntimeError(f"Missing sub-mutable for placeholder: {placeholder}")

        return result