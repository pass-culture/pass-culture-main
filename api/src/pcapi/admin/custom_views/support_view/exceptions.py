class DuplicateIdPieceNumber(Exception):
    def __init__(self, id_piece_number: str, duplicate_user_id: int) -> None:
        self.id_piece_number = id_piece_number
        self.duplicate_user_id = duplicate_user_id
        super().__init__()


class DuplicateIneHash(Exception):
    def __init__(self, ine_hash: str, duplicate_user_id: int) -> None:
        self.ine_hash = ine_hash
        self.duplicate_user_id = duplicate_user_id
        super().__init__()
