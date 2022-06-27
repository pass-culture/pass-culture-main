#!/bin/bash

CLUSTER_NAME=$(kubectl get clustersecretstore -ojsonpath='{..items[*].spec.provider.gcpsm.auth.workloadIdentity.clusterName}')

case $CLUSTER_NAME in

  cluster-metier-ops)
    sed -i 's/$CLUSTERSECRETSTORENAME_OPS/'"$(kubectl get clustersecretstore -ojsonpath='{..items[*].metadata.name}')/g" helmfile.yaml
    ;;

  cluster-metier-ehp)
    sed -i 's/$CLUSTERSECRETSTORENAME_EHP/'"$(kubectl get clustersecretstore -ojsonpath='{..items[*].metadata.name}')/g" helmfile.yaml
    ;;

 cluster-metier-production)
    sed -i 's/$CLUSTERSECRETSTORENAME_PROD/'"$(kubectl get clustersecretstore -ojsonpath='{..items[*].metadata.name}')/g" helmfile.yaml
    ;;
esac