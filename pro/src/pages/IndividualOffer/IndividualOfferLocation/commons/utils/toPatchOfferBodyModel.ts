import type {
  GetIndividualOfferResponseModel,
  PatchOfferBodyModel,
} from '@/apiClient/v1'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'

import type { LocationFormValues } from '../types'

export const toPatchOfferBodyModel = ({
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

  return {
    ...formValues,
    // TODO (igabriele, 2025-07-19): Add this prop to Yup schema set it via react-hook-form.
    shouldSendMail: shouldSendWarningMail,
  }
}
