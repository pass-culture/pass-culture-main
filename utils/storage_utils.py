import os
from pathlib import Path, PurePath
import swiftclient


def swift_con_ante_prod():
    user = os.environ.get('OVH_USER')
    key = os.environ.get('OVH_PASSWORD')
    tenant_name = os.environ.get('OVH_TENANT_NAME')

    auth_url = 'https://auth.cloud.ovh.net/v2.0/'
    options = {
        'region_name': 'GRA3'
    }
    auth_version = '2'
    return swiftclient.Connection(user=user,
                                  key=key,
                                  authurl=auth_url,
                                  os_options=options,
                                  tenant_name=tenant_name,
                                  auth_version=auth_version)


def swift_con_prod():
    user = os.environ.get('OVH_USER_PROD')
    key = os.environ.get('OVH_PASSWORD_PROD')
    tenant_name = os.environ.get('OVH_TENANT_NAME_PROD')

    auth_url = 'https://auth.cloud.ovh.net/v2.0/'
    options = {
        'region_name': 'GRA3'
    }
    auth_version = '2'
    return swiftclient.Connection(user=user,
                                  key=key,
                                  authurl=auth_url,
                                  os_options=options,
                                  tenant_name=tenant_name,
                                  auth_version=auth_version)


def do_copy_src_container_content_to_dest_container(src_container_name, dest_container_name):
    conn = swift_con_ante_prod()

    for data in conn.get_container(src_container_name)[1]:
        # IF DESTINATION CONTAINER DOES NOT CONTAIN OBJECT NAME, WE COPY IT
        try:
            print(data['name'])
            conn.get_object(dest_container_name, data['name'])
        except swiftclient.exceptions.ClientException:
            obj_tuple = conn.get_object(src_container_name, data['name'])
            conn.put_object(dest_container_name,
                            data['name'],
                            contents=obj_tuple[1],
                            content_type=data['content_type'])
            print("Object [" + data['name'] + "] copied")

    return 0


# file_name format : "thumbs/venues/SM"
def do_does_file_exist(container_name, file_name):
    # container_name = os.environ.get('OVH_BUCKET_NAME')
    conn = swift_con_ante_prod()

    for data in conn.get_container(container_name)[1]:
        if data['name'] == file_name:
            print("File exist !")
            obj_tuple = conn.get_object(container_name, file_name)
            destination_file_name = file_name + "_copy"
            conn.put_object(container_name,
                            destination_file_name,
                            contents=obj_tuple[1],
                            content_type=data['content_type'])
            print("File copied.")
            return 0

    print('File does not exist.')
    return 0


def do_delete_file(container_name, file_name):
    conn = swift_con_ante_prod()
    conn.delete_object(container_name, file_name)


def do_list_content(container_name):
    # container_name = os.environ.get('OVH_BUCKET_NAME')
    conn = swift_con_ante_prod()

    for data in conn.get_container(container_name)[1]:
        print('{0}\t{1}\t{2}'.format(data['name'], data['bytes'], data['last_modified']))

    return 0
