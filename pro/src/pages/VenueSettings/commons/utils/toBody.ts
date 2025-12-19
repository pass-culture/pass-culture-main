import type { EditVenueBodyModel, VenueTypeCode } from '@/apiClient/v1'
import { removeQuotes } from '@/commons/utils/removeQuotes'
import { unhumanizeRidet, unhumanizeSiret } from '@/commons/utils/siren'
import type { PartialBy } from '@/commons/utils/types'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'

export const toBody = (
  formValues: PartialBy<VenueSettingsFormValues, 'venueType'>,
  formContext: VenueSettingsFormContext
): EditVenueBodyModel => {
  const payload: EditVenueBodyModel = {
    banId: formValues.banId,
    bookingEmail: formValues.bookingEmail,
    city: removeQuotes(formValues.city),
    comment: formValues.comment,
    latitude: Number(formValues.latitude),
    longitude: Number(formValues.longitude),
    name: formValues.name,
    postalCode: formValues.postalCode,
    inseeCode: formValues.inseeCode,
    publicName: formValues.publicName,
    street: removeQuotes(formValues.street?.trim() ?? ''),
    siret: formContext.isCaledonian
      ? unhumanizeRidet(formValues.siret, true, true)
      : unhumanizeSiret(formValues.siret),
    withdrawalDetails: formValues.withdrawalDetails,
    venueTypeCode: formValues.venueType as VenueTypeCode,
    isManualEdition: formValues.manuallySetAddress,
  }

  if (!formContext.withSiret) {
    delete payload.siret
  } else {
    payload.comment = ''
  }

  return payload
}
