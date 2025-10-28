import type { GetVenueResponseModel } from '@/apiClient/v1'
import { humanizeSiret, unhumanizeRidet } from '@/commons/utils/siren'

import type { VenueSettingsFormValues } from '../types'

export const toFormValues = ({
  venue,
}: {
  venue: GetVenueResponseModel
}): VenueSettingsFormValues => {
  const autoCompleteStreet = venue.address?.street
    ? `${venue.address.street} `
    : ''

  return {
    street: venue.address?.street || '',
    postalCode: venue.address?.postalCode || '',
    inseeCode: venue.address?.inseeCode || null,
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
    siret: venue.isCaledonian
      ? unhumanizeRidet(venue.siret || '', false, false)
      : humanizeSiret(venue.siret || ''),
    venueType: venue.venueType.value,
    withdrawalDetails: venue.withdrawalDetails || '',
  }
}
