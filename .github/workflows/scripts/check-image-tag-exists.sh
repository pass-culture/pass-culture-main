RESULT=`curl -s -o /dev/null --header "Authorization: Bearer $token" -w "%{http_code}" https://europe-west1-docker.pkg.dev/v2/passculture-infra-prod/pass-culture-artifact-registry/$image/manifests/$tag`
OUTPUT="tag-exists="
if [[ $RESULT == "200" ]]; then
  OUTPUT+="true"
else
  OUTPUT+="false"
  echo $RESULT
fi
echo $OUTPUT
echo $OUTPUT >> "$GITHUB_OUTPUT"
