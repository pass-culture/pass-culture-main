#!/bin/sh

curl --url 'https://backend.staging.passculture.team/offers/434266507' \
  -X 'PATCH' \
  -H 'accept: */*' \
  -H 'accept-language: fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'content-type: application/json' \
  -b 'GCP_IAP_UID=107618664809736016399; session=.eJxlj0FuxCAMRa9SsY4iDAHMrHqTyIBpqZJMFMJqNHcvo46y6dL630_vP8ScD67f4nYejQcxlyRuQoEPRDlPkUJwnLNS2hgvQ8aUgYNKGDCmKSjSKifpbQox62x6oJxFjiwhEjo5gQloHQcLDF5rS5KmEDESp6QNysTorc_RJtlPpyA5T6KL7HystPF2Xmqt8vHnh6i8k7bXynbysdEyU1rLNvNKZemFHz54LTwGaonPz51qjW0528Ej7fv_vxcVrEPnB7FQPWfayxxp6SxwXhkPXunRa0TzLiz3r7JdaRcfDUgz4SAq11ru29zai_oQH60LOe8zaMgkc5god5BULIPT2gEySPEcxLXvPe_5C-HFfb4.atjINA.x0PhrEF5T2iCV4mK3At_53Ui0m0' \
  -H 'dnt: 1' \
  -H 'origin: https://pro.staging.passculture.team' \
  -H 'priority: u=1, i' \
  -H 'referer: https://pro.staging.passculture.team/' \
  -H 'sec-ch-ua: "Not:A-Brand";v="8", "Chromium";v="156", "Google Chrome";v="156"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-site' \
  -H 'sec-gpc: 1' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/156.0.0.0 Safari/537.36' \
  --data-raw '{"url": null}'
