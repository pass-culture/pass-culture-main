import { SAVED_OFFERER_ID_KEY } from '@/commons/core/shared/constants'
import { SelectOption } from '@/commons/custom_types/form'
import { storageAvailable } from '@/commons/utils/storageAvailable'

export const getSavedOffererId = (
  offererOptions: SelectOption[]
): string | null => {
  const isLocalStorageAvailable = storageAvailable('localStorage')
  if (!isLocalStorageAvailable) {
    return null
  }

  const savedOffererId = localStorage.getItem(SAVED_OFFERER_ID_KEY)
  if (
    savedOffererId &&
    !offererOptions.map((option) => option.value).includes(savedOffererId)
  ) {
    return null
  }

  return savedOffererId
}
