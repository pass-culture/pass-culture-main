import type {
  GetIndividualOfferResponseModel,
  PatchOfferBodyModel,
} from '@/apiClient/v1'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'

import type { LocationFormValues } from '../types'

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

  const formValuesWithoutNulls = Object.fromEntries(
    Object.entries(formValues).filter(([, value]) => value !== null)
  )

  return {
    ...formValuesWithoutNulls,
    // TODO (igabriele, 2025-07-19): Add this prop to Yup schema set it via react-hook-form.
    shouldSendMail,
  }
}
