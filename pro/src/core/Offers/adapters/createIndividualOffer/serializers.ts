/* istanbul ignore file: DEBT, TO FIX */
import { PostOfferBodyModel } from 'apiClient/v1'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { IOfferExtraData } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

/* istanbul ignore next: DEBT, TO FIX */
export const serializeExtraData = (
  formValues: IOfferIndividualFormValues
): IOfferExtraData => {
  const extraData: IOfferExtraData = {}
  if (formValues.author) extraData.author = formValues.author
  if (formValues.isbn) extraData.isbn = formValues.isbn
  if (formValues.musicType) extraData.musicType = formValues.musicType
  if (formValues.musicSubType) extraData.musicSubType = formValues.musicSubType
  if (formValues.performer) extraData.performer = formValues.performer
  if (formValues.showType) extraData.showType = formValues.showType
  if (formValues.showSubType) extraData.showSubType = formValues.showSubType
  if (formValues.speaker) extraData.speaker = formValues.speaker
  if (formValues.stageDirector)
    extraData.stageDirector = formValues.stageDirector
  if (formValues.visa) extraData.visa = formValues.visa

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
  formValues: IOfferIndividualFormValues
): PostOfferBodyModel => {
  return {
    audioDisabilityCompliant: formValues.accessibility[AccessiblityEnum.AUDIO],
    bookingEmail: formValues.bookingEmail || null,
    description: formValues.description || null,
    extraData: serializeExtraData(formValues),
    isEducational: false,
    isNational: formValues.isNational,
    isDuo: formValues.isDuo,
    mentalDisabilityCompliant:
      formValues.accessibility[AccessiblityEnum.MENTAL],
    motorDisabilityCompliant: formValues.accessibility[AccessiblityEnum.MOTOR],
    name: formValues.name,
    offererId: formValues.offererId,
    subcategoryId: formValues.subcategoryId,
    venueId: formValues.venueId,
    visualDisabilityCompliant:
      formValues.accessibility[AccessiblityEnum.VISUAL],
    withdrawalDelay: formValues.withdrawalDelay || null,
    withdrawalDetails: formValues.withdrawalDetails || null,
    withdrawalType: formValues.withdrawalType || null,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes || ''),
    url: formValues.url || null,
    externalTicketOfficeUrl: formValues.externalTicketOfficeUrl || null,
  }
}
