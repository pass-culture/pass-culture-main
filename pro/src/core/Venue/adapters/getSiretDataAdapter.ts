import type { KeySelector } from 're-reselect'
import { createCachedSelector } from 're-reselect'

import { ENTREPRISE_STATUS_ACTIVE, apiEntreprise } from 'apiClient/api'
import type { IEntrepriseSiretData } from 'apiClient/entreprise/types'
import { isErrorAPIError, HTTP_STATUS } from 'apiClient/helpers'
import { unhumanizeSiret } from 'core/Venue/utils'
import { validateSiret } from 'core/Venue/validate'

type Params = string
type IPayload = {
  values?: IEntrepriseSiretData
}
type GetSiretDataAdapter = Adapter<Params, IPayload, IPayload>

const unavailableSevicesCode = [
  HTTP_STATUS.GATEWAY_TIMEOUT,
  HTTP_STATUS.SERVICE_UNAVAILABLE,
]

const getSiretDataAdapter: GetSiretDataAdapter = async (humanSiret: string) => {
  const siret = unhumanizeSiret(humanSiret || '')
  if (humanSiret === '') {
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
          siret: '',
          companyStatus: '',
          legalUnitStatus: '',
        },
      },
    }
  }
  const error = validateSiret(siret)
  if (error) {
    return {
      isOk: false,
      message: error,
      payload: {},
    }
  }
  try {
    const values = await apiEntreprise.getSiretData(siret)

    if (
      values.companyStatus !== ENTREPRISE_STATUS_ACTIVE ||
      values.legalUnitStatus !== ENTREPRISE_STATUS_ACTIVE
    ) {
      return {
        isOk: false,
        message: 'SIRET invalide',
        payload: {},
      }
    }

    return {
      isOk: true,
      message: `Informations récupéré avec success pour le SIRET: ${humanSiret} :`,
      payload: {
        values,
      },
    }
  } catch (e) {
    let message = 'Impossible de vérifier le SIRET saisi.'
    if (isErrorAPIError(e)) {
      message = e.body
      if (e.status === HTTP_STATUS.NOT_FOUND) {
        message = "Ce SIRET n'est pas reconnu"
      } else if (
        unavailableSevicesCode.includes(HTTP_STATUS.SERVICE_UNAVAILABLE)
      ) {
        message =
          'L’Annuaire public des Entreprises est indisponible. Veuillez réessayer plus tard.'
      }
    } else if (e instanceof Error) {
      message = e.message
    }
    return {
      isOk: false,
      message,
      payload: {},
    }
  }
}

const mapArgsToCacheKey: KeySelector<string> = (siret: string) => siret || ''
const getSiretData = createCachedSelector(
  (siret: string): string => siret,
  getSiretDataAdapter
)(mapArgsToCacheKey)

export default getSiretData
