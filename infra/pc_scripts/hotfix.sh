#!/bin/bash

function tag_hotfix {

    TAG_VERSION="v$TAG_NAME"
    BRANCH_NAME="hotfix-$TAG_VERSION"

    echo --- Tag API $TAG_VERSION ---
    cd $ROOT_PATH/api
    git checkout -b hotfix-$TAG_VERSION
    echo "$TAG_VERSION" > version.txt
    git add version.txt
    git commit -m "🚀 $TAG_VERSION"
    git tag "$TAG_VERSION"
    git push origin "$BRANCH_NAME"
    git push origin "$TAG_VERSION"

    echo --- Tag WebApp $TAG_VERSION ---
    cd $ROOT_PATH/webapp
    git checkout -b hotfix-$TAG_VERSION
    yarn version --new-version "$TAG_NAME"
    git tag "$TAG_VERSION"
    git push origin "$BRANCH_NAME"
    git push origin "$TAG_VERSION"

    echo --- Tag Pro $TAG_VERSION ---
    cd $ROOT_PATH/pro
    git checkout -b hotfix-$TAG_VERSION
    yarn version --new-version "$TAG_NAME"
    git tag "$TAG_VERSION"
    git push origin "$BRANCH_NAME"
    git push origin "$TAG_VERSION"

    echo --- Tag Main $TAG_VERSION ---
    cd "$ROOT_PATH"
    git checkout -b hotfix-$TAG_VERSION
    git add api doc pro webapp
    git commit -m "🚀 $TAG_VERSION"
    git tag "$TAG_VERSION"
    git push origin "$BRANCH_NAME"
    git push origin "$TAG_VERSION"

    echo "New version tagged: $TAG_NAME"
}
