""" save sandbox """
from models.delete import reset_all_db
from sandboxes import scripts

def save_sandbox(name):
    reset_all_db()
    script_name = "sandbox_" + name
    sandbox_module = getattr(scripts, script_name)
    sandbox_module.save_sandbox()
