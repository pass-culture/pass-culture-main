import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'

import { API_ADRESSE_BASE_URL } from './constants'
import { IAdresseApiJson, IAdresseData } from './types'

const handleApiError = async (
  response: Response,
  method: ApiRequestOptions['method'],
  url: string
): Promise<IAdresseApiJson> => {
  if (!response.ok) {
    throw new ApiError(
      { method, url },
      response,
      `Échec de la requête ${response.url}, code: ${response.status}`
    )
  }
  return (await response.json()) as IAdresseApiJson
}

export default {
  getDataFromAddress: async (
    address: string,
    limit = 5
  ): Promise<Array<IAdresseData>> => {
    const url = `${API_ADRESSE_BASE_URL}/search/?limit=${limit}&q=${address}`
    const response = await handleApiError(await fetch(url), 'GET', url)

    return response.features.map(f => ({
      address: f.properties.name,
      city: f.properties.city,
      id: f.properties.id,
      latitude: f.geometry.coordinates[1],
      longitude: f.geometry.coordinates[0],
      label: f.properties.label,
      postalCode: f.properties.postCode,
    }))
  },
}
