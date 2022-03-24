import createCachedSelector from 're-reselect'
import type { KeySelector } from 're-reselect'

import { apiEntreprise } from 'api/api'
import { isApiError, HTTP_STATUS } from 'api/helpers'
import type { IEntrepriseSirenData } from 'api/entreprise/types'
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
    const values = (await apiEntreprise.getSirenData(
      siren
    )) as IEntrepriseSirenData

    return {
      isOk: true,
      message: `Data for Siren: ${humanSiren}`,
      payload: {
        values: values,
      },
    }
  } catch (e) {
    const defaultMessage = 'Une erreur est survenue'
    let message = defaultMessage
    if (isApiError(e)) {
      message = e.content
      if (e.statusCode === HTTP_STATUS.NOT_FOUND) {
        message = "Ce SIREN n'est pas reconnu"
      } else if (
        unavailableSevicesCode.includes(HTTP_STATUS.SERVICE_UNAVAILABLE)
      ) {
        message =
          'L’Annuaire public des Entreprises est indisponible. Veuillez réessayer plus tard.'
      }
    }
    return {
      isOk: false,
      message: message || defaultMessage,
      payload: {
        error: message || defaultMessage,
      },
    }
  }
}

const mapArgsToCacheKey: KeySelector<string> = (siren: string) => siren || ''
const getSirenData = createCachedSelector(
  (siren: string): string => siren,
  getSirenDataAdapter
)(mapArgsToCacheKey)

export default getSirenData
