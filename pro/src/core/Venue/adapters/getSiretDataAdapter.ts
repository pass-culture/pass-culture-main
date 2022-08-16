import type { KeySelector } from 're-reselect'
import { createCachedSelector } from 're-reselect'

import { api, apiAdresse } from 'apiClient/api'
import { isErrorAPIError } from 'apiClient/helpers'
import { unhumanizeSiret } from 'core/Venue/utils'
import { validateSiret } from 'core/Venue/validate'

type Params = string
type IPayload = {
  values?: {
    address: string
    city: string
    latitude: number | null
    longitude: number | null
    name: string
    postalCode: string
    siret: string
  }
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
    const response = await api.getSiretInfo(siret)
    if (!response.active) {
      return {
        isOk: false,
        message: 'SIRET invalide',
        payload: {},
      }
    }
    const { street, city, postalCode } = response.address
    const address = `${street} ${city} ${postalCode}`
    const addressData = await apiAdresse.getDataFromAddress(address, 1)
    if (addressData.length == 0) {
      return {
        isOk: false,
        message: 'Adresse introuvable',
        payload: {},
      }
    }
    const latitude = addressData[0].latitude
    const longitude = addressData[0].longitude
    return {
      isOk: true,
      message: `Informations récupéré avec success pour le SIRET: ${humanSiret} :`,
      payload: {
        values: {
          address: response.address.street,
          city: response.address.city,
          latitude: latitude,
          longitude: longitude,
          name: response.name,
          postalCode: response.address.postalCode,
          siret: response.siret,
        },
      },
    }
  } catch (e) {
    let message = 'Impossible de vérifier le SIRET saisi.'
    if (isErrorAPIError(e) && e.status == 400) {
      message = e.body
      if (e.body.global) {
        message = e.body.global[0]
      }
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
