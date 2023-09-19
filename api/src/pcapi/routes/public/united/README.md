# Public API

This module contains routes and utils related to the public API. For
now, it is nothing more than a simple POC. All the core logic are
copy/pasted from their original modules (routes/public/collective/...
and routes/public/individual_...).

* endpoints: all endpoints. Collective resources modules starts with
`collective_`, individual ones with `individual_`, shared resources do
not need any prefixes.
* blueprint: simple module that sets up the Flask blueprint (keep in
mind that this API is part of a larger Flask app).
* errors: legacy module to be removed or used differently. Only contains
one error class.
* serialization: empty... for now.
* utils: where the fun starts. Mainly contains the generic decorator
used by united routes.

This README is not meant to stay, or at least not in this format. Its
main goal is to keep a track of what has been done and what could be the
next steps.

The redoc can be found (locally) there: http://localhost:5001/oops/redoc
(yes, oops, why not?).

## Goal

This is only a first step. A place to discuss.

The idead behind is that there is no reason to keep a wall between
collective and individual resources, there should not be two distinct
public APIs. We should group routes by resources to avoid, for example,
routes for venues inside a the collective API and the same ones inside
the individual one. This could also help a lot to keep a consistent API:
share error formatting, error messages, descriptions, etc.

## Main changes

1. group routes by resources (create/edit collective offers inside
endpoints/collective_offers.py, create/edit individual offers inside
endpoints/individual_offers.py, create/edit venues inside
endpoints/venues.py...)
2. no more a-thousand-screen-long-decorators (I might be slightly
exagerating), just one simple and generic decorator.

Each import function has (or should have!) a clear (I hope) docstring.

### Tests

Well... this might be the most debatable update.
The main idea is avoid things like:

1. I edited a route... where is the associated tests? Inside
tests/[...]/post_my_resource.py? or tests/[...]/post_my_resources_with_inconsistent_naming.py?
And if I edit another function inside the same source module...where
should I go? test/[...]/get_well_this_should_be_my_resource.py?
2. oh, this test breaks... the route is POST /collective/something-complicated...
where is the source file?
3. I don't (really) care if it's a 401 or 403 error, or if it's a PATCH or a
POST method... I want the check function's outputs and side effects.

Regarding 1., well... this is madness. Please stop this :)
As for 2., we can live with it but... having the route function would
make things nicer. And regarding 3., some might disagree, some not.

A more detailed explanation can be found inside tests/routes/public/united/README.md.

## Next steps

1. Change what seems to complicated from this POC, or missing. And
agree on some v0.1.
2. How should we handle versioning?
3. Clean collective and invidual code that need it.
