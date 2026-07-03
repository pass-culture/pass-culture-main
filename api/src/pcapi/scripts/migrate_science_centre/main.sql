--- gh workflow run on_dispatch_pcapi_console_job.yaml \
---   -f ENVIRONMENT_SHORT_NAME=tst \
---   -f RESOURCES="512Mi/.5" \
---   -f BRANCH_NAME=PC-42163-rattapage-activite-principale-et-domaines-partenaires-ancienne-typologie-autre-2 \
---   -f NAMESPACE=migrate_science_centre \
---   -f SCRIPT_ARGUMENTS="";

UPDATE venue SET activity='SCIENTIFIC_CULTURE' WHERE activity='SCIENCE_CENTRE';