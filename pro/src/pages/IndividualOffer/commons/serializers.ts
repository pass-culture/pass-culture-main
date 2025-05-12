import {
  GetIndividualOfferResponseModel,
  PatchOfferBodyModel,
  PostOfferBodyModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { SYNCHRONIZED_OFFER_EDITABLE_FIELDS } from 'commons/core/Offers/constants'
import { isAllocineOffer } from 'commons/core/Providers/utils/localProvider'
import { AccessibilityEnum } from 'commons/core/shared/types'
import { removeQuotes } from 'commons/utils/removeQuotes'
import { trimStringsInObject } from 'commons/utils/trimStringsInObject'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'
import { IndividualOfferFormValues } from 'pages/IndividualOffer/commons/types'

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

export const serializeExtraDataForPatch = (
  formValues: Partial<IndividualOfferFormValues>
): PostOfferBodyModel['extraData'] | undefined => {
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
  const allAddressFieldsAreNotNull =
    sentValues.city &&
    sentValues.latitude &&
    sentValues.longitude &&
    sentValues.postalCode &&
    sentValues.street &&
    sentValues.offerLocation
  if (!offer.isDigital && allAddressFieldsAreNotNull) {
    addressValues = {
      address: {
        city: removeQuotes(sentValues.city!.trim()), // checked in `allAddressFieldsAreNotNull`
        latitude: sentValues.latitude,
        longitude: sentValues.longitude,
        postalCode: sentValues.postalCode,
        street: removeQuotes(sentValues.street!.trim()), // checked in `allAddressFieldsAreNotNull`
        label: sentValues.locationLabel,
        isManualEdition: sentValues.manuallySetAddress,
        isVenueAddress:
          sentValues.offerLocation === OFFER_LOCATION.OTHER_ADDRESS
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
          extraData: serializeExtraDataForPatch(sentValues),
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
    externalTicketOfficeUrl: sentValues.externalTicketOfficeUrl || null,
    shouldSendMail: shouldSendMail,
    bookingContact: sentValues.bookingContact || undefined,
    ...addressValues,
  })
}
