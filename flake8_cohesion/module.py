# -*- coding: utf-8 -*-

from __future__ import annotations

import operator
from typing import TYPE_CHECKING

from flake8_cohesion import parser

if TYPE_CHECKING:
    import ast
    from collections.abc import Callable
    from collections.abc import Sequence
    from typing import TypedDict

    class FunctionDict(TypedDict):
        variables: Sequence[str]
        bounded: bool
        staticmethod: bool  # noqa: A003,VNE003
        classmethod: bool  # noqa: A003,VNE003
        property: bool  # noqa: A003,VNE003
        abstractmethod: bool
        passing: bool

    class StructureDict(TypedDict):
        cohesion: float | None
        lineno: int
        col_offset: int
        variables: Sequence[str]
        functions: dict[str, FunctionDict]


class Module:
    def __init__(self, module_ast_node: ast.AST, strict: bool = False) -> None:
        self.structure = self._create_structure(module_ast_node, strict)

        for class_name in self.structure.keys():
            self.class_cohesion_percentage(class_name)

    @property
    def classes(self) -> Sequence[str]:
        return list(self.structure.keys())

    def functions(self, class_name: str) -> Sequence[str]:
        return list(self.structure[class_name]["functions"].keys())

    def class_variables(self, class_name: str) -> Sequence[str]:
        return self.structure[class_name]["variables"]

    def function_variables(self, class_name: str, function_name: str) -> Sequence[str]:
        return self.structure[class_name]["functions"][function_name]["variables"]

    @classmethod
    def from_string(cls, python_string: str, strict: bool = False) -> Module:
        module_ast_node = parser.get_ast_node_from_string(python_string)

        return cls(module_ast_node, strict)

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
        class_percentage = self._calculate_class_percentage(class_name)

        self.structure[class_name]["cohesion"] = class_percentage

        return class_percentage

    def _calculate_class_percentage(self, class_name: str) -> float:
        cohesion = self.structure[class_name]["cohesion"]
        if cohesion is not None:
            return cohesion

        relevant_functions = {
            k: v
            for k, v in self.structure[class_name]["functions"].items()
            if (v["staticmethod"] is False)
            and (v["classmethod"] is False)
            and (v["property"] is False)
            and (v["abstractmethod"] is False)
            and (v["passing"] is False)
        }

        if len(relevant_functions) == 0:
            return 100.0

        total_function_variable_count = sum(
            len({e.strip("_") for e in function_structure["variables"]})
            for function_structure in relevant_functions.values()
        )

        total_class_variable_count = len({e.strip("_") for e in self.structure[class_name]["variables"]}) * len(
            relevant_functions
        )

        return round((total_function_variable_count / total_class_variable_count) * 100, 2)

    @staticmethod
    def _create_structure(file_ast_node: ast.AST, strict: bool) -> dict[str, StructureDict]:
        module_classes = parser.get_module_classes(file_ast_node)

        result: dict[str, StructureDict] = {}

        for module_class in module_classes:
            class_name = parser.get_object_name(module_class)

            class_variable_names = list(parser.get_all_class_variable_names(module_class, strict))

            class_methods = parser.get_class_methods(module_class)

            class_method_name_to_method = {str(method.name): method for method in class_methods}

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

            class_method_name_to_propertyness = {
                method_name: parser.is_class_method_property(method)
                for method_name, method in class_method_name_to_method.items()
            }

            class_method_name_to_abstractmethodness = {
                method_name: parser.is_class_method_abstractmethod(method)
                for method_name, method in class_method_name_to_method.items()
            }

            class_method_name_to_only_passing = {
                method_name: parser.is_class_method_only_passing(method)
                for method_name, method in class_method_name_to_method.items()
            }

            cohesion = None
            lineno = module_class.lineno
            col_offset = module_class.col_offset
            variables = class_variable_names
            functions: dict[str, FunctionDict] = {
                method_name: {
                    "variables": class_method_name_to_variable_names[method_name],
                    "bounded": class_method_name_to_boundedness[method_name],
                    "staticmethod": class_method_name_to_staticmethodness[method_name],
                    "classmethod": class_method_name_to_classmethodness[method_name],
                    "property": class_method_name_to_propertyness[method_name],
                    "abstractmethod": class_method_name_to_abstractmethodness[method_name],
                    "passing": class_method_name_to_only_passing[method_name],
                }
                for method_name in class_method_name_to_method.keys()
            }
            result[class_name] = {
                "cohesion": cohesion,
                "lineno": lineno,
                "col_offset": col_offset,
                "variables": variables,
                "functions": functions,
            }

        return result
