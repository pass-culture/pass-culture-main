import type { GetVenueResponseModel } from '@/apiClient/v1'
import { humanizeSiret, unhumanizeRidet } from '@/commons/utils/siren'

import type { VenueSettingsFormValuesType } from '../validationSchema'

export const toFormValues = ({
  venue,
}: {
  venue: GetVenueResponseModel
}): VenueSettingsFormValuesType => {
  const autoCompleteStreet = venue.location?.street
    ? `${venue.location.street} `
    : ''

  return {
    street: venue.location?.street || '',
    postalCode: venue.location?.postalCode || '',
    inseeCode: venue.location?.inseeCode || null,
    city: venue.location?.city || '',
    addressAutocomplete: `${autoCompleteStreet}${venue.location?.postalCode} ${venue.location?.city}`,
    'search-addressAutocomplete': `${autoCompleteStreet}${venue.location?.postalCode} ${venue.location?.city}`,
    coords: `${venue.location?.latitude}, ${venue.location?.longitude}`,
    latitude: String(venue.location?.latitude) || '',
    longitude: String(venue.location?.longitude) || '',
    banId: venue.location?.banId || null,
    manuallySetAddress: venue.location?.isManualEdition ?? false,
    comment: venue.comment || '',
    bookingEmail: venue.bookingEmail || '',
    name: venue.name,
    venueSiret: venue.pricingPoint?.id || '',
    publicName: venue.publicName || '',
    siret: venue.isCaledonian
      ? unhumanizeRidet(venue.siret || '', false, false)
      : humanizeSiret(venue.siret || ''),
    venueType: venue.venueType.value,
    withdrawalDetails: venue.withdrawalDetails || '',
  }
}
