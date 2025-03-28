import { GetVenueResponseModel } from 'apiClient/v1'
import { humanizeSiret } from 'commons/core/Venue/utils'

import { VenueSettingsFormValues } from './types'

export const setInitialFormValues = ({
  venue,
}: {
  venue: GetVenueResponseModel
}): VenueSettingsFormValues => {
  let autoCompleteStreet = venue.address?.street
    ? venue.address.street + ' '
    : ''

  return {
    street: venue.address?.street || '',
    postalCode: venue.address?.postalCode || '',
    city: venue.address?.city || '',
    addressAutocomplete: `${autoCompleteStreet}${venue.address?.postalCode} ${venue.address?.city}`,
    'search-addressAutocomplete': `${autoCompleteStreet}${venue.address?.postalCode} ${venue.address?.city}`,
    coords: `${venue.address?.latitude}, ${venue.address?.longitude}`,
    latitude: String(venue.address?.latitude) || '',
    longitude: String(venue.address?.longitude) || '',
    banId: venue.address?.banId || null,
    manuallySetAddress: venue.address?.isManualEdition,
    comment: venue.comment || '',
    bookingEmail: venue.bookingEmail || '',
    name: venue.name,
    venueSiret: venue.pricingPoint?.id || '',
    publicName: venue.publicName || '',
    siret: humanizeSiret(venue.siret || ''),
    venueType: venue.venueTypeCode,
    withdrawalDetails: venue.withdrawalDetails || '',
  }
}
