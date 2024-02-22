import { Venue } from 'core/Venue/types'
import { humanizeSiret } from 'core/Venue/utils'

import { VenueFormValues } from '../types'

const setInitialFormValues = (venue: Venue): VenueFormValues => {
  return {
    reimbursementPointId: venue.reimbursementPointId || '',
    accessibility: venue.accessibility,
    address: venue.address || '',
    banId: venue.banId || '',
    addressAutocomplete: `${venue.address} ${venue.postalCode} ${venue.city}`,
    'search-addressAutocomplete': `${venue.address} ${venue.postalCode} ${venue.city}`,
    bannerMeta: venue.bannerMeta,
    bannerUrl: venue.bannerUrl || '',
    city: venue.city || '',
    comment: venue.comment || '',
    description: venue.description || '',
    email: venue.contact?.email || '',
    id: venue.id,
    isAccessibilityAppliedOnAllOffers: false,
    isPermanent: Boolean(venue.isPermanent),
    departmentCode: venue.departementCode || '',
    isVenueVirtual: venue.isVenueVirtual,
    latitude: venue.latitude || 0,
    longitude: venue.longitude || 0,
    bookingEmail: venue.mail,
    name: venue.name,
    phoneNumber: venue.contact?.phoneNumber || '',
    postalCode: venue.postalCode || '',
    venueSiret: venue.pricingPoint?.id || null,
    publicName: venue.publicName || '',
    webSite: venue.contact?.website || '',
    siret: humanizeSiret(venue.siret || ''),
    venueType: venue.venueType,
    venueLabel: venue.venueLabel || '',
    withdrawalDetails: venue.withdrawalDetails || '',
    isWithdrawalAppliedOnAllOffers: false,
  }
}

export default setInitialFormValues
