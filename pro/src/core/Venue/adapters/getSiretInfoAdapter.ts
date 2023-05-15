import { api } from 'apiClient/api'
import { GET_DATA_ERROR_MESSAGE } from 'core/shared'
import { unhumanizeSiret } from 'core/Venue/utils'

type Params = string
type IPayload = {
  values?: {
    address: string
    city: string
    name: string
    postalCode: string
    siret: string
    apeCode: string
  }
}

const FAILING_RESPONSE: AdapterFailure<IPayload> = {
  isOk: false,
  message: GET_DATA_ERROR_MESSAGE,
  payload: {},
}

type GetSiretInfoAdapter = Adapter<Params, IPayload, IPayload>

const getSiretInfoAdapter: GetSiretInfoAdapter = async (humanSiret: string) => {
  const siret = unhumanizeSiret(humanSiret)

  try {
    const response = await api.getSiretInfo(siret)

    if (!response.active) {
      return {
        isOk: false,
        message: 'SIRET invalide',
        payload: {},
      }
    }

    return {
      isOk: true,
      message: '',
      payload: {
        values: {
          address: response.address.street,
          city: response.address.city,
          name: response.name,
          postalCode: response.address.postalCode,
          siret: response.siret,
          apeCode: response.ape_code,
        },
      },
    }
  } catch (error) {
    return FAILING_RESPONSE
  }
}

export default getSiretInfoAdapter
