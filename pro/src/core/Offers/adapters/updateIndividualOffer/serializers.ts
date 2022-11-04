import { PatchOfferBodyModel } from 'apiClient/v1'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { IOfferExtraData } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

export const serializeExtraData = (
  formValues: IOfferIndividualFormValues
): IOfferExtraData => {
  // TODO: change api create and update offer in order not to save
  // extra data fields that's aren't link to offer subCategory
  const extraData: IOfferExtraData = {}
  extraData.author = formValues.author
  extraData.isbn = formValues.isbn
  extraData.musicType = formValues.musicType
  extraData.musicSubType = formValues.musicSubType
  extraData.performer = formValues.performer
  extraData.showType = formValues.showType
  extraData.showSubType = formValues.showSubType
  extraData.speaker = formValues.speaker
  extraData.stageDirector = formValues.stageDirector
  extraData.visa = formValues.visa

  return extraData
}

export const serializeDurationMinutes = (
  durationHour: string
): number | null => {
  if (durationHour.trim().length === 0) {
    return null
  }
  const [hours, minutes] = durationHour
    .split(':')
    .map((s: string) => parseInt(s, 10))

  return minutes + hours * 60
}

export const serializePatchOffer = (
  formValues: IOfferIndividualFormValues
): PatchOfferBodyModel => ({
  audioDisabilityCompliant: formValues.accessibility[AccessiblityEnum.AUDIO],
  description: formValues.description,
  extraData: serializeExtraData(formValues),
  isNational: formValues.isNational,
  isDuo: !!formValues.isDuo,
  mentalDisabilityCompliant: formValues.accessibility[AccessiblityEnum.MENTAL],
  motorDisabilityCompliant: formValues.accessibility[AccessiblityEnum.MOTOR],
  name: formValues.name,
  venueId: formValues.venueId,
  visualDisabilityCompliant: formValues.accessibility[AccessiblityEnum.VISUAL],
  withdrawalDelay: formValues.withdrawalDelay,
  withdrawalDetails: formValues.withdrawalDetails,
  withdrawalType: formValues.withdrawalType,
  durationMinutes: serializeDurationMinutes(formValues.durationMinutes || ''),
  bookingEmail: formValues.receiveNotificationEmails
    ? formValues.bookingEmail
    : null,
  externalTicketOfficeUrl: formValues.externalTicketOfficeUrl || null,
  url: formValues.url || null,
})
