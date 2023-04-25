from pcapi.routes.serialization.users import ProUserCreationBodyModel


def create_filled_pro_user_creation_form() -> ProUserCreationBodyModel:
    return ProUserCreationBodyModel(  # type: ignore [call-arg]
        address="REDACTED",
        city="AMSTERDAM",
        email="REDACTED@gmail.com",  # type: ignore [arg-type]
        firstName="REDACTED",
        lastName="REDACTED",
        name="REDACTED",
        password="REDACTED",
        phoneNumber="REDACTED",
        postalCode="REDACTED",
        siren="REDACTED",
        contactOk=True,
    )


if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        from pcapi.core.users import api as users_api

        print("Script starting")
        stranger_pro_user = create_filled_pro_user_creation_form()
        users_api.create_pro_user_and_offerer(stranger_pro_user)
        print("Pro user and offerer created")
