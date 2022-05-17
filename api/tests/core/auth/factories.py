import random
import string

import factory


def random_string(length, chars):
    return "".join(random.choice(chars) for _ in range(length))


def random_etag():
    part_one_prefix = "eue5R"
    part_one_content = random_string(28, string.ascii_letters + string.digits)
    part_one_suffix = "WRhZP5BU"
    part_two = random_string(28, string.ascii_letters + string.digits + "-")
    etag = f'"{part_one_prefix}_{part_one_content}-{part_one_suffix}/{part_two}"'
    return etag


class GoogleWorkspaceGroup(factory.DictFactory):
    kind = "admin#directory#group"
    id: str = factory.LazyFunction(lambda: random_string(15, string.digits + string.ascii_lowercase))
    etag: str = factory.LazyFunction(random_etag)
    name: str = factory.Sequence(lambda n: f"group-{n:04}")
    email: str = factory.LazyAttribute(lambda o: f"{o.name}@passculture.app")
    directMembersCount: str = str(random.randint(1, 150))
    description: str = factory.Faker("sentence")
    adminCreated: bool = random.choice((True, False))
    nonEditableAliases: list[str] = factory.LazyAttribute(lambda o: f"{o.name}@passculture.app.test-google-a.com")


class BackofficeGWGroup(GoogleWorkspaceGroup):
    name: str = factory.Sequence(lambda n: f"backoffice-group-{n:04}")


class GoogleWorkspaceGroupList(factory.DictFactory):
    kind = "admin#directory#groups"
    etag: str = factory.LazyFunction(random_etag)
    groups: list[GoogleWorkspaceGroup] = [GoogleWorkspaceGroup(), BackofficeGWGroup()]
