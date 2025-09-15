#!/bin/bash

# This script is run by the rebuild_staging workflow, see https://github.com/pass-culture/infrastructure/blob/main/.github/workflows/rebuild-staging.yml
# on a container using the `pcapi` docker image (version of the image that the staging cluster uses when the step launches).

# Display commands and stop execution on error
set -ex

export IS_REBUILD_STAGING=1

flask import_test_users --default --update
flask sandbox --name beneficiaries accessibility_offers --clean false

flask add_permissions_to_staging_specific_roles

flask disable_external_bookings
