import { GetIndividualOfferResponseModel } from '@/apiClient/v1'
import {
  OFFER_STATUS_PENDING,
  OFFER_STATUS_REJECTED,
} from '@/commons/core/Offers/constants'
import { isOfferSynchronized } from '@/commons/core/Offers/utils/typology'
import { FORM_DEFAULT_VALUES } from '@/pages/IndividualOffer/commons/constants'

import {
  DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES,
  LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED,
} from './constants'

export function getFormReadOnlyFields(
  offer: GetIndividualOfferResponseModel
): string[] {
  const readOnlyField: string[] = []
  if ([OFFER_STATUS_REJECTED, OFFER_STATUS_PENDING].includes(offer.status)) {
    return Object.keys(DEFAULT_USEFUL_INFORMATION_INITIAL_VALUES)
  }

  if (isOfferSynchronized(offer)) {
    const editableFields: string[] = ['accessibility']

    return Object.keys(FORM_DEFAULT_VALUES).filter(
      (field: string) => !editableFields.includes(field)
    )
  }

  return readOnlyField
}

export const getLocalStorageKeyName = (
  offer: GetIndividualOfferResponseModel
) => `${LOCAL_STORAGE_USEFUL_INFORMATION_SUBMITTED}_${offer.id}`
