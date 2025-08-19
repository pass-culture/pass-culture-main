import { api } from '@/apiClient/api'
import { isErrorAPIError } from '@/apiClient/helpers'
import { StructureDataBodyModel } from '@/apiClient/v1/models/StructureDataBodyModel'
import { unhumanizeSiret } from '@/commons/core/Venue/utils'
import { memoize } from '@/commons/utils/memoize'

import { validateSiret } from './validate'

const getSiretDataRequest = async (
  humanSiret: string
): Promise<StructureDataBodyModel> => {
  const siret = unhumanizeSiret(humanSiret || '')
  if (humanSiret === '') {
    return {
      address: null,
      apeCode: null,
      isDiffusible: false,
      name: null,
      siren: null,
      siret: '',
    }
  }
  const error = validateSiret(siret)
  if (error) {
    throw Error(error)
  }
  try {
    const response = await api.getStructureData(siret)
    return response
  } catch (e) {
    let message = 'Impossible de vérifier le SIRET saisi.'
    if (isErrorAPIError(e) && e.status === 400) {
      message = e.body
      /* istanbul ignore next: DEBT, TO FIX */
      if (e.body.global) {
        message = e.body.global[0]
      }
    }
    throw Error(message)
  }
}

export const getSiretData = memoize(getSiretDataRequest)
