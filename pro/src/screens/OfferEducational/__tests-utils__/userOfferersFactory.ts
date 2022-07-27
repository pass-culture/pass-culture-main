import merge from 'lodash/merge'

import { IUserOfferer, IUserVenue } from 'core/OfferEducational'

export const managedVenueFactory = (
  userVenueExtends: Partial<IUserVenue>
): IUserVenue =>
  merge(
    {},
    {
      id: 'VENUE_ID',
      name: 'Venue name',
      address: {
        street: '2 bis Street Name',
        postalCode: '93100',
        city: 'Montreuil',
      },
    },
    userVenueExtends
  )

export const managedVenuesFactory = (
  managedVenuesExtends: Partial<IUserVenue>[]
): IUserVenue[] => managedVenuesExtends.map(managedVenueFactory)

const userOffererFactory = (
  userOffererExtends: Partial<IUserOfferer>
): IUserOfferer => {
  return {
    id: 'OFFERER_ID',
    name: 'offerer name',
    managedVenues: [managedVenueFactory({})],
    ...userOffererExtends,
  }
}

export const userOfferersFactory = (
  userOfferersExtends: Partial<IUserOfferer>[]
): IUserOfferer[] => userOfferersExtends.map(userOffererFactory)
