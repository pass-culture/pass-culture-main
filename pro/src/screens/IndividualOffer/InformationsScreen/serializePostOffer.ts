/* istanbul ignore file: DEBT, TO FIX */
import { PostOfferBodyModel } from 'apiClient/v1'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import { AccessibilityEnum } from 'core/shared/types'

/* istanbul ignore next: DEBT, TO FIX */
const serializeExtraData = (
  formValues: IndividualOfferFormValues
): PostOfferBodyModel['extraData'] => {
  const extraData: PostOfferBodyModel['extraData'] = {}
  if (formValues.author) {
    extraData.author = formValues.author
  }
  if (formValues.musicType) {
    extraData.musicType = formValues.musicType
  }
  if (formValues.musicSubType) {
    extraData.musicSubType = formValues.musicSubType
  }
  if (formValues.gtl_id) {
    extraData.gtl_id = formValues.gtl_id
  }
  if (formValues.performer) {
    extraData.performer = formValues.performer
  }
  if (formValues.ean) {
    extraData.ean = formValues.ean
  }
  if (formValues.showType) {
    extraData.showType = formValues.showType
  }
  if (formValues.showSubType) {
    extraData.showSubType = formValues.showSubType
  }
  if (formValues.speaker) {
    extraData.speaker = formValues.speaker
  }
  if (formValues.stageDirector) {
    extraData.stageDirector = formValues.stageDirector
  }
  if (formValues.visa) {
    extraData.visa = formValues.visa
  }

  return extraData
}

const serializeDurationMinutes = (durationHour: string): number | null => {
  if (durationHour.trim().length === 0) {
    return null
  }

  const [hours, minutes] = durationHour
    .split(':')
    .map((s: string) => parseInt(s, 10))

  return (minutes || 0) + (hours || 0) * 60
}

export const serializePostOffer = (
  formValues: IndividualOfferFormValues
): PostOfferBodyModel => {
  return {
    audioDisabilityCompliant: formValues.accessibility[AccessibilityEnum.AUDIO],
    bookingContact: formValues.bookingContact || null,
    bookingEmail: formValues.bookingEmail || null,
    description: formValues.description || null,
    extraData: serializeExtraData(formValues),
    isNational: formValues.isNational,
    isDuo: formValues.isDuo,
    mentalDisabilityCompliant:
      formValues.accessibility[AccessibilityEnum.MENTAL],
    motorDisabilityCompliant: formValues.accessibility[AccessibilityEnum.MOTOR],
    name: formValues.name,
    subcategoryId: formValues.subcategoryId,
    // FIXME mageoffray (2023-04-03) : This is a dirty fix until GET /venues route returns dehumanized Id
    venueId: Number(formValues.venueId),
    visualDisabilityCompliant:
      formValues.accessibility[AccessibilityEnum.VISUAL],
    withdrawalDelay:
      formValues.withdrawalDelay === undefined
        ? null
        : formValues.withdrawalDelay,
    withdrawalDetails: formValues.withdrawalDetails || null,
    withdrawalType: formValues.withdrawalType || null,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes || ''),
    url: formValues.url || null,
    externalTicketOfficeUrl: formValues.externalTicketOfficeUrl || null,
  }
}
