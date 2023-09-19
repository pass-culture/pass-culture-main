# Public API: tests

The main ideas are:

1. one source file -> one test file;
2. remove all (almost) http related stuff from testing methods;
3. use generic helpers classes to avoid duplicated tests between
classes, like unauthorized or not found errors...

To do so, test classes should define:

1. the `controller`, a reference to the route function;
2. the `status_code`, only for error test classes;
3. some `path_kwargs` as a dict, mainly for error tests;
4. the expected `num_queries`, if needed.

The most basic test must therefore only define a `controller`.

Then, the test class must inherit (at least) from helpers.PublicApiBaseTest.

Finally, the test methods should call `self.assert_valid_response()`
context manager whose goal is to send the request, check the http
status and JSON response and yield the JSON as a dict.

For more details, please check its docstring and code.

## Helpers

`PublicApiBaseTest` is the main helper class, but there are others, like
`UnauthorizedBaseTest` which inherit from it and only defines
the expected `status_code`.

There is also the `UnauthenticatedMixin` mixin which defines a single
method: `test_unauthenticated` (checks status code).

And a couple more.
