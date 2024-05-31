import { SAVED_OFFERER_ID_KEY } from 'core/shared/constants'
import { SelectOption } from 'custom_types/form'
import { localStorageAvailable } from 'utils/localStorageAvailable'

export const getSavedOffererId = (
  offererOptions: SelectOption[]
): string | null => {
  const isLocalStorageAvailable = localStorageAvailable()
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
