#!/bin/bash

function tag_hotfix {

    TAG_VERSION="v$TAG_NAME"
    BRANCH_NAME="hotfix-$TAG_VERSION"

    git checkout -b hotfix-$TAG_VERSION

    echo --- Change API version $TAG_VERSION ---
    cd $ROOT_PATH/api
    echo "$TAG_VERSION" > version.txt
    git add version.txt

    echo --- Change Pro version $TAG_VERSION ---
    cd $ROOT_PATH/pro
    yarn version --new-version "$TAG_NAME"
    git add package.json

    echo --- Change Adage-front version $TAG_VERSION ---
    cd $ROOT_PATH/adage-front
    yarn version --new-version "$TAG_NAME"
    git add package.json

    echo --- Tagging $TAG_VERSION ---
    cd "$ROOT_PATH"
    git commit -m "🚀 $TAG_VERSION" -n
    git tag -a "$TAG_VERSION" -m "🚀 $TAG_VERSION"
    git push origin "$BRANCH_NAME"
    git push origin "$TAG_VERSION"

    echo "New version tagged: $TAG_NAME"
}
