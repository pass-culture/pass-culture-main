import { api } from 'apiClient/api'
import { SirenInfo } from 'apiClient/v1'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'

type Params = {
  siren: string
}

type GetSirenInfoAdapter = Adapter<Params, SirenInfo, null>

const getSirenInfoAdapter: GetSirenInfoAdapter = async ({ siren }: Params) => {
  try {
    const response = await api.getSirenInfo(siren)
    return {
      isOk: true,
      message: '',
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

export default getSirenInfoAdapter
