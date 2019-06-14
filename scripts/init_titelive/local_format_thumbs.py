import glob
from io import BufferedReader
from typing import List

import os

from models import Product
from utils.human_ids import humanize


# TODO: /media/daniel.baudry/Dell Portable Hard Drive/MediaLivre/thumbs/products/

def format_all_thumbs(source_directory: str, destination_directory: str):
    sub_directories = get_all_sub_directories(source_directory)
    for directory in sub_directories:
        files_in_directory = get_files_from_folder(directory)
        for filename in files_in_directory:
            book_ean13 = extract_book_ean13(filename)
            existing_product = Product.query \
                .filter(Product.idAtProviders == book_ean13) \
                .first()
            if not existing_product:
                continue

            product_humanized_id = humanize(existing_product.id)
            thumb_content = open(filename, 'rb')

            write_file_to_directory(destination_directory,
                                    product_humanized_id,
                                    thumb_content)
            thumb_content.close()


def extract_book_ean13(filename):
    return filename.split('/')[-1].split('_')[0]


def get_all_sub_directories(main_directory):
    return sorted(glob.glob("%s/%s" % (main_directory, '*/')))


def get_files_from_folder(directory_identifier: str) -> List[str]:
    return glob.glob("%s/%s" % (directory_identifier, '*_75.jpg'))


def write_file_to_directory(directory_identifier: str, filename: str, file_content: BufferedReader):
    absolute_path_filename = "%s/%s" % (directory_identifier, filename)
    file_index = 1
    destination_path_filename = absolute_path_filename

    while os.path.exists(destination_path_filename):
        destination_path_filename = absolute_path_filename \
                                 + '_' \
                                 + str(file_index)
        file_index = file_index + 1

    print("Saving file %s" % destination_path_filename)
    file = open(destination_path_filename, "wb")
    file.write(file_content.read())
    file.close()
