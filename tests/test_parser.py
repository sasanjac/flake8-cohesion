# -*- coding: utf-8 -*-

import ast
import textwrap

import pytest

from flake8_cohesion import parser


class TestParser:
    def test_valid_syntax(self):
        python_string = textwrap.dedent(
            """
        a = 5
        """
        )

        result = parser.get_ast_node_from_string(python_string)
        expected = ast.Module

        assert isinstance(result, expected)

    def test_invalid_syntax(self):
        python_string = textwrap.dedent(
            """
        a )= 5
        """
        )

        with pytest.raises(SyntaxError):
            parser.get_ast_node_from_string(python_string)

    def test_get_module_classes_empty(self):
        python_string = textwrap.dedent(
            """
        def func(arg1):
            print("Hi")
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        result = parser.get_module_classes(node)

        assert result == []

    def test_get_module_classes_single(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        classes = parser.get_module_classes(node)
        result = [cls.name for cls in classes]
        expected = ["Cls"]

        assert set(result) == set(expected)

    def test_get_module_classes_multiple(self):
        python_string = textwrap.dedent(
            """
        class Cls1:
            pass
        class Cls2:
            pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        classes = parser.get_module_classes(node)
        result = [cls.name for cls in classes]
        expected = ["Cls1", "Cls2"]

        assert set(result) == set(expected)

    def test_get_class_methods_empty(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        result = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]

        assert result == []

    def test_get_class_methods_single(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func1(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [method.name for method in methods]
        expected = ["func1"]

        assert set(result) == set(expected)

    def test_get_class_methods_multiple(self):
        python_string = textwrap.dedent(
            """
        class Cls1:
            def func1(self, arg1):
                pass
            def func2(self, arg1):
                pass
        class Cls2:
            def func3(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [method.name for method in methods]
        expected = ["func1", "func2", "func3"]

        assert set(result) == set(expected)

    def test_get_class_methods_avoid_nested(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func1(self, arg1):
                def func2(arg2):
                    pass
                print("Hi")
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [method.name for method in methods]
        expected = ["func1"]

        assert set(result) == set(expected)

    def test_get_class_methods_avoid_lambda(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func1(self, arg1):
                func2 = lambda arg: arg
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [method.name for method in methods]
        expected = ["func1"]

        assert set(result) == set(expected)

    def test_bound_method_is_bound(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_bound(method)
        ]
        result = [method.name for method in methods]
        expected = ["func"]

        assert set(result) == set(expected)

    def test_is_class_method_staticmethod_is_staticmethod(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            @staticmethod
            def func(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_staticmethod(method)
        ]
        result = [method.name for method in methods]
        expected = ["func"]

        assert set(result) == set(expected)

    def test_is_class_method_staticmethod_not_decorated(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_staticmethod(method)
        ]
        result = [method.name for method in methods]

        assert result == []

    def test_is_class_method_classmethod_other_decorator(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            @other_decorator
            def func(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_classmethod(method)
        ]
        result = [method.name for method in methods]

        assert result == []

    def test_is_class_method_classmethod_other_decorator_with_arguments(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            @other_decorator("argument")
            def func(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_classmethod(method)
        ]
        result = [method.name for method in methods]

        assert result == []

    def test_is_class_method_classmethod_is_classmethod(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            @classmethod
            def func(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_classmethod(method)
        ]
        result = [method.name for method in methods]
        expected = ["func"]

        assert set(result) == set(expected)

    def test_is_class_method_classmethod_not_decorated(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_classmethod(method)
        ]
        result = [method.name for method in methods]

        assert result == []

    def test_is_class_method_staticmethod_other_decorator(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            @other_decorator
            def func(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_staticmethod(method)
        ]
        result = [method.name for method in methods]

        assert result == []

    def test_is_class_method_staticmethod_other_decorator_with_arguments(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            @other_decorator("argument")
            def func(self, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_staticmethod(method)
        ]
        result = [method.name for method in methods]

        assert result == []

    def test_bound_method_non_default_name(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(this, arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_bound(method, arg_name="this")
        ]
        result = [method.name for method in methods]
        expected = ["func"]

        assert set(result) == set(expected)

    def test_bound_method_static(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            @staticmethod
            def func(arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_bound(method)
        ]
        result = [method.name for method in methods]

        assert result == []

    def test_bound_method_static_no_arguments(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            @staticmethod
            def func():
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_bound(method)
        ]
        result = [method.name for method in methods]

        assert result == []

    def test_bound_method_unbound(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(arg1):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        methods = [
            method
            for cls in parser.get_module_classes(node)
            for method in parser.get_class_methods(cls)
            if parser.is_class_method_bound(method)
        ]
        result = [method.name for method in methods]

        assert result == []

    def test_get_instance_variables_from_class_single(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def __init__(self):
                self.attr = 5
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        instance_variables = parser.get_instance_variables(node)
        result = [instance_variable.attr for instance_variable in instance_variables]
        expected = ["attr"]

        assert set(result) == set(expected)

    def test_get_instance_variables_from_class_multiple(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def __init__(self):
                self.attr1 = 5
                self.attr2 = 6
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        instance_variables = parser.get_instance_variables(node)
        result = [instance_variable.attr for instance_variable in instance_variables]
        expected = ["attr1", "attr2"]

        assert set(result) == set(expected)

    def test_get_instance_variables_from_class_multiple_same_line(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def __init__(self):
                self.attr1 = self.attr2 = 5
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        instance_variables = parser.get_instance_variables(node)
        result = [instance_variable.attr for instance_variable in instance_variables]
        expected = ["attr1", "attr2"]

        assert set(result) == set(expected)

    def test_get_instance_variables_from_class_avoid_class_variable(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            attr = 5
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        instance_variables = parser.get_instance_variables(node)
        result = [instance_variable.attr for instance_variable in instance_variables]

        assert result == []

    def test_get_class_variables_from_class_single(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            attr = 5
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        classes = parser.get_module_classes(node)
        class_variables = [class_variable for cls in classes for class_variable in parser.get_class_variables(cls)]
        result = [class_variable.id for class_variable in class_variables]
        expected = ["attr"]

        assert set(result) == set(expected)

    def test_get_class_variables_from_class_multiple_targets(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            attr1 = attr2 = 5
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        classes = parser.get_module_classes(node)
        class_variables = [class_variable for cls in classes for class_variable in parser.get_class_variables(cls)]
        result = [class_variable.id for class_variable in class_variables]
        expected = ["attr1", "attr2"]

        assert set(result) == set(expected)

    def test_get_class_variables_from_class_avoid_instance_variable(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def __init__(self):
                self.attr = 5
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        classes = parser.get_module_classes(node)
        class_variables = [class_variable for cls in classes for class_variable in parser.get_class_variables(cls)]
        result = [class_variable.id for class_variable in class_variables]

        assert result == []

    def test_get_all_class_variable_names_both_types(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            attr1 = 5
            def __init__(self):
                self.attr2 = 6
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        classes = parser.get_module_classes(node)
        result = [name for cls in classes for name in parser.get_all_class_variable_names(cls, strict=True)]
        expected = ["attr1", "attr2"]

        assert set(result) == set(expected)

    def test_get_all_class_variable_names_just_instance(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def __init__(self):
                self.attr = 6
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        classes = parser.get_module_classes(node)
        result = [name for cls in classes for name in parser.get_all_class_variable_names(cls, strict=True)]
        expected = ["attr"]

        assert set(result) == set(expected)

    def test_get_all_class_variable_names_just_class(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            attr = 6
            def __init__(self):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        classes = parser.get_module_classes(node)
        result = [name for cls in classes for name in parser.get_all_class_variable_names(cls, strict=True)]
        expected = ["attr"]

        assert set(result) == set(expected)

    def test_get_all_class_variable_names_ensure_no_method_names(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            attr = 6
            def func(self):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        classes = parser.get_module_classes(node)
        result = [name for cls in classes for name in parser.get_all_class_variable_names(cls, strict=True)]
        # Ensure 'func' isn't in the list of included names
        expected = ["attr"]

        assert set(result) == set(expected)

    def test_get_all_class_variable_names_used_in_method(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            attr1 = 5
            def func(self):
                self.attr2 = 6
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        class_methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [
            name for method in class_methods for name in parser.get_all_class_variable_names_used_in_method(method)
        ]
        expected = ["attr2"]

        assert set(result) == set(expected)

    def test_ensure_method_call_not_considered_instance_variable(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func1(self):
                pass
            def func2(self):
                self.attr1 = 5
                self.func1()
                self.attr2 = self.attr1
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        class_methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [
            name for method in class_methods for name in parser.get_all_class_variable_names_used_in_method(method)
        ]
        # Ensure 'func1' isn't in the list of included names
        expected = ["attr1", "attr2"]

        assert set(result) == set(expected)

    def test_ensure_decorator_not_considered_instance_variable(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            @library.decorator
            def func(self):
                self.attr1 = 5
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        class_methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [
            name for method in class_methods for name in parser.get_all_class_variable_names_used_in_method(method)
        ]
        # Ensure 'decorator' isn't in the list of included names
        expected = ["attr1"]

        assert set(result) == set(expected)

    def test_ensure_unbound_attribute_not_considered_instance_variable(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(self):
                self.attr1 = 5
                otherclass.attr2 = 6
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        class_methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [
            name for method in class_methods for name in parser.get_all_class_variable_names_used_in_method(method)
        ]
        # Ensure 'attr2' isn't in the list of included names
        expected = ["attr1"]

        assert set(result) == set(expected)

    def test_only_passing_ok(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(self):
                self.attr1 = 4
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        class_methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [parser.is_class_method_only_passing(method) for method in class_methods]
        # Ensure 'func' is passing
        expected = [False]

        assert set(result) == set(expected)

    def test_only_passing(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(self):
                pass
        """
        )

        node = parser.get_ast_node_from_string(python_string)
        class_methods = [method for cls in parser.get_module_classes(node) for method in parser.get_class_methods(cls)]
        result = [parser.is_class_method_only_passing(method) for method in class_methods]
        # Ensure 'func' is passing
        expected = [True]

        assert set(result) == set(expected)
