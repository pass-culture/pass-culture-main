""" sandbox webapp """
from sandboxes.scripts.creators.handmade import save_handmade_sandbox
from sandboxes.scripts.creators.industrial import save_industrial_sandbox

def save_sandbox():
    save_handmade_sandbox()
    save_industrial_sandbox()
