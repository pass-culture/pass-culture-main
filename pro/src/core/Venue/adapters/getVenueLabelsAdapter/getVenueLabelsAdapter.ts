import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

export type GetVenueLabelsAdapter = Adapter<
  void,
  SelectOption[],
  SelectOption[]
>

const FAILING_RESPONSE: AdapterFailure<SelectOption[]> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: [],
}

const getVenueLabelsAdapter: GetVenueLabelsAdapter = async () => {
  try {
    const venueLabels = await api.fetchVenueLabels()

    return {
      isOk: true,
      message: '',
      payload: venueLabels.map(type => ({
        value: type.id,
        label: type.label,
      })),
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getVenueLabelsAdapter
