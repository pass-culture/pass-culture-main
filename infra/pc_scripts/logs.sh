#!/env/bash

function logs {
    if [[ "$ENV" == "development" ]]; then
        export RUN="docker compose -f \"$ROOT_PATH\"/docker-compose-backend.yml logs"
    else
      echo "Use GCP console or kubectl CLI to access k8s logs"
      exit
    fi
}
