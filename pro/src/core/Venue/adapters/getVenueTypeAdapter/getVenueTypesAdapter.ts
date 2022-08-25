import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

export type GetVenueTypesAdapter = Adapter<void, SelectOption[], SelectOption[]>

const FAILING_RESPONSE: AdapterFailure<SelectOption[]> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getVenueTypesAdapter: GetVenueTypesAdapter = async () => {
  try {
    const venueTypes = await api.getVenueTypes()

    return {
      isOk: true,
      message: '',
      payload: venueTypes.map(type => ({
        value: type.id,
        label: type.label,
      })),
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getVenueTypesAdapter
