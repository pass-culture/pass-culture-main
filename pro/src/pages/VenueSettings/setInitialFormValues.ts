import { GetVenueResponseModel } from 'apiClient/v1'
import { humanizeSiret } from 'core/Venue/utils'

import { VenueSettingsFormValues } from './types'

export const setInitialFormValues = (
  venue: GetVenueResponseModel
): VenueSettingsFormValues => {
  return {
    reimbursementPointId: venue.reimbursementPointId || '',
    address: venue.address || '',
    banId: venue.banId || '',
    addressAutocomplete: `${venue.address} ${venue.postalCode} ${venue.city}`,
    'search-addressAutocomplete': `${venue.address} ${venue.postalCode} ${venue.city}`,
    city: venue.city || '',
    comment: venue.comment || '',
    latitude: venue.latitude || 0,
    longitude: venue.longitude || 0,
    bookingEmail: venue.bookingEmail || '',
    name: venue.name,
    postalCode: venue.postalCode || '',
    venueSiret: venue.pricingPoint?.id || null,
    publicName: venue.publicName || '',
    siret: humanizeSiret(venue.siret || ''),
    venueType: venue.venueTypeCode,
    withdrawalDetails: venue.withdrawalDetails || '',
    isWithdrawalAppliedOnAllOffers: false,
  }
}
