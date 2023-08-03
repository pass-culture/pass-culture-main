#/bin/bash

# This script is run by the rebuild_staging workflow, see https://github.com/pass-culture/pass-culture-deployment/blob/master/helm/db-ops/values.ep.yaml
# on a container using the `pcapi` docker image (version of the image that the staging cluster uses when the step launches).

# Display commands and stop execution on error
set -ex

flask import_test_users --default --update
flask sandbox --name beneficiaries --clean false

flask add_permissions_to_staging_specific_roles
