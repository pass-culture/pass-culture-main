import { apiAdresse } from 'apiClient/adresse'
import { AutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'

import { serializeAdressData } from './serializer'

interface AddressParams {
  search: string
  suggestionLimit?: number
}

type GetAdressDataAdapter = Adapter<
  AddressParams,
  AutocompleteItemProps[],
  AutocompleteItemProps[]
>

const FAILING_RESPONSE: AdapterFailure<AutocompleteItemProps[]> = {
  isOk: false,
  message:
    "Une erreur est survenue lors de la récupération des suggestions d'adresse",
  payload: [],
}

const getVenueAdapter: GetAdressDataAdapter = async ({
  search,
  suggestionLimit = 10,
}: AddressParams) => {
  try {
    const adressSuggestions = await apiAdresse.getDataFromAddress(
      search,
      suggestionLimit
    )

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
