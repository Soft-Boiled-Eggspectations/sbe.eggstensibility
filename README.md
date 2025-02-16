<p align="center"><img src="./.img/icon.svg" width=30% /></p>

# `sbe.eggstensibility` - A very simple python extension framework

`sbe.eggstensibility` is a simple library to make tools extendable by users
by providing a simple mechanism to load extensions. Extensions can define their
dependencies allowing dependencies in between them.

The load-mechanism is customizable, but provides sensible defaults to get you
up and running quickly. See below for the installation and usage.

## Motivation

I often find myself working on tooling that I want to be extensible without providing
end-users direct access to source code. `sbe.eggstensibility` provides the behavior
to easily add extensions to such tooling which users can use to further customize
behavior of a tool without having to provide direct access to the source code or
access to the delivery of the tool.

Python itself provides multiple alternatives to this, which you should definitely
consider before using this library.

* Direct access to the source code: Full customizability and an easier set up, but does not insulate your own code-base from users and makes distribution more difficult
* Extensions through entrypoints: Customizability and separation, but requires access to the distribution in order for the user extensions to be properly loaded

## Usage

`sbe.eggstensibility` can be installed in any python `>=3.10` project. It only relies
on [the `networkx` package](https://networkx.org/documentation/stable/tutorial.html) to
ensure the extensions are loaded in the correct order.

The implementing application is responsibility for defining where to load extensions
from and how to resolve them. `sbe.eggstensibility` provides a set of sensible but
opinionated defaults but allows the implementing application to provide its own as
well.

### Installation

`sbe.eggstensibility` is delivered as a regular wheel and can be installed with `pip`
or any package management tool of your choosing.

```powershell
wget https://github.com/Soft-Boiled-Eggspectations/sbe.eggstensibility/releases/download/v1.0.0/sbe.eggstensibility-1.0.0-py3-none-any.whl
pip install sbe.eggstensibility-1.0.0-py3-none-any.whl
```

For the time being, it is only
available through the Python packages associated with this repository.
Once the API is considered stable, it will be released on pip directly.

### Implementation

Using `sbe.eggstensibility` requires two steps:

* Defining the load-mechanism within some entry-point of your application
* Defining the extensions

The load-mechanism can be created with the `Builder` object, obtained with the
`construct_builder` method which allows you to build up your loader.
The `Loader` provides a `load_extension_descriptions` which will yield an
ordered list of extension descriptions which can subsequently be used by
the tool to load the extensions.

```python
paths = ...

extension_descriptions = (
    sbe.eggstensibility.construct_builder()
    .add_module_resolver(...)
    .add_description_resolver(...)
    .configure_identifier_resolver(...)
    .configure_dependency_resolver(...)
    .add_harvest_path(*paths)
    .build()
    .load_extension_descriptions()
)
```

By not defining how extensions should be loaded and only generating the order
(and availability of the python modules), `sbe.eggstensibility` does not try
to impede on design decisions of the tool itself.

How the actual extension descriptions are defined can be customized, but
`sbe.eggstensibility` does provide some sensible but opinionated defaults
described below.

#### Default Implementation

`sbe.eggstensibility` provides the following default implementations:

* description
* module resolver
* description resolver
* identifier resolver
* dependency resolver

These are located in `sbe.eggstensibility.defaults` and are described below.

For a full example, [see the default implementation acceptance test](/test/acceptance/default/__init__.py)

##### Description and ExtensionID

An extension description describes a single extension and should be independent of the
extension it describes. The default `Description` requires the following:

* A human-readable name
* The extensions this extension relies on (as a list of `ExtensionID`)
* A constructor function to create a new instance of the extension it describes

The `ExtensionID` is defined as a simple hexadecimal value of a UID and is
generated automatically when a new `Description` is created.

By keeping the description independent of the extension it describes, extensions
descriptions to refer to one another, thus re-using their `ExtensionID` values.

##### Module resolver

As seen in the example above, the `Builder` is provided with a set of paths. From
these paths we need to determine which actual python modules we need to load.
The module resolver is responsible for this.

There are two default module resolvers:

* `FileModuleResolver`: if a path to a (python) file is provided this path will be
    loaded as a module
* `DirectoryModuleResolver`: if a path to a python directory is provided, the module
    with a default specified name is loaded as a module

These resolvers will produce a set of paths to python modules which will be used
to resolve the descriptions from.

##### Description Resolver

The description resolver is responsible for retrieving an extension description
from a given module. The default `DescriptionResolver` assumes that the description
is always stored in a specific variable. The name of this variable can be specified
upon construction of the `DescriptionResolver`.

##### Identifier Resolver and Dependency Resolver

The identifier and dependency resolver are responsible for retrieving the identifier
and dependencies of a given description. The default `ResolveIdentifier` and
`ResolveDependency` will return the corresponding properties of the default
`Description`.

#### Custom Implementation

For each of the default implementations, a custom implementation can be provided as
well to further customize `sbe.eggstensibility`. These custom implementations need
to implement the corresponding protocols defined in `sbe.eggstensibility.protocols`.

For a full example, [see the custom implementation acceptance test](/test/acceptance/custom/__init__.py)

### Defining the extension paths

`sbe.eggstensibility` does not enforce how the initial module paths should be found.
This is left up to the tool to define. Some common approaches are:

* A pre-defined directory within the installation directory
* A PATH-like environment variable
* A configuration file specifying the relevant directories
