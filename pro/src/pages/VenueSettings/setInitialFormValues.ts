import { GetVenueResponseModel } from 'apiClient/v1'
import { humanizeSiret } from 'core/Venue/utils'

import { VenueSettingsFormValues } from './types'

export const setInitialFormValues = (
  venue: GetVenueResponseModel
): VenueSettingsFormValues => {
  return {
    street: venue.street || '',
    banId: venue.banId || '',
    addressAutocomplete: `${venue.street} ${venue.postalCode} ${venue.city}`,
    'search-addressAutocomplete': `${venue.street} ${venue.postalCode} ${venue.city}`,
    city: venue.city || '',
    coords: '',
    comment: venue.comment || '',
    latitude: String(venue.latitude) || '',
    longitude: String(venue.longitude) || '',
    bookingEmail: venue.bookingEmail || '',
    name: venue.name,
    postalCode: venue.postalCode || '',
    venueSiret: venue.pricingPoint?.id || null,
    publicName: venue.publicName || '',
    siret: humanizeSiret(venue.siret || ''),
    venueLabel: venue.venueLabelId?.toString() || '',
    venueType: venue.venueTypeCode,
    withdrawalDetails: venue.withdrawalDetails || '',
    isWithdrawalAppliedOnAllOffers: false,
    manuallySetAddress: venue.address?.isManualEdition,
  }
}
