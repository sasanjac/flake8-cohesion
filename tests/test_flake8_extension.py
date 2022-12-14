# -*- coding: utf-8 -*-

import textwrap

from flake8_cohesion import extension
from flake8_cohesion import parser


class TestFlake8Extension:
    def test_extension_empty(self):
        python_string = textwrap.dedent("")

        ast_node = parser.get_ast_node_from_string(python_string)
        checker = extension.CohesionChecker(ast_node)
        checker._cohesion_below = 0.0
        checker._strict = False

        result = list(checker.run())

        assert result == []

    def test_extension_basic(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def a():
                x = 1
                print("a")
            def b():
                self.b = 1
                print("b")
            def c():
                print("c")
            def d():
                print("d")
        """
        )

        ast_node = parser.get_ast_node_from_string(python_string)
        checker = extension.CohesionChecker(ast_node)
        checker._cohesion_below = 0.0
        checker._strict = False

        result = list(checker.run())

        assert result == []

    def test_extension_basic_empty(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            pass
        """
        )

        ast_node = parser.get_ast_node_from_string(python_string)
        checker = extension.CohesionChecker(ast_node)
        checker._cohesion_below = 0.0
        checker._strict = False

        result = list(checker.run())

        assert result == []

    def test_extension_high(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(self):
                self.variable = 'foo'
        """
        )

        ast_node = parser.get_ast_node_from_string(python_string)
        checker = extension.CohesionChecker(ast_node)
        checker._cohesion_below = 50.0
        checker._strict = False

        result = list(checker.run())

        assert result == []

    def test_extension_low(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            variable1 = 'foo'
            variable2 = 'bar'
            variable3 = 'baz'
            def func(self):
                self.variable2 = 'baz'
            def func2(self):
                self.variable3 = 'bazz'
        """
        )

        ast_node = parser.get_ast_node_from_string(python_string)
        checker = extension.CohesionChecker(ast_node)
        checker._cohesion_below = 75.0
        checker._strict = False

        result = list(checker.run())
        expected = [
            (2, 0, extension.CohesionChecker._error_tmpl.format(50.0), extension.CohesionChecker),
        ]

        assert result == expected
