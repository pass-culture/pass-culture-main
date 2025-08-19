import type {
  GetIndividualOfferResponseModel,
  PatchOfferBodyModel,
} from '@/apiClient/v1'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { removeQuotes } from '@/commons/utils/removeQuotes'
import { trimStringsInObject } from '@/commons/utils/trimStringsInObject'
import { OFFER_LOCATION } from '@/pages/IndividualOffer/commons/constants'

import type { LocationFormValues } from '../types'

function isPhysicalLocationComplete(
  formValues: LocationFormValues
): formValues is LocationFormValues & {
  city: string
  latitude: string
  longitude: string
  postalCode: string
  street: string
} {
  return (
    !!formValues.city &&
    !!formValues.latitude &&
    !!formValues.longitude &&
    !!formValues.postalCode &&
    !!formValues.street &&
    !!formValues.offerLocation
  )
}

// TODO (igabriele, 2025-07-19): Handle these dynamic props, logical & formatting rules via Yup schema to keep a single source of rules.
// TODO (igabriele, 2025-07-19): Finish updating form values structure to match expected Patch payload and maybe prefix pure Frontend fields (`$internalField`).
export const toPatchOfferPayload = ({
  offer,
  formValues,
  shouldSendWarningMail,
}: {
  offer: GetIndividualOfferResponseModel
  formValues: LocationFormValues
  shouldSendWarningMail: boolean
}): PatchOfferBodyModel => {
  if (isOfferSynchronized(offer)) {
    return {}
  }

  const maybePhysicalLocation =
    !offer.isDigital && isPhysicalLocationComplete(formValues)
      ? {
          address: {
            banId: formValues.banId,
            city: removeQuotes(formValues.city),
            inseeCode: formValues.inseeCode,
            isManualEdition: formValues.isManualEdition,
            isVenueAddress:
              formValues.offerLocation !== OFFER_LOCATION.OTHER_ADDRESS,
            label: formValues.locationLabel,
            latitude: formValues.latitude,
            longitude: formValues.longitude,
            postalCode: formValues.postalCode,
            street: removeQuotes(formValues.street),
          },
        }
      : {
          address: null,
        }

  return trimStringsInObject({
    ...maybePhysicalLocation,
    shouldSendMail: shouldSendWarningMail,
    url: formValues.url?.trim() || null,
  })
}
