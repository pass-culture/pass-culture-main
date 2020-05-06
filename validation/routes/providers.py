from models import ApiErrors

def check_provider_name(provider_name):
    if provider_name not in ["offerer", "venue"]:
        api_errors = ApiErrors()
        api_errors.add_error('unknown provider', 'unknown provider. Choose beetween offerer or venue')
        raise api_errors
