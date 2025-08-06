import merge from 'lodash/merge'

import {
  GetEducationalOffererResponseModel,
  GetEducationalOffererVenueResponseModel,
} from '@/apiClient//v1'

let venueId = 1

export const managedVenueFactory = (
  userVenueExtends: Partial<GetEducationalOffererVenueResponseModel> = {}
): GetEducationalOffererVenueResponseModel => {
  const currentVenueId = venueId++
  return merge(
    {},
    {
      id: currentVenueId,
      name: 'Venue name',
      address: '2 bis Street Name',
      postalCode: '93100',
      city: 'Montreuil',
      isVirtual: false,
    },
    userVenueExtends
  )
}

export const managedVenuesFactory = (
  managedVenuesExtends: Partial<GetEducationalOffererVenueResponseModel>[]
): GetEducationalOffererVenueResponseModel[] =>
  managedVenuesExtends.map(managedVenueFactory)

let offererId = 1

export const userOffererFactory = (
  userOffererExtends: Partial<GetEducationalOffererResponseModel> = {}
): GetEducationalOffererResponseModel => {
  const currentOffererId = offererId++
  return {
    id: currentOffererId,
    name: 'offerer name',
    allowedOnAdage: true,
    managedVenues: [managedVenueFactory({})],
    ...userOffererExtends,
  }
}
