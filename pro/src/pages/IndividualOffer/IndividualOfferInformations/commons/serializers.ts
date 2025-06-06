import {
  GetIndividualOfferResponseModel,
  PatchOfferBodyModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { AccessibilityEnum } from 'commons/core/shared/types'
import { removeQuotes } from 'commons/utils/removeQuotes'
import { trimStringsInObject } from 'commons/utils/trimStringsInObject'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'

import { UsefulInformationFormValues } from './types'

export const serializePatchOffer = ({
  offer,
  formValues,
  shouldSendMail = false,
}: {
  offer: GetIndividualOfferResponseModel
  formValues: UsefulInformationFormValues
  shouldSendMail?: boolean
}): PatchOfferBodyModel => {
  let sentValues: Partial<UsefulInformationFormValues> = formValues

  if (offer.lastProvider) {
    const asArray = Object.entries(formValues)
    const editableFields = [
      'audioDisabilityCompliant',
      'mentalDisabilityCompliant',
      'motorDisabilityCompliant',
      'visualDisabilityCompliant',
      'accessibility',
    ]

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
        banId: !sentValues.banId ? undefined : sentValues.banId,
        inseeCode: !sentValues.inseeCode ? undefined : sentValues.inseeCode,
        city: removeQuotes(sentValues.city!.trim()), // checked in `allAddressFieldsAreNotNull`
        latitude: sentValues.latitude,
        longitude: sentValues.longitude,
        postalCode: sentValues.postalCode,
        street: removeQuotes(sentValues.street!.trim()), // checked in `allAddressFieldsAreNotNull`
        label: sentValues.locationLabel,
        isManualEdition: sentValues.manuallySetAddress,
        isVenueAddress:
          sentValues.offerLocation !== OFFER_LOCATION.OTHER_ADDRESS,
      },
    }
  }

  const withdrawalDelayNullishValue =
    sentValues.withdrawalType === WithdrawalTypeEnum.NO_TICKET
      ? null
      : undefined
  const withdrawalDelay =
    sentValues.withdrawalDelay === undefined
      ? withdrawalDelayNullishValue
      : Number(sentValues.withdrawalDelay)

  return trimStringsInObject({
    ...addressValues,
    audioDisabilityCompliant:
      sentValues.accessibility?.[AccessibilityEnum.AUDIO],
    bookingContact: sentValues.bookingContact,
    bookingEmail: !sentValues.receiveNotificationEmails
      ? null
      : sentValues.bookingEmail,
    externalTicketOfficeUrl: !sentValues.externalTicketOfficeUrl
      ? null
      : sentValues.externalTicketOfficeUrl,
    isNational: sentValues.isNational,
    mentalDisabilityCompliant:
      sentValues.accessibility?.[AccessibilityEnum.MENTAL],
    motorDisabilityCompliant:
      sentValues.accessibility?.[AccessibilityEnum.MOTOR],
    shouldSendMail: shouldSendMail,
    visualDisabilityCompliant:
      sentValues.accessibility?.[AccessibilityEnum.VISUAL],
    withdrawalDelay,
    withdrawalDetails: sentValues.withdrawalDetails ?? undefined,
    withdrawalType: sentValues.withdrawalType,
  })
}
