import type {
  ListOffersVenueResponseModelV2,
  LocationResponseModel,
  LocationResponseModelV2,
} from '@/apiClient/v1'

export const getLocationResponseModel = (
  addressResponse: Partial<LocationResponseModel> = {}
): LocationResponseModel => {
  return {
    banId: 'ban',
    city: 'city',
    id: 1,
    inseeCode: 'inseeCode',
    isVenueLocation: true,
    isManualEdition: false,
    label: 'label',
    latitude: 48.866667,
    longitude: 2.333333,
    postalCode: '75008',
    street: 'ma super rue',
    departmentCode: '75',
    ...addressResponse,
  }
}

export const getLocationResponseModelV2 = (
  addressResponse: Partial<LocationResponseModelV2> = {}
): LocationResponseModelV2 => {
  return {
    banId: 'ban',
    city: 'city',
    id: 1,
    inseeCode: 'inseeCode',
    isVenueLocation: true,
    isManualEdition: false,
    label: 'label',
    latitude: 48.866667,
    longitude: 2.333333,
    postalCode: '75008',
    street: 'ma super rue',
    departmentCode: '33',
    ...addressResponse,
  }
}

export const listOffersVenueV2Factory = (
  customListOffersVenue: Partial<ListOffersVenueResponseModelV2> = {}
): ListOffersVenueResponseModelV2 => ({
  id: 1,
  name: 'Nom de la structure',
  departementCode: '33',
  ...customListOffersVenue,
})
