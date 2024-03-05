import { EditVenueBodyModel, VenueTypeCode } from 'apiClient/v1'
import { unhumanizeSiret } from 'core/Venue/utils'

import { VenueSettingsFormValues } from './types'

export const serializeEditVenueBodyModel = (
  formValues: VenueSettingsFormValues,
  hideSiret: boolean,
  isVenueVirtual: boolean,
  shouldSendMail?: boolean
): EditVenueBodyModel => {
  const reimbursementPointId =
    !formValues.reimbursementPointId || formValues.reimbursementPointId === ''
      ? null
      : Number(formValues.reimbursementPointId)

  if (isVenueVirtual) {
    return {
      reimbursementPointId: reimbursementPointId,
    }
  }

  const payload: EditVenueBodyModel = {
    address: formValues.address,
    banId: formValues.banId,
    bookingEmail: formValues.bookingEmail,
    city: formValues.city,
    comment: formValues.comment,
    latitude: formValues.latitude,
    longitude: formValues.longitude,
    name: formValues.name,
    postalCode: formValues.postalCode,
    publicName: formValues.publicName,
    siret: unhumanizeSiret(formValues.siret),
    withdrawalDetails: formValues.withdrawalDetails,
    isEmailAppliedOnAllOffers: true,
    isWithdrawalAppliedOnAllOffers: formValues.isWithdrawalAppliedOnAllOffers,
    reimbursementPointId: reimbursementPointId,
    shouldSendMail: shouldSendMail,
    venueLabelId: !formValues.venueLabel ? null : Number(formValues.venueLabel),
    venueTypeCode: formValues.venueType as VenueTypeCode,
  }

  if (hideSiret) {
    delete payload.siret
  } else {
    payload.comment = ''
  }

  return payload
}
