#/bin/bash

# This script is run by the rebuild_staging workflow, see https://github.com/pass-culture/pass-culture-deployment/blob/master/helm/db-ops/values.prod.yaml
# on a container using the `pcapi` docker image (version of the image that the production cluster uses when the step launches)
# with ENV=rebuild_staging so it uses the environnement variables in .env.rebuild_staging file.
# The pod is in full isolation, with only a connection to a database (the future staging's database), so it cannot access any infrastructure element such as Redis, cloud tasks etc

# Display commands and stop execution on error
set -ex

for table in activity user_session email; do
  psql $DATABASE_URL -c "TRUNCATE TABLE $table;"
done

psql $DATABASE_URL -c "UPDATE venue_provider SET \"isActive\" = false;"

psql $DATABASE_URL < src/pcapi/scripts/rebuild_staging/anonymize.sql

python3 src/pcapi/scripts/beneficiary/import_test_users.py --default --update

flask sandbox --name beneficiaries --clean false
