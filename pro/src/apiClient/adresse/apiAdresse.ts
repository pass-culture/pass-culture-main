import { ApiError } from '@/apiClient/v1'
import { ApiRequestOptions } from '@/apiClient/v1/core/ApiRequestOptions'

import { API_ADRESSE_BASE_URL } from './constants'
import { AdresseApiJson, AdresseData, FeaturePropertyType } from './types'

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

function formatAdressApiResponse(response: AdresseApiJson): Array<AdresseData> {
  return response.features.map((f) => ({
    address: f.properties.name,
    city: f.properties.city,
    inseeCode: f.properties.citycode,
    id: f.properties.id,
    latitude: f.geometry.coordinates[1],
    longitude: f.geometry.coordinates[0],
    label: f.properties.label,
    postalCode: f.properties.postcode,
  }))
}

type AddressDataOptions = {
  limit?: number
  onlyTypes?: FeaturePropertyType[]
}
const DEFAULTS_OPTIONS: AddressDataOptions = {
  limit: 5,
  onlyTypes: ['housenumber', 'street'], // Defaults will always list streets + addresses with a number (e.g. "17 Rue de Paris …")
}

export const getDataFromAddressParts = async (
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
}

export const getDataFromAddress = async (
  address: string,
  {
    limit = DEFAULTS_OPTIONS.limit,
    onlyTypes = DEFAULTS_OPTIONS.onlyTypes,
  }: AddressDataOptions = DEFAULTS_OPTIONS
): Promise<Array<AdresseData>> => {
  const url = `${API_ADRESSE_BASE_URL}/search/?limit=${limit}&q=${address}`
  const response = await handleApiError(await fetch(url), 'GET', url)

  if (!onlyTypes) {
    return formatAdressApiResponse(response)
  }

  // Restrict results by API "types" if specifically asked
  const filteredResponse = {
    ...response,
    features: response.features.filter((r) =>
      onlyTypes.includes(r.properties.type)
    ),
  }

  return formatAdressApiResponse(filteredResponse)
}
