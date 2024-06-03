import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'

import { API_ADRESSE_BASE_URL } from './constants'
import { AdresseApiJson, AdresseData } from './types'

const handleApiError = async (
  response: Response,
  method: ApiRequestOptions['method'],
  url: string
): Promise<AdresseApiJson> => {
  if (!response.ok) {
    throw new ApiError(
      { method, url },
      response,
      `Échec de la requête ${response.url}, code: ${response.status}`
    )
  }
  return (await response.json()) as AdresseApiJson
}

function formatAdressApiResponse(response: AdresseApiJson) {
  return response.features.map((f) => ({
    address: f.properties.name,
    city: f.properties.city,
    id: f.properties.id,
    latitude: f.geometry.coordinates[1],
    longitude: f.geometry.coordinates[0],
    label: f.properties.label,
    postalCode: f.properties.postcode,
  }))
}

export const apiAdresse = {
  getDataFromAddressParts: async (
    street: string,
    city: string,
    postalCode: string,
    limit = 5
  ): Promise<Array<AdresseData>> => {
    const url = `${API_ADRESSE_BASE_URL}/search/?limit=${limit}&q=${street} ${city} ${postalCode}`
    const response = await handleApiError(await fetch(url), 'GET', url)

    if (response.features.length > 0) {
      return formatAdressApiResponse(response)
    } else {
      const url = `${API_ADRESSE_BASE_URL}/search/?q=${city}&postcode=${postalCode}&type=municipality&autocomplete=0&limit=1`
      const response = await handleApiError(await fetch(url), 'GET', url)
      return formatAdressApiResponse(response)
    }
  },
  getDataFromAddress: async (
    adress: string,
    limit = 5
  ): Promise<Array<AdresseData>> => {
    const url = `${API_ADRESSE_BASE_URL}/search/?limit=${limit}&q=${adress}`
    const response = await handleApiError(await fetch(url), 'GET', url)

    return formatAdressApiResponse(response)
  },
}
