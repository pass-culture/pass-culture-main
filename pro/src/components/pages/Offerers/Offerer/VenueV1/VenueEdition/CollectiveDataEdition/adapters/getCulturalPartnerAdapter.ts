import { AdageCulturalPartnerResponseModel } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { api } from 'apiClient/api'

type GetCulturalPartnerAdapter = Adapter<
  string,
  AdageCulturalPartnerResponseModel,
  null
>

const getCulturalPartnerAdapter: GetCulturalPartnerAdapter = async siret => {
  try {
    const response = await api.getEducationalPartner(siret)
    return {
      isOk: true,
      message: null,
      payload: response,
    }
  } catch (e) {
    return {
      isOk: false,
      message: GET_DATA_ERROR_MESSAGE,
      payload: null,
    }
  }
}

export default getCulturalPartnerAdapter
