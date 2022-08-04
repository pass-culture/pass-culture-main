import type { KeySelector } from 're-reselect'
import { createCachedSelector } from 're-reselect'

import { apiEntreprise } from 'apiClient/api'
import { isApiError } from 'apiClient/entreprise/helpers'
import type { IEntrepriseSirenData } from 'apiClient/entreprise/types'
import { HTTP_STATUS } from 'apiClient/helpers'
import { unhumanizeSiren } from 'core/Offerers/utils'
import { validateSiren } from 'core/Offerers/validate'

type Params = string
type IPayload = {
  values?: IEntrepriseSirenData
}
type GetSirenDataAdapter = Adapter<Params, IPayload, IPayload>

const unavailableSevicesCode = [
  HTTP_STATUS.GATEWAY_TIMEOUT,
  HTTP_STATUS.SERVICE_UNAVAILABLE,
]

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
          latitude: null,
          longitude: null,
          name: '',
          postalCode: '',
          siren: '',
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
    const values = await apiEntreprise.getSirenData(siren)

    return {
      isOk: true,
      message: `Informations récupéré avec success pour le SIREN: ${humanSiren}`,
      payload: {
        values: values,
      },
    }
  } catch (e) {
    let message = 'Une erreur est survenue'
    if (isApiError(e)) {
      message = e.content
      if (e.statusCode === HTTP_STATUS.NOT_FOUND) {
        message = "Ce SIREN n'est pas reconnu"
      } else if (unavailableSevicesCode.includes(e.statusCode)) {
        message =
          'L’Annuaire public des Entreprises est indisponible. Veuillez réessayer plus tard.'
      }
    } else if (e instanceof Error) {
      message = e.message
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
