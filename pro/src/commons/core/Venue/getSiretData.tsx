import { getDataFromAddressParts } from '@/apiClient//adresse/apiAdresse'
import { api } from '@/apiClient//api'
import { isErrorAPIError } from '@/apiClient//helpers'
import { unhumanizeSiret } from '@/commons/core/Venue/utils'
import { validateSiret } from '@/commons/core/Venue/validate'
import { memoize } from '@/commons/utils/memoize'

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
        inseeCode: '',
        siret: '',
        apeCode: '',
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
    const addressData = await getDataFromAddressParts(
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
        address: addressData[0].address,
        city: addressData[0].city,
        latitude: latitude,
        longitude: longitude,
        name: response.name,
        postalCode: addressData[0].postalCode,
        inseeCode: addressData[0].inseeCode,
        siret: response.siret,
        apeCode: response.ape_code,
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
