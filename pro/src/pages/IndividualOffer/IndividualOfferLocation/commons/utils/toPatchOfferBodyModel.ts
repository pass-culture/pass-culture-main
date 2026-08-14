import type {
  GetIndividualOfferResponseModel,
  PatchOfferBodyModel,
} from '@/apiClient/v1'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'

import type { LocationFormValues, PhysicalAddressSubformValues } from '../types'

const toLocationBodyModel = (
  location: PhysicalAddressSubformValues
): PatchOfferBodyModel['location'] => {
  if (location.isVenueLocation) {
    return { isVenueLocation: true }
  }

  // the validation schema requires `street` for `OTHER_ADDRESS`
  assertOrFrontendError(location.street, '`location.street` is null')

  // listed explicitly because the subform also carries UI-only values
  return {
    isVenueLocation: false,
    banId: location.banId,
    city: location.city,
    inseeCode: location.inseeCode,
    isManualEdition: location.isManualEdition,
    label: location.label,
    latitude: location.latitude,
    longitude: location.longitude,
    postalCode: location.postalCode,
    street: location.street,
  }
}

export const toPatchOfferBodyModel = ({
  offer,
  formValues,
  shouldSendMail,
}: {
  offer: GetIndividualOfferResponseModel
  formValues: LocationFormValues
  shouldSendMail: boolean
}): PatchOfferBodyModel => {
  if (isOfferSynchronized(offer)) {
    return {}
  }

  const { location, url } = formValues

  return {
    ...(url !== null && { url }),
    ...(location !== null && { location: toLocationBodyModel(location) }),
    // TODO (igabriele, 2025-07-19): Add this prop to Yup schema set it via react-hook-form.
    shouldSendMail,
  }
}
