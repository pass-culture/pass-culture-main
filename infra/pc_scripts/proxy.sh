#!/bin/bash

PROXY_CERT_DEST="$ROOT_PATH/api/cacert.pem"

function _is_proxy_cert_copied {
    [ -f $PROXY_CERT_DEST ]
}

function _is_proxy_running {
    ps aux | grep -v grep | grep -i "proxy" | grep "/Library/SystemExtensions/" &>/dev/null
}
