""" save sandbox """
from sandboxes import scripts

def save_sandbox(name):
    script_name = "sandbox_" + name
    sandbox_module = getattr(scripts, script_name)
    sandbox_module.save_sandbox()
