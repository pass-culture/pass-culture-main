import memoize from 'lodash.memoize'

import { api, apiAdresse } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { unhumanizeSiret } from 'core/Venue/utils'
import { validateSiret } from 'core/Venue/validate'

export type GetSiretDataResponse = {
  values?: {
    address: string
    city: string
    latitude: number | null
    longitude: number | null
    name: string
    postalCode: string
    siret: string
    apeCode: string
    legalCategoryCode: string
    banId: string | null
  }
}

const getSiretDataRequest = async (
  humanSiret: string
): Promise<GetSiretDataResponse> => {
  const siret = unhumanizeSiret(humanSiret || '')
  if (humanSiret === '') {
    return {
      values: {
        address: '',
        city: '',
        latitude: null,
        longitude: null,
        name: '',
        postalCode: '',
        siret: '',
        apeCode: '',
        legalCategoryCode: '',
        banId: '',
      },
    }
  }
  const error = validateSiret(siret)
  if (error) {
    throw Error(error)
  }
  try {
    const response = await api.getSiretInfo(siret)
    if (!response.active) {
      throw Error('SIRET invalide')
    }
    const { street, city, postalCode } = response.address
    const addressData = await apiAdresse.getDataFromAddressParts(
      street,
      city,
      postalCode,
      1
    )
    if (addressData.length === 0) {
      throw Error('Adresse introuvable')
    }
    const latitude = addressData[0].latitude
    const longitude = addressData[0].longitude
    return {
      values: {
        address: response.address.street,
        city: response.address.city,
        latitude: latitude,
        longitude: longitude,
        name: response.name,
        postalCode: response.address.postalCode,
        siret: response.siret,
        apeCode: response.ape_code,
        legalCategoryCode: response.legal_category_code,
        banId: addressData[0].id,
      },
    }
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
