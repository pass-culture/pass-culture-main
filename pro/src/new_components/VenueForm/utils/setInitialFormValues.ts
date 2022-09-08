import { humanizeSiret, IVenue } from 'core/Venue'

import { IVenueFormValues } from '../types'

const setInitialFormValues = (venue: IVenue): IVenueFormValues => {
  return {
    accessibility: venue.accessibility,
    address: venue.address,
    addressAutocomplete: `${venue.address} ${venue.postalCode} ${venue.city}`,
    'search-addressAutocomplete': `${venue.address} ${venue.postalCode} ${venue.city}`,
    additionalAddress: '',
    bannerMeta: venue.bannerMeta,
    bannerUrl: venue.bannerUrl,
    city: venue.city,
    comment: venue.comment,
    description: venue.description,
    email: venue.contact.email,
    id: venue.id,
    isAccessibilityAppliedOnAllOffers: false,
    isPermanent: venue.isPermanent,
    departmentCode: venue.departmentCode,
    isVenueVirtual: venue.isVenueVirtual,
    latitude: venue.latitude,
    longitude: venue.longitude,
    mail: venue.mail,
    name: venue.name,
    phoneNumber: venue.contact.phoneNumber,
    postalCode: venue.postalCode,
    publicName: venue.publicName,
    webSite: venue.contact.webSite,
    siret: humanizeSiret(venue.siret),
    venueType: venue.venueType,
    venueLabel: venue.venueLabel,
  }
}

export default setInitialFormValues
