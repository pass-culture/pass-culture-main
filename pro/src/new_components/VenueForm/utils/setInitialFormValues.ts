import { IVenue } from 'core/Venue'

import { IVenueFormValues } from '../types'

const setInitialFormValues = (venue: IVenue): IVenueFormValues => {
  return {
    publicName: venue.publicName,
  }
}

export default setInitialFormValues
