import {
  GetIndividualOfferResponseModel,
  PatchOfferBodyModel,
  WithdrawalTypeEnum,
} from 'apiClient/v1'
import { isOfferSynchronized } from 'commons/core/Offers/utils/typology'
import { AccessibilityEnum } from 'commons/core/shared/types'
import { removeQuotes } from 'commons/utils/removeQuotes'
import { trimStringsInObject } from 'commons/utils/trimStringsInObject'
import { OFFER_LOCATION } from 'pages/IndividualOffer/commons/constants'

import { UsefulInformationFormValues } from './types'

// TODO (igabriele, 2025-07-24): Make the form values naming & structure closer to the API model rather than serializing back and forth.
export const serializePatchOffer = ({
  offer,
  formValues,
  shouldSendMail = false,
  isNewOfferCreationFlowFeatureActive,
}: {
  offer: GetIndividualOfferResponseModel
  formValues: UsefulInformationFormValues
  shouldSendMail?: boolean
  isNewOfferCreationFlowFeatureActive: boolean
}): PatchOfferBodyModel => {
  const maybeAccessibilityProps = isNewOfferCreationFlowFeatureActive
    ? {}
    : {
        audioDisabilityCompliant:
          formValues.accessibility?.[AccessibilityEnum.AUDIO],
        mentalDisabilityCompliant:
          formValues.accessibility?.[AccessibilityEnum.MENTAL],
        motorDisabilityCompliant:
          formValues.accessibility?.[AccessibilityEnum.MOTOR],
        visualDisabilityCompliant:
          formValues.accessibility?.[AccessibilityEnum.VISUAL],
      }

  if (isOfferSynchronized(offer)) {
    return maybeAccessibilityProps
  }

  const maybeUrl = isNewOfferCreationFlowFeatureActive
    ? {
        url: formValues.url?.trim() || undefined,
      }
    : {}

  let addressValues = {}
  const allAddressFieldsAreNotNull =
    formValues.city &&
    formValues.latitude &&
    formValues.longitude &&
    formValues.postalCode &&
    formValues.street &&
    formValues.offerLocation
  if (!offer.isDigital && allAddressFieldsAreNotNull) {
    addressValues = {
      address: {
        banId: !formValues.banId ? undefined : formValues.banId,
        inseeCode: !formValues.inseeCode ? undefined : formValues.inseeCode,
        city: removeQuotes(formValues.city!.trim()), // checked in `allAddressFieldsAreNotNull`
        latitude: formValues.latitude,
        longitude: formValues.longitude,
        postalCode: formValues.postalCode,
        street: removeQuotes(formValues.street!.trim()), // checked in `allAddressFieldsAreNotNull`
        label: formValues.locationLabel,
        isManualEdition: formValues.manuallySetAddress,
        isVenueAddress:
          formValues.offerLocation !== OFFER_LOCATION.OTHER_ADDRESS,
      },
    }
  }

  const withdrawalDelayNullishValue =
    formValues.withdrawalType === WithdrawalTypeEnum.NO_TICKET
      ? null
      : undefined
  const withdrawalDelay =
    formValues.withdrawalDelay === undefined
      ? withdrawalDelayNullishValue
      : Number(formValues.withdrawalDelay)

  return trimStringsInObject({
    ...maybeAccessibilityProps,
    ...addressValues,
    ...maybeUrl,

    bookingContact: formValues.bookingContact,
    bookingEmail: !formValues.receiveNotificationEmails
      ? null
      : formValues.bookingEmail,
    externalTicketOfficeUrl: !formValues.externalTicketOfficeUrl
      ? null
      : formValues.externalTicketOfficeUrl,
    isNational: formValues.isNational,
    shouldSendMail: shouldSendMail,
    withdrawalDelay,
    withdrawalDetails: formValues.withdrawalDetails ?? undefined,
    withdrawalType: formValues.withdrawalType,
  })
}
