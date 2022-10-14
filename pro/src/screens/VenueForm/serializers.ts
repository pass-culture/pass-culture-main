import { EditVenueBodyModel } from 'apiClient/v1'
import { PostVenueBodyModel } from 'apiClient/v1/models/PostVenueBodyModel'
import { unhumanizeSiret } from 'core/Venue'
import { IVenueFormValues } from 'new_components/VenueForm'

export const serializePostVenueBodyModel = (
  formValues: IVenueFormValues,
  isSiretValued: boolean,
  offererId: string
): PostVenueBodyModel => {
  const model = {
    address: formValues.address,
    audioDisabilityCompliant: formValues.accessibility.audio,
    bookingEmail: formValues.mail,
    city: formValues.city,
    comment: formValues.comment,
    description: formValues.description,
    latitude: formValues.latitude,
    longitude: formValues.longitude,
    mentalDisabilityCompliant: formValues.accessibility.mental,
    motorDisabilityCompliant: formValues.accessibility.motor,
    name: formValues.name,
    postalCode: formValues.postalCode,
    publicName: formValues.publicName,
    siret: unhumanizeSiret(formValues.siret),
    venueLabelId: formValues.venueLabel,
    venueTypeCode: formValues.venueType,
    visualDisabilityCompliant: formValues.accessibility.visual,
    withdrawalDetails: formValues.withdrawalDetails,
    contact: {
      email: formValues.email,
      phoneNumber: formValues.phoneNumber,
      website: formValues.webSite,
      socialMedias: null,
    },
    managingOffererId: offererId,
  }

  if (!isSiretValued) {
    delete model.siret
  } else {
    model.comment = ''
  }

  return model
}
export const serializeEditVenueBodyModel = (
  formValues: IVenueFormValues,
  venueLabels: SelectOption[],
  isSiretValued: boolean
): EditVenueBodyModel => {
  const model: EditVenueBodyModel = {
    address: formValues.address,
    audioDisabilityCompliant: formValues.accessibility.audio,
    bookingEmail: formValues.mail,
    city: formValues.city,
    comment: formValues.comment,
    description: formValues.description,
    latitude: formValues.latitude,
    longitude: formValues.longitude,
    mentalDisabilityCompliant: formValues.accessibility.mental,
    motorDisabilityCompliant: formValues.accessibility.motor,
    name: formValues.name,
    postalCode: formValues.postalCode,
    publicName: formValues.publicName,
    siret: unhumanizeSiret(formValues.siret),
    // @ts-expect-error string is not assignable to type number
    venueLabelId: formValues.venueLabel,
    venueTypeCode: formValues.venueType,
    visualDisabilityCompliant: formValues.accessibility.visual,
    withdrawalDetails: formValues.withdrawalDetails,
    contact: {
      email: formValues.email,
      phoneNumber: formValues.phoneNumber,
      website: formValues.webSite,
      socialMedias: null,
    },
    isAccessibilityAppliedOnAllOffers:
      formValues.isAccessibilityAppliedOnAllOffers,
    isEmailAppliedOnAllOffers: false,
  }
  if (!isSiretValued) {
    delete model.siret
  } else {
    model.comment = ''
  }

  return model
}
