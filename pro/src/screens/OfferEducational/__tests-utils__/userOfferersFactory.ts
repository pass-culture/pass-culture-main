import { IUserOfferer, IUserVenue } from 'core/OfferEducational'

export const managedVenueFactory = (
  userVenueExtends: Partial<IUserVenue>
): IUserVenue => {
  return {
    id: 'VENUE_ID',
    name: 'Venue name',
    ...userVenueExtends,
  }
}

const userOffererFactory = (
  userOffererExtends: Partial<IUserOfferer>
): IUserOfferer => {
  return {
    id: 'OFFERER_ID',
    name: 'offerer name',
    siren: '111111',
    managedVenues: [
      managedVenueFactory({}),
      managedVenueFactory({ id: 'VENUE_ID_2', name: 'Venue name 2' }),
    ],
    ...userOffererExtends,
  }
}

export const userOfferersFactory = (
  userOfferersExtends: Partial<IUserOfferer>[]
): IUserOfferer[] => userOfferersExtends.map(userOffererFactory)
