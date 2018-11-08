""" sandbox light """
from sandboxes.scripts.creators import create_scratch_offerers, \
                                       create_scratch_users

def save_sandbox():
    create_scratch_users()
    create_scratch_offerers()
