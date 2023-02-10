from pcapi.sandboxes.scripts.creators.e2e import save_e2e_sandbox


def save_sandbox() -> None:
    save_e2e_sandbox()


if __name__ == "__main__":
    from pcapi.flask_app import app; app.app_context().push()
    from pcapi.sandboxes.scripts.save_sandbox import save_sandbox as global_save_sandbox
    global_save_sandbox("e2e", True)
