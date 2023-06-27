import type { KeySelector } from 're-reselect'
import { createCachedSelector } from 're-reselect'

import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { unhumanizeSiren } from 'core/Offerers/utils'
import { validateSiren } from 'core/Offerers/validate'

type Params = string
type Payload = {
  values?: {
    address: string
    city: string
    name: string
    postalCode: string
    siren: string
    apeCode: string
  }
}

type GetSirenDataAdapter = Adapter<Params, Payload, Payload>

const getSirenDataAdapter: GetSirenDataAdapter = async (humanSiren: string) => {
  const siren = unhumanizeSiren(humanSiren || '')
  if (humanSiren === '') {
    return {
      isOk: true,
      message: '',
      payload: {
        values: {
          address: '',
          city: '',
          name: '',
          postalCode: '',
          siren: '',
          apeCode: '',
        },
      },
    }
  }
  const error = validateSiren(siren)
  if (error) {
    return {
      isOk: false,
      message: error,
      payload: {},
    }
  }
  try {
    const response = await api.getSirenInfo(siren)
    return {
      isOk: true,
      message: `Informations récupéré avec success pour le SIREN: ${humanSiren}`,
      payload: {
        values: {
          address: response.address.street,
          city: response.address.city,
          name: response.name,
          postalCode: response.address.postalCode,
          siren: response.siren,
          apeCode: response.ape_code,
        },
      },
    }
  } catch (e) {
    let message = 'Une erreur est survenue'
    if (isErrorAPIError(e) && e.status == 400) {
      if (e.body.global) {
        message = e.body.global[0]
      }
    }
    return {
      isOk: false,
      message: message,
      payload: {},
    }
  }
}

const mapArgsToCacheKey: KeySelector<string> = (siren: string) => siren || ''
const getSirenData = createCachedSelector(
  (siren: string): string => siren,
  getSirenDataAdapter
)(mapArgsToCacheKey)

export default getSirenData
