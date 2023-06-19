import { EditVenueBodyModel } from 'apiClient/v1'
import { PostVenueBodyModel } from 'apiClient/v1/models/PostVenueBodyModel'
import { IVenueFormValues } from 'components/VenueForm'
import { unhumanizeSiret } from 'core/Venue'

interface VenueBodyModelParams {
  hideSiret: boolean
  offererId: number
}

type HideSiretParam = Pick<VenueBodyModelParams, 'hideSiret'>
type VenueBodyModel = Omit<
  PostVenueBodyModel,
  'managingOffererId' | 'venueLabelId'
>

export interface EditVirtualVenueBodyModel {
  reimbursementPointId?: number | null
}

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
      email: !formValues.email ? null : formValues.email,
      phoneNumber: !formValues.phoneNumber ? null : formValues.phoneNumber,
      website: !formValues.webSite ? null : formValues.webSite,
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
    venueLabelId: Number(formValues.venueLabel) || null,
    managingOffererId: offererId,
  }
}

export const serializeEditVenueBodyModel = (
  formValues: IVenueFormValues,
  { hideSiret }: HideSiretParam,
  shouldSendMail?: boolean
): EditVenueBodyModel | EditVirtualVenueBodyModel => {
  const reimbursementPointId =
    !formValues.reimbursementPointId || formValues.reimbursementPointId === ''
      ? null
      : Number(formValues.reimbursementPointId)
  if (formValues.isVenueVirtual) {
    return {
      reimbursementPointId: reimbursementPointId,
    }
  } else {
    const model = serializeCommunData(formValues, {
      hideSiret,
    })
    return {
      ...model,
      // @ts-expect-error string is not assignable to type number
      venueLabelId: !formValues.venueLabel ? null : formValues.venueLabel,
      isEmailAppliedOnAllOffers: true,
      isWithdrawalAppliedOnAllOffers: formValues.isWithdrawalAppliedOnAllOffers,
      reimbursementPointId: reimbursementPointId,
      shouldSendMail: shouldSendMail,
      isAccessibilityAppliedOnAllOffers:
        formValues.isAccessibilityAppliedOnAllOffers,
    }
  }
}
