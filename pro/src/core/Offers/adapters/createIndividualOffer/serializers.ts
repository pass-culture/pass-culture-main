/* istanbul ignore file: DEBT, TO FIX */
import { PostOfferBodyModel } from 'apiClient/v1'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm'
import { OfferExtraData } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

/* istanbul ignore next: DEBT, TO FIX */
const serializeExtraData = (
  formValues: IndividualOfferFormValues
): OfferExtraData => {
  const extraData: OfferExtraData = {}
  if (formValues.author) {
    extraData.author = formValues.author
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
  /* istanbul ignore next: DEBT, TO FIX */
  if (durationHour.trim().length === 0) {
    return null
  }

  /* istanbul ignore next: DEBT, TO FIX */
  const [hours, minutes] = durationHour
    .split(':')
    .map((s: string) => parseInt(s, 10))

  /* istanbul ignore next: DEBT, TO FIX */
  return minutes + hours * 60
}

export const serializePostOffer = (
  formValues: IndividualOfferFormValues
): PostOfferBodyModel => {
  return {
    audioDisabilityCompliant: formValues.accessibility[AccessiblityEnum.AUDIO],
    bookingContact: formValues.bookingContact || null,
    bookingEmail: formValues.bookingEmail || null,
    description: formValues.description || null,
    extraData: serializeExtraData(formValues),
    isNational: formValues.isNational,
    isDuo: formValues.isDuo,
    mentalDisabilityCompliant:
      formValues.accessibility[AccessiblityEnum.MENTAL],
    motorDisabilityCompliant: formValues.accessibility[AccessiblityEnum.MOTOR],
    name: formValues.name,
    subcategoryId: formValues.subcategoryId,
    // FIXME mageoffray (2023-04-03) : This is a dirty fix until GET /venues route returns dehumanized Id
    venueId: Number(formValues.venueId),
    visualDisabilityCompliant:
      formValues.accessibility[AccessiblityEnum.VISUAL],
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
