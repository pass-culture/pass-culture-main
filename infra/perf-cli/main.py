import click


from api import api
from native import native
from signin import signin


@click.group()
def pcapi():
    """CLI for PCAPI"""
    pass


if __name__ == '__main__':
    pcapi.add_command(api)
    pcapi.add_command(native)
    pcapi.add_command(signin)
    pcapi()

