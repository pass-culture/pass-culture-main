import { api } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import type { StructureDataBodyModel } from 'apiClient/v1'
import { unhumanizeSiret } from 'commons/core/Venue/utils'
import { memoize } from 'commons/utils/memoize'

export type GetSiretDataResponse = {
  values?: {
    address: string
    city: string
    latitude: number | null
    longitude: number | null
    name: string
    postalCode: string
    inseeCode: string | null
    siret: string
    apeCode: string
    banId: string | null
  }
}

const getSiretDataRequest = async (
  humanSiret: string
): Promise<StructureDataBodyModel> => {
  const siret = unhumanizeSiret(humanSiret || '')
  if (humanSiret === '') {
    return {
      // TODO: le bon type
      // @ts-expect-error
      values: {
        address: '',
        city: '',
        latitude: null,
        longitude: null,
        name: '',
        postalCode: '',
        inseeCode: '',
        siret: '',
        apeCode: '',
        banId: '',
      },
    }
  }
  /*const error = validateSiret(siret)
  if (error) {
    throw Error(error)
  }*/
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
