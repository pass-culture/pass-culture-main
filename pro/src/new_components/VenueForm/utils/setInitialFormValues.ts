import { IVenue } from 'core/Venue'

import { IVenueFormValues } from '../types'

const setInitialFormValues = (venue: IVenue): IVenueFormValues => {
  return {
    publicName: venue.publicName,
    isPermanent: venue.isPermanent,
    bannerMeta: venue.bannerMeta,
    id: venue.id,
    bannerUrl: venue.bannerUrl,
  }
}

export default setInitialFormValues
