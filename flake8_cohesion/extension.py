# -*- coding: utf-8 -*-

from __future__ import annotations

from typing import TYPE_CHECKING

import flake8_cohesion

if TYPE_CHECKING:
    import ast
    from collections.abc import Generator
    from typing import Protocol

    from flake8.options import manager

    class Options(Protocol):
        cohesion_below: float
        cohesion_strict: bool
        ...


class CohesionChecker:
    name = flake8_cohesion.__name__
    version = flake8_cohesion.__version__
    off_by_default = False

    _code = "H601"
    _error_tmpl = "H601 class has low ({0:.2f}%) cohesion"

    def __init__(self, tree: ast.AST) -> None:
        self._tree = tree

    @classmethod
    def add_options(cls: type[CohesionChecker], parser: manager.OptionManager) -> None:
        flag = "--cohesion-below"
        kwargs = {
            "action": "store",
            "type": float,
            "default": 50.0,
            "help": "only show cohesion results with this percentage or lower",
            "parse_from_config": "True",
        }
        parser.add_option(flag, **kwargs)
        flag = "--cohesion-strict"
        kwargs = {
            "action": "store_true",
            "help": "count variables from class definition",
            "parse_from_config": "True",
        }
        parser.add_option(flag, **kwargs)

    @classmethod
    def parse_options(cls: type[CohesionChecker], options: Options) -> None:
        cls._cohesion_below = options.cohesion_below
        cls._strict = options.cohesion_strict

    def run(self) -> Generator[tuple[int, int, str, type[CohesionChecker]], None, None]:  # noqa: TAE002
        file_module = flake8_cohesion.module.Module(self._tree, self._strict)
        file_module.filter_below(float(self._cohesion_below))

        for class_name in file_module.classes:
            cohesion_percentage = file_module.class_cohesion_percentage(class_name)
            yield (  # noqa: TMN002
                file_module.structure[class_name]["lineno"],
                file_module.structure[class_name]["col_offset"],
                self._error_tmpl.format(cohesion_percentage),
                type(self),
            )

    @property
    def cohesion_below(self) -> float:
        return self._cohesion_below
