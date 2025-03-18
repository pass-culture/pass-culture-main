
import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { unhumanizeSiren } from 'commons/core/Offerers/utils'
import { validateSiren } from 'commons/core/Offerers/validate'
import { memoize } from 'commons/utils/memoize'

type GetSirenDataResponse = {
  values?: {
    address: string
    city: string
    name: string
    postalCode: string
    siren: string
    apeCode: string
  }
}

const getSirenDataRequest = async (
  humanSiren: string
): Promise<GetSirenDataResponse> => {
  const siren = unhumanizeSiren(humanSiren || '')
  if (humanSiren === '') {
    return {
      values: {
        address: '',
        city: '',
        name: '',
        postalCode: '',
        siren: '',
        apeCode: '',
      },
    }
  }
  const error = validateSiren(siren)
  if (error) {
    throw Error(error)
  }
  try {
    const response = await api.getSirenInfo(siren)
    return {
      values: {
        address: response.address.street,
        city: response.address.city,
        name: response.name,
        postalCode: response.address.postalCode,
        siren: response.siren,
        apeCode: response.ape_code,
      },
    }
  } catch (e) {
    let message = 'Une erreur est survenue'
    if (isErrorAPIError(e) && e.status === 400) {
      if (e.body.global) {
        message = e.body.global[0]
      }
    }
    throw Error(message)
  }
}

export const getSirenData = memoize(getSirenDataRequest)
