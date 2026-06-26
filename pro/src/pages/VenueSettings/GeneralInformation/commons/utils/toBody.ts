import type { ActivityOpenToPublic, EditVenueBodyModel } from '@/apiClient/v1'
import { normalizeActivity } from '@/commons/core/VenueEdition/serializeEditVenueBodyModel'
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

  if ('withdrawalDetails' in formValues) {
    payload.withdrawalDetails = formValues.withdrawalDetails
  }

  payload.isOpenToPublic = formValues.isOpenToPublic
    ? formValues.isOpenToPublic === 'true'
    : undefined

  const normalizedActivity = normalizeActivity(formValues.activity)
  payload.activity =
    normalizedActivity === null
      ? null
      : (normalizedActivity as ActivityOpenToPublic)

  payload.culturalDomains = formValues.culturalDomains
  payload.description = formValues.description

  return payload
}
