import type { LocationResponseModel } from '@/apiClient/v1'

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
    ...addressResponse,
  }
}
