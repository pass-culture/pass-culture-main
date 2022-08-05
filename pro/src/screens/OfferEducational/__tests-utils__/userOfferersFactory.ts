import merge from 'lodash/merge'

import {
  GetEducationalOffererResponseModel,
  GetEducationalOffererVenueResponseModel,
} from 'apiClient/v1'

export const managedVenueFactory = (
  userVenueExtends: Partial<GetEducationalOffererVenueResponseModel>
): GetEducationalOffererVenueResponseModel =>
  merge(
    {},
    {
      id: 'VENUE_ID',
      name: 'Venue name',
      address: '2 bis Street Name',
      postalCode: '93100',
      city: 'Montreuil',
      isVirtual: false,
    },
    userVenueExtends
  )

export const managedVenuesFactory = (
  managedVenuesExtends: Partial<GetEducationalOffererVenueResponseModel>[]
): GetEducationalOffererVenueResponseModel[] =>
  managedVenuesExtends.map(managedVenueFactory)

export const userOffererFactory = (
  userOffererExtends: Partial<GetEducationalOffererResponseModel>
): GetEducationalOffererResponseModel => {
  return {
    id: 'OFFERER_ID',
    name: 'offerer name',
    managedVenues: [managedVenueFactory({})],
    ...userOffererExtends,
  }
}

export const userOfferersFactory = (
  userOfferersExtends: Partial<GetEducationalOffererResponseModel>[]
): GetEducationalOffererResponseModel[] =>
  userOfferersExtends.map(userOffererFactory)
