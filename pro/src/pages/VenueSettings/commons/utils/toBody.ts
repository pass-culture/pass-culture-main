import type { EditVenueBodyModel } from '@/apiClient/v1'
import { removeQuotes } from '@/commons/utils/removeQuotes'
import { unhumanizeRidet, unhumanizeSiret } from '@/commons/utils/siren'

import type {
  VenueSettingsFormContext,
  VenueSettingsFormValues,
} from '../types'

export const toBody = (
  formValues: VenueSettingsFormValues,
  formContext: VenueSettingsFormContext
): EditVenueBodyModel => {
  const payload: EditVenueBodyModel = {}

  if ('name' in formValues) {
    payload.banId = formValues.banId
    payload.city = removeQuotes(formValues.city)
    payload.comment = formValues.comment
    payload.latitude = Number(formValues.latitude)
    payload.longitude = Number(formValues.longitude)
    payload.name = formValues.name
    payload.postalCode = formValues.postalCode
    payload.inseeCode = formValues.inseeCode
    payload.publicName = formValues.publicName
    payload.street = removeQuotes(formValues.street?.trim() ?? '')
    payload.siret = formContext.isCaledonian
      ? unhumanizeRidet(formValues.siret, true, true)
      : unhumanizeSiret(formValues.siret)
    payload.isManualEdition = formValues.manuallySetAddress

    if (!formContext.withSiret) {
      delete payload.siret
    } else {
      payload.comment = ''
    }
  }

  if ('bookingEmail' in formValues) {
    payload.bookingEmail = formValues.bookingEmail
  }

  if ('withdrawalDetails' in formValues) {
    payload.withdrawalDetails = formValues.withdrawalDetails
  }

  return payload
}
