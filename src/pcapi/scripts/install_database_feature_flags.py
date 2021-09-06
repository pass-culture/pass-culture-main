from pcapi.models.feature import install_feature_flags


def install_database_feature_flags(app):
    with app.app_context():
        install_feature_flags()


def main():
    from pcapi.flask_app import app

    install_database_feature_flags(app)


if __name__ == "__main__":
    main()
