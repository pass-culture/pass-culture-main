import type { GetOffererNameResponseModel } from '@/apiClient/v1'
import {
  LOCAL_STORAGE_KEY,
  localStorageManager,
} from '@/commons/utils/localStorageManager'

export const getInitialAdminOffererId = (
  offererNames: GetOffererNameResponseModel[]
): number | null => {
  if (!offererNames || offererNames.length === 0) {
    return null
  }

  const savedAdminOffererId = localStorageManager.getItem(
    LOCAL_STORAGE_KEY.SELECTED_ADMIN_OFFERER_ID
  )

  if (savedAdminOffererId) {
    const savedOfferer = offererNames.find(
      (offerer) => offerer.id === Number(savedAdminOffererId)
    )

    if (savedOfferer) {
      return savedOfferer.id
    }
  }

  return offererNames.at(0)?.id ?? null
}
