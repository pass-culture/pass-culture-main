-- gh workflow run on_dispatch_pcapi_console_job.yaml \
--   -f ENVIRONMENT_SHORT_NAME=tst \
--   -f RESOURCES="512Mi/.5" \
--   -f BRANCH_NAME=PC-42164-assigner-lactivite-principale-autre-a-tous-les-partenaires-restant \
--   -f NAMESPACE=assign_unknown_activity_to_other \
--   -f SCRIPT_ARGUMENTS="";

UPDATE venue SET activity='OTHER' WHERE activity IS NULL OR activity = 'NOT_ASSIGNED';
