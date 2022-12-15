# -*- coding: utf-8 -*-

from __future__ import annotations

import ast
import itertools
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterable

    NameDispatchKey = type[ast.AST]


BOUND_METHOD_ARGUMENT_NAME = "self"


def is_class_method_bound(method: ast.FunctionDef, arg_name: str = BOUND_METHOD_ARGUMENT_NAME) -> bool:
    """Return whether a class method is bound to the class."""
    if not method.args.args:
        return False

    first_arg = method.args.args[0]

    first_arg_name = get_object_name(first_arg)

    return first_arg_name == arg_name


def is_class_method_classmethod(method: ast.FunctionDef) -> bool:
    """Return whether a class method is a classmethod."""
    return class_method_has_decorator(method, "classmethod")


def is_class_method_staticmethod(method: ast.FunctionDef) -> bool:
    """Return whether a class method is a staticmethod."""
    return class_method_has_decorator(method, "staticmethod")


def is_class_method_property(method: ast.FunctionDef) -> bool:
    """Return whether a class method is a property."""
    return class_method_has_decorator(method, "property")


def is_class_method_abstractmethod(method: ast.FunctionDef) -> bool:
    """Return whether a class method is a abstractmethod."""
    return class_method_has_decorator(method, "abstractmethod")


def is_class_method_passing(method: ast.FunctionDef) -> bool:
    """Return whether a class method is a abstractmethod."""
    return any(isinstance(child, ast.Pass) for child in ast.walk(method))


def class_method_has_decorator(method: ast.FunctionDef, decorator: str) -> bool:
    """Return whether a class method has a specific decorator."""
    return decorator in [get_object_name(d) for d in method.decorator_list]


def get_class_methods(cls: ast.ClassDef) -> Iterable[ast.FunctionDef]:
    """Return methods associated with a given class."""
    return [node for node in cls.body if isinstance(node, ast.FunctionDef)]


def get_all_class_variable_names_used_in_method(method: ast.FunctionDef) -> set[str]:
    """Return the names of all instance variables associated with a given method."""
    return {get_object_name(variable) for variable in get_instance_variables(method)}


def get_all_class_variable_names(cls: ast.ClassDef, strict: bool) -> set[str]:
    """Return the names of all class and instance variables associated with a given class."""
    return {get_object_name(variable) for variable in get_all_class_variables(cls, strict)}


def get_all_class_variables(cls: ast.ClassDef, strict: bool) -> Iterable[ast.expr | ast.Attribute]:
    """Return class and instance variables associated with a given class."""
    if strict:
        items: Iterable[Iterable[ast.Attribute | ast.expr]] = [
            get_class_variables(cls),
            get_instance_variables(cls),
        ]
        return itertools.chain.from_iterable(items)

    return get_instance_variables(cls)


def get_instance_variables(
    node: ast.AST,
    bound_name_classifier: str = BOUND_METHOD_ARGUMENT_NAME,
) -> Iterable[ast.Attribute]:
    """Return instance variables used in an AST node."""
    node_attributes = [
        child
        for child in ast.walk(node)
        if isinstance(child, ast.Attribute) and get_attribute_name_id(child) == bound_name_classifier
    ]
    node_function_call_names = [get_object_name(child) for child in ast.walk(node) if isinstance(child, ast.Call)]
    return [attribute for attribute in node_attributes if get_object_name(attribute) not in node_function_call_names]


def get_attribute_name_id(attr: ast.Attribute) -> str | None:
    """Return the attribute name identifier."""
    return attr.value.id if isinstance(attr.value, ast.Name) else None


def get_class_variables(cls: ast.ClassDef) -> Iterable[ast.expr]:
    """Return class variables associated with a given class."""
    return [target for node in cls.body if isinstance(node, ast.Assign) for target in node.targets]


def get_object_name(obj: ast.AST) -> str:
    """Return the name of a given object."""
    name_dispatch: dict[NameDispatchKey, str] = {
        ast.Name: "id",
        ast.Attribute: "attr",
        ast.Call: "func",
        ast.FunctionDef: "name",
        ast.ClassDef: "name",
        ast.Subscript: "value",
        ast.arg: "arg",
    }

    while not isinstance(obj, str):
        obj = getattr(obj, name_dispatch[type(obj)])

    return obj


def get_module_classes(node: ast.AST) -> list[ast.ClassDef]:
    """Return classes associated with a given module."""
    return [child for child in ast.walk(node) if isinstance(child, ast.ClassDef)]


def get_ast_node_from_string(string: str) -> ast.AST:
    """Return an AST node from a string."""
    return ast.parse(string)
