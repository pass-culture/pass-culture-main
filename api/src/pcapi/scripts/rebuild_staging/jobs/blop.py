# meta: dependencies=
import typing


def main(db: typing.Any) -> None:
    cursor = db.cursor()
    cursor.execute("SELECT NOW()")
    print(cursor.fetchall())


if not typing.TYPE_CHECKING:
    main(db)  # noqa
