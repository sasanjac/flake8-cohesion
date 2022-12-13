# -*- coding: utf-8 -*-

from __future__ import annotations

import operator
from typing import TYPE_CHECKING

from flake8_cohesion import parser

if TYPE_CHECKING:
    import ast
    from collections.abc import Callable
    from typing import TypedDict

    class FunctionDict(TypedDict):
        variables: list[str]
        bounded: bool
        staticmethod: bool  # noqa: A003,VNE003
        classmethod: bool  # noqa: A003,VNE003

    class StructureDict(TypedDict):
        cohesion: float | None
        lineno: int
        col_offset: int
        variables: list[str]
        functions: dict[str, FunctionDict]


class Module:
    def __init__(self, module_ast_node: ast.AST) -> None:
        self.structure = self._create_structure(module_ast_node)

        for class_name in self.structure.keys():
            self.class_cohesion_percentage(class_name)

    def classes(self) -> list[str]:
        return list(self.structure.keys())

    def functions(self, class_name: str) -> list[str]:
        return list(self.structure[class_name]["functions"].keys())

    def class_variables(self, class_name: str) -> list[str]:
        return self.structure[class_name]["variables"]

    def function_variables(self, class_name: str, function_name: str) -> list[str]:
        return self.structure[class_name]["functions"][function_name]["variables"]

    @classmethod
    def from_string(cls, python_string: str) -> Module:
        module_ast_node = parser.get_ast_node_from_string(python_string)

        return cls(module_ast_node)

    def filter_below(self, percentage: float) -> None:
        def predicate(class_name: str) -> bool:
            class_percentage = self.class_cohesion_percentage(class_name)
            return operator.le(class_percentage, percentage)

        self._filter(predicate)

    def filter_above(self, percentage: float) -> None:
        def predicate(class_name: str) -> bool:
            class_percentage = self.class_cohesion_percentage(class_name)
            return operator.ge(class_percentage, percentage)

        self._filter(predicate)

    def _filter(self, predicate: Callable[[str], bool] = lambda class_name: True) -> None:
        self.structure = {
            class_name: class_structure
            for class_name, class_structure in self.structure.items()
            if predicate(class_name)
        }

    def class_cohesion_percentage(self, class_name: str) -> float:
        cohesion = self.structure[class_name]["cohesion"]
        if cohesion is not None:
            return cohesion

        functions = {k: v for k, v in self.structure[class_name]["functions"].items() if len(v["variables"]) > 0}

        total_function_variable_count = sum(
            len(function_structure["variables"]) for function_structure in functions.values()
        )

        total_class_variable_count = len(self.structure[class_name]["variables"]) * len(functions)

        if total_class_variable_count != 0.0:
            class_percentage = round((total_function_variable_count / total_class_variable_count) * 100, 2)
        else:
            class_percentage = 0.0

        self.structure[class_name]["cohesion"] = class_percentage

        return class_percentage

    @staticmethod
    def _create_structure(file_ast_node: ast.AST) -> dict[str, StructureDict]:
        module_classes = parser.get_module_classes(file_ast_node)

        result = {}

        for module_class in module_classes:
            class_name = parser.get_object_name(module_class)

            class_variable_names = list(parser.get_all_class_variable_names(module_class))

            class_methods = parser.get_class_methods(module_class)

            class_method_name_to_method = {method.name: method for method in class_methods}

            class_method_name_to_variable_names = {
                method_name: list(parser.get_all_class_variable_names_used_in_method(method))
                for method_name, method in class_method_name_to_method.items()
            }

            class_method_name_to_boundedness = {
                method_name: parser.is_class_method_bound(method)
                for method_name, method in class_method_name_to_method.items()
            }

            class_method_name_to_staticmethodness = {
                method_name: parser.is_class_method_staticmethod(method)
                for method_name, method in class_method_name_to_method.items()
            }

            class_method_name_to_classmethodness = {
                method_name: parser.is_class_method_classmethod(method)
                for method_name, method in class_method_name_to_method.items()
            }

            result[class_name]["cohesion"] = None
            result[class_name]["lineno"] = module_class.lineno
            result[class_name]["col_offset"] = module_class.col_offset
            result[class_name]["variables"] = class_variable_names
            result[class_name]["functions"] = {
                method_name: {
                    "variables": class_method_name_to_variable_names[method_name],
                    "bounded": class_method_name_to_boundedness[method_name],
                    "staticmethod": class_method_name_to_staticmethodness[method_name],
                    "classmethod": class_method_name_to_classmethodness[method_name],
                }
                for method_name in class_method_name_to_method.keys()
            }

        return result
