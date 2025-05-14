import { EditVenueBodyModel, VenueTypeCode } from 'apiClient/v1'
import { unhumanizeSiret } from 'commons/core/Venue/utils'
import { removeQuotes } from 'commons/utils/removeQuotes'

import { VenueSettingsFormValues } from './types'

export const serializeEditVenueBodyModel = (
  formValues: VenueSettingsFormValues,
  hideSiret: boolean
): EditVenueBodyModel => {
  const payload: EditVenueBodyModel = {
    banId: formValues.banId,
    bookingEmail: formValues.bookingEmail,
    city: removeQuotes(formValues.city),
    comment: formValues.comment,
    latitude: formValues.latitude,
    longitude: formValues.longitude,
    name: formValues.name,
    postalCode: formValues.postalCode,
    inseeCode: formValues.inseeCode,
    publicName: formValues.publicName,
    street: removeQuotes(formValues.street?.trim() ?? ''),
    siret: unhumanizeSiret(formValues.siret),
    withdrawalDetails: formValues.withdrawalDetails,
    venueTypeCode: formValues.venueType as VenueTypeCode,
    isManualEdition: formValues.manuallySetAddress,
  }

  if (hideSiret) {
    delete payload.siret
  } else {
    payload.comment = ''
  }

  return payload
}
