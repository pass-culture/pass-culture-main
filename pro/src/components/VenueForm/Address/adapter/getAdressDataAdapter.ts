import { apiAdresse } from 'apiClient/adresse'
import { IAutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'

import { serializeAdressData } from './serializer'

export type GetAdressDataAdapter = Adapter<
  string,
  IAutocompleteItemProps[],
  IAutocompleteItemProps[]
>

const FAILING_RESPONSE: AdapterFailure<IAutocompleteItemProps[]> = {
  isOk: false,
  message:
    "Une erreur est survenue lors de la récupération des suggestions d'adresse",
  payload: [],
}

const getVenueAdapter: GetAdressDataAdapter = async search => {
  try {
    const adressSuggestions = await apiAdresse.getDataFromAddress(search, 10)

    return {
      isOk: true,
      message: '',
      payload: serializeAdressData(adressSuggestions),
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getVenueAdapter
