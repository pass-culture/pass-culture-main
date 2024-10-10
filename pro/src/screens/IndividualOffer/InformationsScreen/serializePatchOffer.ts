import {
  GetIndividualOfferResponseModel,
  PatchOfferBodyModel,
  PostOfferBodyModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { OFFER_LOCATION } from 'components/IndividualOfferForm/OfferLocation/constants'
import { IndividualOfferFormValues } from 'components/IndividualOfferForm/types'
import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'core/Offers/constants'
import { isAllocineOffer } from 'core/Providers/utils/localProvider'
import { AccessibilityEnum } from 'core/shared/types'
import { trimStringsInObject } from 'utils/trimStringsInObject'

export const serializeExtraData = (
  formValues: Partial<IndividualOfferFormValues>
): PostOfferBodyModel['extraData'] | undefined => {
  // TODO: change api create and update offer in order not to save
  // extra data fields that's aren't link to offer subCategory

  const extraData: PostOfferBodyModel['extraData'] = {}
  extraData.author = formValues.author
  extraData.gtl_id = formValues.gtl_id
  extraData.musicType = formValues.musicType
  extraData.musicSubType = formValues.musicSubType
  extraData.performer = formValues.performer
  extraData.ean = formValues.ean
  extraData.showType = formValues.showType
  extraData.showSubType = formValues.showSubType
  extraData.speaker = formValues.speaker
  extraData.stageDirector = formValues.stageDirector
  extraData.visa = formValues.visa

  const isEmpty = Object.values(extraData).every((value) => value === undefined)

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
interface SerializePatchOffer {
  offer: GetIndividualOfferResponseModel
  formValues: Partial<IndividualOfferFormValues>
  shouldSendMail?: boolean
  shouldNotSendExtraData?: boolean
}

export const serializePatchOffer = ({
  offer,
  formValues,
  shouldSendMail = false,
  shouldNotSendExtraData = false,
}: SerializePatchOffer): PatchOfferBodyModel => {
  let sentValues: Partial<IndividualOfferFormValues> = formValues
  if (offer.lastProvider) {
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

  let addressValues = {}
  // Once WIP_ENABLE_OFFER_ADDRESS have been adopted, just remove this condition and place Object address in the lower return
  //  (address data would always be present in payload)
  if (
    sentValues.city &&
    sentValues.latitude &&
    sentValues.longitude &&
    sentValues.postalCode &&
    sentValues.street
  ) {
    addressValues = {
      address: {
        city: sentValues.city,
        latitude: sentValues.latitude,
        longitude: sentValues.longitude,
        postalCode: sentValues.postalCode,
        street: sentValues.street,
        label: sentValues.locationLabel,
        isManualEdition: sentValues.manuallySetAddress,
        isVenueAddress:
          sentValues.offerlocation === OFFER_LOCATION.OTHER_ADDRESS
            ? false
            : true,
      },
    }
  }

  return trimStringsInObject({
    audioDisabilityCompliant:
      sentValues.accessibility &&
      sentValues.accessibility[AccessibilityEnum.AUDIO],
    description: sentValues.description,
    ...(shouldNotSendExtraData
      ? {}
      : {
          extraData: serializeExtraData(sentValues),
        }),
    isNational: sentValues.isNational,
    isDuo: sentValues.isDuo,
    mentalDisabilityCompliant:
      sentValues.accessibility &&
      sentValues.accessibility[AccessibilityEnum.MENTAL],
    motorDisabilityCompliant:
      sentValues.accessibility &&
      sentValues.accessibility[AccessibilityEnum.MOTOR],
    name: sentValues.name,
    withdrawalDelay:
      sentValues.withdrawalDelay === undefined
        ? sentValues.withdrawalType === WithdrawalTypeEnum.NO_TICKET
          ? null
          : undefined
        : Number(sentValues.withdrawalDelay),
    withdrawalDetails: sentValues.withdrawalDetails ?? undefined,
    visualDisabilityCompliant:
      sentValues.accessibility &&
      sentValues.accessibility[AccessibilityEnum.VISUAL],
    withdrawalType: sentValues.withdrawalType,
    durationMinutes: serializeDurationMinutes(sentValues.durationMinutes || ''),
    bookingEmail:
      sentValues.receiveNotificationEmails === undefined
        ? undefined
        : !sentValues.receiveNotificationEmails
          ? null
          : sentValues.bookingEmail,
    url: sentValues.url || undefined,
    shouldSendMail: shouldSendMail,
    bookingContact: sentValues.bookingContact || undefined,
    ...addressValues,
  })
}
