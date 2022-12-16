# Cohesion

flake8-cohesion is a flake8 extension for measuring Python class cohesion.

> In computer programming, cohesion refers to the degree to which the elements
> of a module belong together. Thus, cohesion measures the strength of
> relationship between pieces of functionality within a given module. For
> example, in highly cohesive systems functionality is strongly related.
> - [Wikipedia](https://en.wikipedia.org/wiki/Cohesion_(computer_science))

> When cohesion is high, it means that the methods and variables of the class
> are co-dependent and hang together as a logical whole.
> - Clean Code pg. 140

Some of the advantages of high cohesion, also by Wikipedia:

* Reduced module complexity (they are simpler, having fewer operations).
* Increased system maintainability, because logical changes in the domain
  affect fewer modules, and because changes in one module require fewer
  changes in other modules.
* Increased module reusability, because application developers will find
  the component they need more easily among the cohesive set of operations
  provided by the module.

## Differences to `cohesion`

`flake8-cohesion` is a fork of `cohesion`. However, because it seems abandoned, I decided to change the calculations to match a more regular workflow when coding in `python`:

- The following method types are not considered when calculating class cohesion:
  - `abstractmethods`
  - `classmethods`
  - `staticmethods`
  - `properties`

- Methods containing only a `pass` statement are not considered.

- Class variables that are defined in class definition are not considered when they are not accessed in any considered method.

## Installation

Install with `pip`:
```sh
pip install flake8-cohesion
```

requires `python >= 3.9`

## Usage

Check with `flake8`:

```sh
python -m flake8
```

## Violations

`flake8-cohesion` currently reports only one violation:

| code | description                                             |
| ---- | ------------------------------------------------------- |
| H601 | calculated class cohesion falls below defined threshold |

## Options

`flake8-cohesion` supports two options:

| option                | default value | description                                                    |
| --------------------- | ------------- | -------------------------------------------------------------- |
| `cohesion-percentage` | `50.0`        | upper percentage threshold below which a violation is reported |
| `cohesion-strict`     | `false`       | includes variables of class defintion in cohesion calculation  |

example flake8 configuration file:
```toml
[flake8]
cohesion-percentage = 70.0
cohesion-strict = true
```