import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { SelectOption } from 'custom_types/form'
import { api } from 'apiClient/api'

type GetCulturalPartnersAdapter = Adapter<void, SelectOption[], SelectOption[]>

const getCulturalPartnersAdapter: GetCulturalPartnersAdapter = async () => {
  try {
    const response = await api.getEducationalPartners()
    return {
      isOk: true,
      message: '',
      payload: response.partners.map(partner => ({
        value: partner.id.toString(),
        label: partner.libelle,
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

export default getCulturalPartnersAdapter
