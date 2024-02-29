import { EditVenueBodyModel } from 'apiClient/v1'

import { VenueEditionFormValues } from './types'

export interface EditVirtualVenueBodyModel {
  reimbursementPointId?: number | null
}

export const serializeEditVenueBodyModel = (
  formValues: VenueEditionFormValues,
  hideSiret: boolean
): EditVenueBodyModel => {
  const payload: EditVenueBodyModel = {
    audioDisabilityCompliant: formValues.accessibility.audio,
    description: formValues.description,
    mentalDisabilityCompliant: formValues.accessibility.mental,
    motorDisabilityCompliant: formValues.accessibility.motor,
    visualDisabilityCompliant: formValues.accessibility.visual,
    contact: {
      email: !formValues.email ? null : formValues.email,
      phoneNumber: !formValues.phoneNumber ? null : formValues.phoneNumber,
      website: !formValues.webSite ? null : formValues.webSite,
      socialMedias: null,
    },
    venueLabelId: !formValues.venueLabel ? null : Number(formValues.venueLabel),
    isEmailAppliedOnAllOffers: true,
    isAccessibilityAppliedOnAllOffers:
      formValues.isAccessibilityAppliedOnAllOffers,
  }

  if (hideSiret) {
    delete payload.siret
  } else {
    payload.comment = ''
  }

  return payload
}
