import { PostOfferBodyModel } from 'apiClient/v1'
import { IOfferExtraData } from 'core/Offers/types'
import { AccessiblityEnum } from 'core/shared'
import { IOfferIndividualFormValues } from 'new_components/OfferIndividualForm'

export const serializeApiErrors = (
  errors: Record<string, string>
): Record<string, string> => {
  const apiFieldsMap: Record<string, string> = {
    venue: 'venueId',
  }
  const formErrors: Record<string, string> = {}
  let formFieldName
  for (const apiFieldName in errors) {
    formFieldName =
      apiFieldName in apiFieldsMap ? apiFieldsMap[apiFieldName] : apiFieldName
    formErrors[formFieldName] = errors[apiFieldName]
  }
  return formErrors
}

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
  if (durationHour.trim().length === 0) {
    return null
  }
  const [hours, minutes] = durationHour
    .split(':')
    .map((s: string) => parseInt(s, 10))

  return minutes + hours * 60
}

export const serializePostOffer = (
  formValues: IOfferIndividualFormValues
): PostOfferBodyModel => {
  return {
    audioDisabilityCompliant: formValues.accessibility[AccessiblityEnum.AUDIO],
    description: formValues.description,
    extraData: serializeExtraData(formValues),
    isEducational: false,
    isNational: formValues.isNational,
    isDuo: !!formValues.isDuo,
    mentalDisabilityCompliant:
      formValues.accessibility[AccessiblityEnum.MENTAL],
    motorDisabilityCompliant: formValues.accessibility[AccessiblityEnum.MOTOR],
    name: formValues.name,
    offererId: formValues.offererId,
    subcategoryId: formValues.subcategoryId,
    venueId: formValues.venueId,
    visualDisabilityCompliant:
      formValues.accessibility[AccessiblityEnum.VISUAL],
    withdrawalDelay: formValues.withdrawalDelay,
    withdrawalDetails: formValues.withdrawalDetails,
    withdrawalType: formValues.withdrawalType,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes || ''),
  }
}
