""" sandbox webapp """
from sandboxes.scripts.creators.grid import save_grid_sandbox
from sandboxes.scripts.creators.scratch import save_scratch_sandbox

def save_sandbox():
    save_scratch_sandbox()
    #save_grid_sandbox()
