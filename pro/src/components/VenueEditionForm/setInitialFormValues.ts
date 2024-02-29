import { GetVenueResponseModel } from 'apiClient/v1'
import { AccessiblityEnum } from 'core/shared'
import { humanizeSiret } from 'core/Venue/utils'

import { VenueEditionFormValues } from './types'

export const setInitialFormValues = (
  venue: GetVenueResponseModel
): VenueEditionFormValues => {
  const venueAccessibility = {
    [AccessiblityEnum.VISUAL]: venue.visualDisabilityCompliant || false,
    [AccessiblityEnum.MENTAL]: venue.mentalDisabilityCompliant || false,
    [AccessiblityEnum.AUDIO]: venue.audioDisabilityCompliant || false,
    [AccessiblityEnum.MOTOR]: venue.motorDisabilityCompliant || false,
    [AccessiblityEnum.NONE]: [
      venue.visualDisabilityCompliant,
      venue.mentalDisabilityCompliant,
      venue.audioDisabilityCompliant,
      venue.motorDisabilityCompliant,
    ].every((accessibility) => accessibility === false),
  }

  return {
    reimbursementPointId: venue.reimbursementPointId || '',
    accessibility: venueAccessibility,
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
    isVenueVirtual: venue.isVirtual,
    latitude: venue.latitude || 0,
    longitude: venue.longitude || 0,
    bookingEmail: venue.bookingEmail || '',
    name: venue.name,
    phoneNumber: venue.contact?.phoneNumber || '',
    postalCode: venue.postalCode || '',
    venueSiret: venue.pricingPoint?.id || null,
    publicName: venue.publicName || '',
    webSite: venue.contact?.website || '',
    siret: humanizeSiret(venue.siret || ''),
    venueType: venue.venueTypeCode,
    venueLabel: venue.venueLabelId?.toString() || '',
    withdrawalDetails: venue.withdrawalDetails || '',
    isWithdrawalAppliedOnAllOffers: false,
  }
}
