# Cohesion

flake8-ohesion is a flake8 extension for measuring Python class cohesion.

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
