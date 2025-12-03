import type {
  CollectiveSearchFiltersParams,
  IndividualSearchFiltersParams,
} from '@/commons/core/Offers/types'
import { storageAvailable } from '@/commons/utils/storageAvailable'

type StoredFilterConfig = {
  filtersVisibility: boolean
  storedFilters: Partial<
    IndividualSearchFiltersParams | CollectiveSearchFiltersParams
  >
}

export type FilterConfigType = 'individual' | 'collective' | 'template'

export const locallyStoredFilterConfig: Record<FilterConfigType, string> = {
  individual: 'INDIVIDUAL_OFFERS_FILTER_CONFIG',
  collective: 'COLLECTIVE_OFFERS_FILTER_CONFIG',
  template: 'TEMPLATE_OFFERS_FILTER_CONFIG',
}

export function getStoredFilterConfig(
  type: FilterConfigType
): StoredFilterConfig {
  const isSessionStorageAvailable = storageAvailable('sessionStorage')
  const storedFilterConfig: StoredFilterConfig = isSessionStorageAvailable
    ? JSON.parse(
        sessionStorage.getItem(locallyStoredFilterConfig[type]) || '{}'
      )
    : {}
  const { filtersVisibility = false, storedFilters = {} } = storedFilterConfig

  return {
    filtersVisibility,
    storedFilters,
  }
}

export function useStoredFilterConfig<
  T extends 'individual' | 'collective' | 'template',
>(type: T) {
  const isSessionStorageAvailable = storageAvailable('sessionStorage')

  const onFiltersToggle = (filtersVisibility: boolean) => {
    const filterConfig = getStoredFilterConfig(type)
    const newFilterConfig: StoredFilterConfig = {
      ...filterConfig,
      filtersVisibility,
    }

    if (isSessionStorageAvailable) {
      sessionStorage.setItem(
        locallyStoredFilterConfig[type],
        JSON.stringify(newFilterConfig)
      )
    }
  }

  const onApplyFilters = (
    selectedFilters: Partial<
      IndividualSearchFiltersParams | CollectiveSearchFiltersParams
    >
  ) => {
    const filterConfig = getStoredFilterConfig(type)
    const newFilterConfig: StoredFilterConfig = {
      ...filterConfig,
      storedFilters: {
        ...filterConfig.storedFilters,
        ...selectedFilters,
      },
    }

    // We don't want to store offererId to support offerer switching.
    // The /offers API will be called with a different offererId, but with the same filters saved
    // by type of offer (individual, collective, template).
    delete newFilterConfig.storedFilters.offererId

    if (isSessionStorageAvailable) {
      sessionStorage.setItem(
        locallyStoredFilterConfig[type],
        JSON.stringify(newFilterConfig)
      )
    }
  }

  const onResetFilters = (resetNameOrIsbn = true) => {
    const filterConfig = getStoredFilterConfig(type)
    const nameKey = type === 'individual' ? 'nameOrIsbn' : 'name'
    const newFilterConfig: StoredFilterConfig = {
      ...filterConfig,
      storedFilters: {
        ...(!resetNameOrIsbn
          ? {
              [nameKey]:
                filterConfig.storedFilters[
                  nameKey as keyof typeof filterConfig.storedFilters
                ],
            }
          : {}),
      },
    }

    if (isSessionStorageAvailable) {
      sessionStorage.setItem(
        locallyStoredFilterConfig[type],
        JSON.stringify(newFilterConfig)
      )
    }
  }

  return {
    onFiltersToggle,
    onApplyFilters,
    onResetFilters,
  }
}
