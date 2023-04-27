import { PatchOfferBodyModel } from 'apiClient/v1'
import { IOfferIndividualFormValues } from 'components/OfferIndividualForm'
import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'core/Offers'
import { IOfferExtraData, IOfferIndividual } from 'core/Offers/types'
import { isAllocineOffer } from 'core/Providers/utils/localProvider'
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
  extraData.ean = formValues.ean
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
interface ISerializePatchOffer {
  offer: IOfferIndividual
  formValues: Partial<IOfferIndividualFormValues>
  shouldSendMail?: boolean
}

export const serializePatchOffer = ({
  offer,
  formValues,
  shouldSendMail = false,
}: ISerializePatchOffer): PatchOfferBodyModel => {
  let sentValues: Partial<IOfferIndividualFormValues> = formValues
  if (offer?.lastProvider) {
    const {
      ALLOCINE: allocineEditableFields,
      ALL_PROVIDERS: allProvidersEditableFields,
    } = SYNCHRONIZED_OFFER_EDITABLE_FIELDS

    const asArray = Object.entries(formValues)

    const editableFields = allProvidersEditableFields
    if (isAllocineOffer(offer)) {
      editableFields.push(...allocineEditableFields)
    }
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const filtered = asArray.filter(([key, _]) => editableFields.includes(key))

    sentValues = Object.fromEntries(filtered)
  }

  return {
    audioDisabilityCompliant:
      sentValues.accessibility &&
      sentValues.accessibility[AccessiblityEnum.AUDIO],
    description: sentValues.description,
    extraData: serializeExtraData(sentValues),
    isNational: sentValues.isNational,
    isDuo: !!sentValues.isDuo,
    mentalDisabilityCompliant:
      sentValues.accessibility &&
      sentValues.accessibility[AccessiblityEnum.MENTAL],
    motorDisabilityCompliant:
      sentValues.accessibility &&
      sentValues.accessibility[AccessiblityEnum.MOTOR],
    name: sentValues.name,
    withdrawalDelay:
      sentValues.withdrawalDelay === undefined
        ? null
        : Number(sentValues.withdrawalDelay),
    withdrawalDetails: sentValues.withdrawalDetails || undefined,
    visualDisabilityCompliant:
      sentValues.accessibility &&
      sentValues.accessibility[AccessiblityEnum.VISUAL],
    withdrawalType: sentValues.withdrawalType,
    durationMinutes: serializeDurationMinutes(sentValues.durationMinutes || ''),
    bookingEmail:
      sentValues.receiveNotificationEmails === undefined
        ? undefined
        : sentValues.receiveNotificationEmails === false
        ? null
        : sentValues.bookingEmail,
    externalTicketOfficeUrl: sentValues.externalTicketOfficeUrl || undefined,
    url: sentValues.url || undefined,
    shouldSendMail: shouldSendMail,
  }
}
