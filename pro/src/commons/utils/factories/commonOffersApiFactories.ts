import { AddressResponseIsLinkedToVenueModel } from '@/apiClient/v1'

export const getAddressResponseIsLinkedToVenueModelFactory = (
  addressResponse: Partial<AddressResponseIsLinkedToVenueModel> = {}
): AddressResponseIsLinkedToVenueModel => {
  return {
    banId: 'ban',
    city: 'city',
    id: 1,
    id_oa: 1,
    inseeCode: 'inseeCode',
    isLinkedToVenue: true,
    isManualEdition: false,
    label: 'label',
    latitude: 48.866667,
    longitude: 2.333333,
    postalCode: '75008',
    street: 'ma super rue',
    ...addressResponse,
  }
}
