import { GetVenueResponseModel } from 'apiClient/v1'
import { humanizeSiret } from 'commons/core/Venue/utils'

import { VenueSettingsFormValues } from './types'

export const setInitialFormValues = ({
  venue,
}: {
  venue: GetVenueResponseModel
}): VenueSettingsFormValues => {
  const addressFields = venue.address || venue

  let autoCompleteStreet = addressFields.street
    ? addressFields.street + ' '
    : ''

  return {
    street: addressFields.street || '',
    postalCode: addressFields.postalCode || '',
    city: addressFields.city || '',
    addressAutocomplete: `${autoCompleteStreet}${addressFields.postalCode} ${addressFields.city}`,
    'search-addressAutocomplete': `${autoCompleteStreet}${addressFields.postalCode} ${addressFields.city}`,
    coords: `${addressFields.latitude}, ${addressFields.longitude}`,
    latitude: String(addressFields.latitude) || '',
    longitude: String(addressFields.longitude) || '',
    banId: addressFields.banId || null,
    manuallySetAddress: venue.address?.isManualEdition,
    comment: venue.comment || '',
    bookingEmail: venue.bookingEmail || '',
    name: venue.name,
    venueSiret: venue.pricingPoint?.id || '',
    publicName: venue.publicName || '',
    siret: humanizeSiret(venue.siret || ''),
    venueLabel: venue.venueLabelId?.toString() || '',
    venueType: venue.venueTypeCode,
    withdrawalDetails: venue.withdrawalDetails || '',
  }
}
