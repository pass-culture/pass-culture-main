import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { sortByLabel } from 'utils/strings'

type GetVenueTypesAdapter = Adapter<void, SelectOption[], SelectOption[]>

const FAILING_RESPONSE: AdapterFailure<SelectOption[]> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getVenueTypesAdapter: GetVenueTypesAdapter = async () => {
  try {
    const venueTypes = await api.getVenueTypes()
    const wordToNotSort = venueTypes.filter(type => type.label === 'Autre')
    const sortedTypes = sortByLabel(
      venueTypes.filter(type => wordToNotSort.indexOf(type) === -1)
    ).concat(wordToNotSort)

    return {
      isOk: true,
      message: '',
      payload: sortedTypes.map(type => ({
        value: type.id,
        label: type.label,
      })),
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getVenueTypesAdapter
