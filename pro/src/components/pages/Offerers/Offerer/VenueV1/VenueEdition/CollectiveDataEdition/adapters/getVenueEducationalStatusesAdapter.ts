import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'

type GetCulturelPartnersAdapter = Adapter<void, SelectOption[], SelectOption[]>

const getCulturelPartnersAdapter: GetCulturelPartnersAdapter = async () => {
  try {
    const response = await api.getVenuesEducationalStatuses()
    return {
      isOk: true,
      message: '',
      payload: response.statuses.map(status => ({
        value: status.id,
        label: status.name,
      })),
    }
  } catch (e) {
    return {
      isOk: false,
      message: GET_DATA_ERROR_MESSAGE,
      payload: [],
    }
  }
}

export default getCulturelPartnersAdapter
