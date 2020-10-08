from pcapi.repository.product_queries import delete_unwanted_existing_product, ProductWithBookingsException


def delete_product_from_isbn_file(file_path: str):
    print("[ISBN SCAN] START")
    book_isbns = read_isbn_from_file(file_path)
    print(f"[ISBN SCAN] Getting {len(book_isbns)} isbn to check")
    isbn_in_errors = []
    progress = 0

    for isbn in book_isbns:
        try:
            delete_unwanted_existing_product(isbn)
        except ProductWithBookingsException:
            isbn_in_errors.append(isbn)
            print(f"[ISBN SCAN] Bookings found for product with isbn : {isbn}")
        progress += 1
        step = progress / len(book_isbns) * 100
        if (progress % 1000) == 0:
            print(f"[ISBN SCAN] Progress: {str(step)}")
    print(f"[ISBN SCAN] Product with errors : {isbn_in_errors}")
    print("[ISBN SCAN] END")


def read_isbn_from_file(file_path: str) -> [str]:
    with open(file_path, mode='r', newline='\n') as file:
        book_isbns = file.read().splitlines()
    return book_isbns
