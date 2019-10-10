import local_providers


class Provider:
    @staticmethod
    def get_provider_by_name(name: str):
        return getattr(local_providers, name)
