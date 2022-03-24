import createCachedSelector from 're-reselect'
import type { KeySelector } from 're-reselect'

import { apiEntreprise } from 'api/api'
import type { IEntrepriseSiretData } from 'api/entreprise/types'
import { unhumanizeSiret } from 'core/Venue/utils'
import { validateSiret } from 'core/Venue/validate'

type Params = string
type IPayload = {
  values?: IEntrepriseSiretData
}
type GetSiretDataAdapter = Adapter<Params, IPayload, IPayload>

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
    if ('error' in values) {
      return {
        isOk: false,
        message: values.error,
        payload: {},
      }
    }

    return {
      isOk: true,
      message: `Siret ${humanSiret} :`,
      payload: {
        values: values,
      },
    }
  } catch {
    return {
      isOk: false,
      message: 'Impossible de vérifier le SIRET saisi.',
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
