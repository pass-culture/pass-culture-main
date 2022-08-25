import { humanizeSiret, IVenue } from 'core/Venue'

import { IVenueFormValues } from '../types'

const setInitialFormValues = (venue: IVenue): IVenueFormValues => {
  return {
    comment: venue.comment,
    description: venue.description,
    isVenueVirtual: venue.isVenueVirtual,
    mail: venue.mail,
    name: venue.name,
    publicName: venue.publicName,
    isPermanent: venue.isPermanent,
    phoneNumber: venue.contact.phoneNumber,
    email: venue.contact.email,
    webSite: venue.contact.webSite,
    bannerMeta: venue.bannerMeta,
    id: venue.id,
    bannerUrl: venue.bannerUrl,
    siret: humanizeSiret(venue.siret),
    venueType: venue.venueType,
    venueLabel: venue.venueLabel,
  }
}

export default setInitialFormValues
