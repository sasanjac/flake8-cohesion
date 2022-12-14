# -*- coding: utf-8 -*-

import collections
import textwrap

from flake8_cohesion import module


class TestModule:
    def assertCountEqual(self, first, second):
        """
        Test whether two sequences contain the same elements.

        This exists in Python 3, but not Python 2.
        """
        assert collections.Counter(list(first)) == collections.Counter(list(second))

    def test_module_empty(self):
        python_string = textwrap.dedent("")

        python_module = module.Module.from_string(python_string)

        result = python_module.classes

        assert result == []

    def test_module_class_empty(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            pass
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.classes
        expected = ["Cls"]

        assert result == expected

    def test_module_function_empty(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(self):
                pass
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.functions("Cls")
        expected = ["func"]

        assert result == expected

    def test_module_class_variable(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            class_variable = 'foo'
            def func(self):
                pass
        """
        )

        python_module = module.Module.from_string(python_string, strict=True)

        result = python_module.class_variables("Cls")
        expected = ["class_variable"]

        assert result == expected

    def test_module_function_variable(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def func(self):
                self.function_variable = 'foo'
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.function_variables("Cls", "func")
        expected = ["function_variable"]

        assert result == expected

    def test_module_filter_below_false(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            class_variable = 'foo'
            def func(self):
                self.instance_variable = 'bar'
        """
        )

        python_module = module.Module.from_string(python_string)
        python_module.filter_below(40)

        result = python_module.classes

        assert result == []

    def test_module_filter_below_true(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            class_variable = 'foo'
            def func(self):
                self.instance_variable = 'bar'
        """
        )

        python_module = module.Module.from_string(python_string, strict=True)
        python_module.filter_below(60)

        result = python_module.classes
        expected = ["Cls"]

        assert result == expected

    def test_module_filter_below_equal(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            class_variable = 'foo'
            def func(self):
                self.instance_variable = 'bar'
        """
        )

        python_module = module.Module.from_string(python_string, strict=True)
        python_module.filter_below(50)

        result = python_module.classes
        expected = ["Cls"]

        assert result == expected

    def test_module_filter_above_false(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            class_variable = 'foo'
            def func(self):
                self.instance_variable = 'bar'
        """
        )

        python_module = module.Module.from_string(python_string, strict=True)
        python_module.filter_above(60)

        result = python_module.classes

        assert result == []

    def test_module_filter_above_true(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            class_variable = 'foo'
            def func(self):
                self.instance_variable = 'bar'
        """
        )

        python_module = module.Module.from_string(python_string)
        python_module.filter_above(40)

        result = python_module.classes
        expected = ["Cls"]

        assert result == expected

    def test_module_filter_above_equal(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            class_variable = 'foo'
            def func(self):
                self.instance_variable = 'bar'
        """
        )

        python_module = module.Module.from_string(python_string)
        python_module.filter_above(50)

        result = python_module.classes
        expected = ["Cls"]

        assert result == expected

    def test_module_class_cohesion_percentage(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            class_variable = 'foo'
            def func(self):
                self.instance_variable = 'bar'
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.class_cohesion_percentage("Cls")
        expected = 100

        assert result == expected

    def test_module_class_cohesion_percentage_empty(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            pass
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.class_cohesion_percentage("Cls")
        expected = 100

        assert result == expected

    def test_module_class_cohesion_percentage_empty_with_init(self):
        python_string = textwrap.dedent(
            """
        class Cls:
            def __init__(self):
                self.a = 100
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.class_cohesion_percentage("Cls")
        expected = 100

        assert result == expected

    def test_module_class_cohesion_percentage_empty_abstract(self):
        python_string = textwrap.dedent(
            """
        class Cls(abc.ABC):
            @abc.abstractmethod
            def x(self) -> int:
                ...
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.class_cohesion_percentage("Cls")
        expected = 100

        assert result == expected

    def test_module_class_lineno(self):
        python_string = textwrap.dedent(
            """
        def foo():
            pass
        class Cls:
            pass
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.structure["Cls"]["lineno"]

        # Don't forget the initial newline
        expected = 4

        assert result == expected

    def test_module_class_col_offset(self):
        python_string = textwrap.dedent(
            """
        def foo():
            class Cls:
                pass
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.structure["Cls"]["col_offset"]
        expected = 4

        assert result == expected

    def test_extension_code(self):
        python_string = textwrap.dedent(
            """
        class CohesionChecker:
            name = flake8_cohesion.__name__
            version = flake8_cohesion.__version__
            off_by_default = False

            _code = "H601"
            _error_tmpl = "H601 class has low ({0:.2f}%) cohesion"

            def __init__(self, tree: ast.AST) -> None:
                self._tree = tree
                self._cohesion_below = 50.0

            @classmethod
            def add_options(cls: type[CohesionChecker], parser: manager.OptionManager) -> None:
                flag = "--cohesion-below"
                kwargs = {
                    "action": "store",
                    "type": "float",
                    "default": 50.0,
                    "help": "only show cohesion results with this percentage or lower",
                    "parse_from_config": "True",
                }
                parser.add_option(flag, **kwargs)

            @classmethod
            def parse_options(cls: type[CohesionChecker], options: Options) -> None:
                cls._cohesion_below = options.cohesion_below

            def run(self) -> Generator[tuple[int, int, str, type[CohesionChecker]], None, None]:  # noqa: TAE002
                file_module = flake8_cohesion.module.Module(self._tree)
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
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.class_cohesion_percentage("CohesionChecker")
        expected = 83.33

        assert result == expected

    def test_extension_code_without_underscore(self):
        python_string = textwrap.dedent(
            """
        class CohesionChecker:
            name = flake8_cohesion.__name__
            version = flake8_cohesion.__version__
            off_by_default = False

            _code = "H601"
            _error_tmpl = "H601 class has low ({0:.2f}%) cohesion"

            def __init__(self, tree: ast.AST) -> None:
                self._tree = tree
                self._cohesion_below = 50.0

            def run(self) -> Generator[tuple[int, int, str, type[CohesionChecker]], None, None]:  # noqa: TAE002
                file_module = flake8_cohesion.module.Module(self._tree)
                file_module.filter_below(float(self.cohesion_below))

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
        """
        )

        python_module = module.Module.from_string(python_string)

        result = python_module.class_cohesion_percentage("CohesionChecker")
        expected = 83.33

        assert result == expected

    def test_extension_code_strict(self):
        python_string = textwrap.dedent(
            """
        class CohesionChecker:
            name = flake8_cohesion.__name__
            version = flake8_cohesion.__version__
            off_by_default = False

            _code = "H601"
            _error_tmpl = "H601 class has low ({0:.2f}%) cohesion"

            def __init__(self, tree: ast.AST) -> None:
                self._tree = tree
                self._cohesion_below = 50.0

            def run(self) -> Generator[tuple[int, int, str, type[CohesionChecker]], None, None]:  # noqa: TAE002
                file_module = flake8_cohesion.module.Module(self._tree)
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
        """
        )

        python_module = module.Module.from_string(python_string, strict=True)

        result = python_module.class_cohesion_percentage("CohesionChecker")
        expected = 35.71

        assert result == expected
