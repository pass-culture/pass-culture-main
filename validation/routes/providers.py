from models import ApiErrors

def check_provider_name(provider_name):
    if provider_name is Not in ["", ""]:
        api_errors = ApiErrors()
        api_errors.add_error('eventOccurrenceId', 'l’offreur associé à cet évènement est inconnu')
        raise api_errors
