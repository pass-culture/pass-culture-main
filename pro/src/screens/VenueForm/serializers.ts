import { EditVenueBodyModel } from 'apiClient/v1'
import { PostVenueBodyModel } from 'apiClient/v1/models/PostVenueBodyModel'
import { unhumanizeSiret } from 'core/Venue'
import { IVenueFormValues } from 'new_components/VenueForm'

interface VenueBodyModelParams {
  hideSiret: boolean
  offererId: string
}

type HideSiretParam = Pick<VenueBodyModelParams, 'hideSiret'>
type VenueBodyModel = Omit<
  PostVenueBodyModel,
  'managingOffererId' | 'venueLabelId'
>

const serializeCommunData = (
  formValues: IVenueFormValues,
  { hideSiret }: HideSiretParam
): VenueBodyModel => {
  const model = {
    address: formValues.address,
    audioDisabilityCompliant: formValues.accessibility.audio,
    bookingEmail: formValues.bookingEmail,
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
    venueTypeCode: formValues.venueType,
    visualDisabilityCompliant: formValues.accessibility.visual,
    withdrawalDetails: formValues.withdrawalDetails,
    contact: {
      email: formValues.email,
      phoneNumber: formValues.phoneNumber,
      website: formValues.webSite,
      socialMedias: null,
    },
  }

  if (hideSiret) {
    delete model.siret
  } else {
    model.comment = ''
  }

  return model
}

export const serializePostVenueBodyModel = (
  formValues: IVenueFormValues,
  { hideSiret, offererId }: VenueBodyModelParams
): PostVenueBodyModel => {
  const model = serializeCommunData(formValues, {
    hideSiret,
  })
  return {
    ...model,
    venueLabelId:
      formValues.venueLabel.length === 0 ? null : formValues.venueLabel,
    managingOffererId: offererId,
  }
}

export const serializeEditVenueBodyModel = (
  formValues: IVenueFormValues,
  { hideSiret }: HideSiretParam
): EditVenueBodyModel => {
  const model = serializeCommunData(formValues, {
    hideSiret,
  })
  return {
    ...model,
    // @ts-expect-error string is not assignable to type number
    venueLabelId: formValues.venueLabel,
    isEmailAppliedOnAllOffers: true,
  }
}
