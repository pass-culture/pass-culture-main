import createCachedSelector from 're-reselect'
import type { KeySelector } from 're-reselect'

import { apiEntreprise } from 'api/api'
import type { IEntrepriseData } from 'api/entreprise/types'
import { unhumanizeSiret } from 'core/Venue/utils'
import { validateSiret } from 'core/Venue/validate'

type Params = string
type IPayload = {
  values?: IEntrepriseData
}
type GetEntrepriseDataFromSiretAdapter = Adapter<Params, IPayload, IPayload>

const getEntrepriseDataAdapter: GetEntrepriseDataFromSiretAdapter = async (
  humanSiret: string
) => {
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
    const values = await apiEntreprise.getEntrepriseDataFromSiret(siret)
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
export const getEntrepriseData = createCachedSelector(
  (siret: string): string => siret,
  getEntrepriseDataAdapter
)(mapArgsToCacheKey)
