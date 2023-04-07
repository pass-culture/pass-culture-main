import { apiAdresse } from 'apiClient/adresse'
import { IAutocompleteItemProps } from 'ui-kit/form/shared/AutocompleteList/type'

import { serializeAdressData } from './serializer'

export interface IAddressParams {
  search: string
  suggestionLimit?: number
}

export type GetAdressDataAdapter = Adapter<
  IAddressParams,
  IAutocompleteItemProps[],
  IAutocompleteItemProps[]
>

const FAILING_RESPONSE: AdapterFailure<IAutocompleteItemProps[]> = {
  isOk: false,
  message:
    "Une erreur est survenue lors de la récupération des suggestions d'adresse",
  payload: [],
}

const getVenueAdapter: GetAdressDataAdapter = async ({
  search,
  suggestionLimit = 10,
}: IAddressParams) => {
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
