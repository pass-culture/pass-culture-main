import { PatchOfferBodyModel } from 'apiClient/v1'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { IOfferExtraData } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'

export const serializeExtraData = (
  formValues: Partial<IOfferIndividualFormValues>
): IOfferExtraData | undefined => {
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

  const isEmpty = Object.values(extraData).every(value => value === undefined)

  return isEmpty ? undefined : extraData
}

export const serializeDurationMinutes = (
  durationHour: string
): number | undefined => {
  if (durationHour.trim().length === 0) {
    return undefined
  }
  const [hours, minutes] = durationHour
    .split(':')
    .map((s: string) => parseInt(s, 10))

  return minutes + hours * 60
}

export const serializePatchOffer = (
  formValues: Partial<IOfferIndividualFormValues>
): PatchOfferBodyModel => ({
  audioDisabilityCompliant:
    formValues.accessibility &&
    formValues.accessibility[AccessiblityEnum.AUDIO],
  description: formValues.description,
  extraData: serializeExtraData(formValues),
  isNational: formValues.isNational,
  isDuo: !!formValues.isDuo,
  mentalDisabilityCompliant:
    formValues.accessibility &&
    formValues.accessibility[AccessiblityEnum.MENTAL],
  motorDisabilityCompliant:
    formValues.accessibility &&
    formValues.accessibility[AccessiblityEnum.MOTOR],
  name: formValues.name,
  venueId: formValues.venueId,
  withdrawalDelay: formValues.withdrawalDelay || null,
  withdrawalDetails: formValues.withdrawalDetails || null,
  visualDisabilityCompliant:
    formValues.accessibility &&
    formValues.accessibility[AccessiblityEnum.VISUAL],
  withdrawalType: formValues.withdrawalType,
  durationMinutes: serializeDurationMinutes(formValues.durationMinutes || ''),
  bookingEmail: formValues.receiveNotificationEmails
    ? formValues.bookingEmail
    : undefined,
  externalTicketOfficeUrl: formValues.externalTicketOfficeUrl || undefined,
  url: formValues.url || undefined,
})
