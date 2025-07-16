import { PatchDraftOfferBodyModel, PostDraftOfferBodyModel } from 'apiClient/v1'
import { trimStringsInObject } from 'commons/utils/trimStringsInObject'

import { DetailsFormValues } from './types'

export const serializeDurationMinutes = (
  durationHour: string
): number | undefined => {
  /* istanbul ignore next: DEBT, TO FIX */
  if (durationHour.trim().length === 0) {
    return undefined
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const [hours, minutes] = durationHour
    .split(':')
    .map((s: string) => parseInt(s, 10))

  return minutes + hours * 60
}

export function deSerializeDurationMinutes(durationMinute: number): string {
  const hours = Math.floor(durationMinute / 60)
  const minutes = (durationMinute % 60).toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

const serializeExtraData = (formValues: DetailsFormValues) => {
  return trimStringsInObject({
    author: formValues.author,
    gtl_id: formValues.gtl_id,
    performer: formValues.performer,
    showType: formValues.showType,
    showSubType: formValues.showSubType,
    speaker: formValues.speaker,
    stageDirector: formValues.stageDirector,
    visa: formValues.visa,
    ean: formValues.ean,
  })
}

export function serializeDetailsPostData(
  formValues: DetailsFormValues,
  isNewOfferCreationFlowFeatureActive: boolean
): PostDraftOfferBodyModel {
  return trimStringsInObject({
    name: formValues.name,
    subcategoryId: formValues.subcategoryId,
    venueId: Number(formValues.venueId),
    description: formValues.description,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes ?? ''),
    extraData: serializeExtraData(formValues),
    productId: formValues.productId ? Number(formValues.productId) : undefined,
    url: formValues.url,

    ...(isNewOfferCreationFlowFeatureActive
      ? {
          audioDisabilityCompliant: formValues.accessibility?.audio,
          mentalDisabilityCompliant: formValues.accessibility?.mental,
          motorDisabilityCompliant: formValues.accessibility?.motor,
          visualDisabilityCompliant: formValues.accessibility?.visual,
        }
      : {}),
  })
}

export function serializeDetailsPatchData(
  formValues: DetailsFormValues,
  isNewOfferCreationFlowFeatureActive: boolean
): PatchDraftOfferBodyModel {
  return trimStringsInObject({
    name: formValues.name,
    subcategoryId: formValues.subcategoryId,
    description: formValues.description,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes ?? ''),
    extraData: serializeExtraData(formValues),
    url: formValues.url,

    ...(isNewOfferCreationFlowFeatureActive
      ? {
          audioDisabilityCompliant: formValues.accessibility?.audio,
          mentalDisabilityCompliant: formValues.accessibility?.mental,
          motorDisabilityCompliant: formValues.accessibility?.motor,
          visualDisabilityCompliant: formValues.accessibility?.visual,
        }
      : {}),
  })
}
