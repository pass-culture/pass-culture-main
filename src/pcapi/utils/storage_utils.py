import os
from pathlib import Path

import swiftclient

from pcapi import settings


# TODO: why isn't it common with pcapi.utils.objects_storage ?
def swift_con(dest_container_name):
    # TODO: This probably could be simplified. Why do we have several identifiers ?
    if dest_container_name == "storage-pc-dev":
        user = settings.SWIFT_TESTING_USER
        key = settings.SWIFT_TESTING_KEY
        tenant_name = settings.SWIFT_TESTING_TENANT_NAME
        region_name = settings.SWIFT_TESTING_REGION_NAME
    elif dest_container_name == "storage-pc-staging":
        user = settings.SWIFT_STAGING_USER
        key = settings.SWIFT_STAGING_KEY
        tenant_name = settings.SWIFT_STAGING_TENANT_NAME
        region_name = settings.SWIFT_STAGING_REGION_NAME
    else:
        print("Ce conteneur ne semble pas exister")
        return 1

    options = {"region_name": region_name}
    return swiftclient.Connection(
        user=user,
        key=key,
        authurl=settings.SWIFT_AUTH_URL,
        os_options=options,
        tenant_name=tenant_name,
        auth_version="3",
    )


def swift_con_prod():
    return swiftclient.Connection(
        user=settings.SWIFT_PROD_USER,
        key=settings.SWIFT_PROD_KEY,
        authurl=settings.SWIFT_AUTH_URL,
        os_options={"region_name": settings.SWIFT_PROD_REGION_NAME},
        tenant_name=settings.SWIFT_PROD_TENANT_NAME,
        auth_version="3",
    )


def do_local_backup_prod_container(dest_folder_name):
    if settings.SWIFT_BUCKET_NAME:
        prod_container_name = settings.SWIFT_BUCKET_NAME
        prod_conn = swift_con_prod()
    else:
        print("OVH_BUCKET_NAME does not seem to be set.")
        return 1

    download_count = 0
    object_count = 0
    print("Backup starting")

    for data in prod_conn.get_container(prod_container_name)[1]:
        obj_tuple = prod_conn.get_object(prod_container_name, data["name"])
        destination_path = (
            Path(os.path.dirname(os.path.realpath(__file__))) / ".." / "static" / dest_folder_name / data["name"]
        )
        object_count += 1
        if not destination_path.is_file() or data["bytes"] != destination_path.stat().st_size:
            with open(destination_path, "wb") as destination_file:
                destination_file.write(obj_tuple[1])
            download_count += 1
            print("Object [" + data["name"] + "] retrieved")

    print("Backup done.")
    print("%s objects listed" % object_count)
    print("%s objects downloaded." % download_count)

    return 0


def do_copy_prod_container_content_to_dest_container(dest_container_name):
    if dest_container_name not in ("storage-pc-staging", "storage-pc-dev"):
        print("Ce conteneur ne semble pas exister")
        return 1
    conn = swift_con(dest_container_name)

    if settings.SWIFT_BUCKET_NAME:
        print("OVH_BUCKET_NAME does not seem to be set.")
        return 1

    prod_container_name = settings.SWIFT_BUCKET_NAME
    prod_conn = swift_con_prod()

    for data in prod_conn.get_container(prod_container_name)[1]:
        obj_tuple = prod_conn.get_object(prod_container_name, data["name"])
        conn.put_object(dest_container_name, data["name"], contents=obj_tuple[1], content_type=data["content_type"])
        print("Object [" + data["name"] + "] copied")

    return 0


# file_name format : "thumbs/venues/SM"
def do_does_file_exist(container_name, file_name):
    if container_name in ("storage-pc-staging", "storage-pc-dev"):
        conn = swift_con(container_name)
    elif container_name == "storage-pc":
        conn = swift_con_prod()
    else:
        print("Ce conteneur ne semble pas exister")
        return 1

    for data in conn.get_container(container_name)[1]:
        if data["name"] == file_name:
            print("File exist !")
            return 0

    print("File does not exist.")
    return 0


def do_delete_file(container_name, file_name):
    if container_name in ("storage-pc-staging", "storage-pc-dev"):
        conn = swift_con(container_name)
    elif container_name == "storage-pc":
        conn = swift_con_prod()
    else:
        conn = None
        print("Ce conteneur ne semble pas exister")

    if conn:
        try:
            conn.delete_object(container_name, file_name)
            print("File deleted with success !")
        except swiftclient.ClientException as err:
            print("File deletion failed.")
            print(err)


def do_list_content(container_name):
    if container_name == "storage-pc-dev":
        conn = swift_con(container_name)
        container_url_path = settings.SWIFT_TESTING_URL_PATH
    elif container_name == "storage-pc-staging":
        conn = swift_con(container_name)
        container_url_path = settings.SWIFT_STAGING_URL_PATH
    elif container_name == "storage-pc":
        conn = swift_con_prod()
        container_url_path = settings.SWIFT_PROD_URL_PATH
    else:
        raise ValueError("Ce conteneur ne semble pas exister")

    objects_urls = []
    for data in conn.get_container(container_name)[1]:
        object_url = container_url_path + data["name"]
        objects_urls.append(object_url)

    return objects_urls
