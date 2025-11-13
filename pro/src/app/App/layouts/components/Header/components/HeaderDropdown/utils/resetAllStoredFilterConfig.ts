import { storageAvailable } from '@/commons/utils/storageAvailable'
import { locallyStoredFilterConfig } from '@/components/OffersTableSearch/utils'

export function resetAllStoredFilterConfig() {
  const isSessionStorageAvailable = storageAvailable('sessionStorage')
  if (isSessionStorageAvailable) {
    Object.values(locallyStoredFilterConfig).forEach((key) => {
      const previousFiltersVisibility = JSON.parse(
        sessionStorage.getItem(key) || '{}'
      ).filtersVisibility

      sessionStorage.setItem(
        key,
        JSON.stringify({
          filtersVisibility: previousFiltersVisibility || false,
          storedFilters: {},
        })
      )
    })
  }
}
