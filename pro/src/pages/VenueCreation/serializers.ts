import { PostVenueBodyModel } from 'apiClient/v1/models/PostVenueBodyModel'
import { unhumanizeSiret } from 'commons/core/Venue/utils'
import { VenueCreationFormValues } from 'pages/VenueCreation/types'

export const serializePostVenueBodyModel = (
  formValues: VenueCreationFormValues,
  offererId: number,
  hideSiret: boolean
): PostVenueBodyModel => {
  const payload: PostVenueBodyModel = {
    audioDisabilityCompliant: formValues.accessibility.audio,
    bookingEmail: formValues.bookingEmail,
    comment: formValues.comment,
    mentalDisabilityCompliant: formValues.accessibility.mental,
    motorDisabilityCompliant: formValues.accessibility.motor,
    name: formValues.name,
    publicName: formValues.publicName,
    siret: unhumanizeSiret(formValues.siret),
    venueTypeCode: formValues.venueType,
    visualDisabilityCompliant: formValues.accessibility.visual,
    contact: {
      email: null,
      phoneNumber: null,
      website: null,
      socialMedias: null,
    },
    venueLabelId: null,
    managingOffererId: offererId,
    address: {
      banId: formValues.banId,
      city: formValues.city,
      latitude: formValues.latitude,
      longitude: formValues.longitude,
      postalCode: formValues.postalCode,
      street: formValues.street
    }
  }

  if (hideSiret) {
    delete payload.siret
  } else {
    payload.comment = ''
  }

  return payload
}
