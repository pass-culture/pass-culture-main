from repository.product_queries import delete_unwanted_existing_product, ProductWithBookingsException


def delete_product_from_isbn_file(file_path: str):
    print("[ISBN SCAN] START")
    book_isbns = read_isbn_from_file(file_path)
    print("[ISBN SCAN] Getting %s isbn to check" % len(book_isbns))

    for isbn in book_isbns:
        try:
            print("[ISBN SCAN] Analyzing ISBN %s" % isbn)
            delete_unwanted_existing_product(isbn)
        except ProductWithBookingsException:
            print("[ISBN SCAN] Bookings found for product with isbn : %s" % isbn)
    print("[ISBN SCAN] END")


def read_isbn_from_file(file_path: str) -> [str]:
    with open(file_path, mode='r', newline='\n') as file:
        book_isbns = file.read().splitlines()
    return book_isbns
