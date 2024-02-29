import { PostVenueBodyModel } from 'apiClient/v1/models/PostVenueBodyModel'
import { unhumanizeSiret } from 'core/Venue/utils'
import { VenueCreationFormValues } from 'pages/VenueCreation/types'

export const serializePostVenueBodyModel = (
  formValues: VenueCreationFormValues,
  offererId: number,
  hideSiret: boolean
): PostVenueBodyModel => {
  const payload: PostVenueBodyModel = {
    address: formValues.address,
    audioDisabilityCompliant: formValues.accessibility.audio,
    banId: formValues.banId,
    bookingEmail: formValues.bookingEmail,
    city: formValues.city,
    comment: formValues.comment,
    latitude: formValues.latitude,
    longitude: formValues.longitude,
    mentalDisabilityCompliant: formValues.accessibility.mental,
    motorDisabilityCompliant: formValues.accessibility.motor,
    name: formValues.name,
    postalCode: formValues.postalCode,
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
  }

  if (hideSiret) {
    delete payload.siret
  } else {
    payload.comment = ''
  }

  return payload
}
