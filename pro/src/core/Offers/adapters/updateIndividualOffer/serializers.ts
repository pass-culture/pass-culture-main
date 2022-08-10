import { PatchOfferBodyModel } from 'apiClient/v1'
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

const serializeDurationMinutes = (durationHour: string): number | null => {
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
): PatchOfferBodyModel => {
  return {
    audioDisabilityCompliant: formValues.accessibility[AccessiblityEnum.AUDIO],
    description: formValues.description,
    extraData: serializeExtraData(formValues),
    isNational: formValues.isNational,
    mentalDisabilityCompliant:
      formValues.accessibility[AccessiblityEnum.MENTAL],
    motorDisabilityCompliant: formValues.accessibility[AccessiblityEnum.MOTOR],
    name: formValues.name,
    venueId: formValues.venueId,
    visualDisabilityCompliant:
      formValues.accessibility[AccessiblityEnum.VISUAL],
    withdrawalDelay: formValues.withdrawalDelay,
    withdrawalDetails: formValues.withdrawalDetails,
    withdrawalType: formValues.withdrawalType,
    durationMinutes: serializeDurationMinutes(formValues.durationMinutes || ''),
  }
}
