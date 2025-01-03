import { useState } from 'react'

import { SearchFiltersParams, CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { localStorageAvailable } from 'commons/utils/localStorageAvailable'

type FilterConfigType = 'individual' | 'collective' | 'template'
type SelectedFilters = Partial<SearchFiltersParams | CollectiveSearchFiltersParams>
type StoredFilterConfig = {
  filtersVisibility: boolean
  storedFilters: SelectedFilters
}

const locallyStoredFilterConfig: Record<FilterConfigType, string> = {
  individual: 'INDIVIDUAL_OFFERS_FILTER_CONFIG',
  collective: 'COLLECTIVE_OFFERS_FILTER_CONFIG',
  template: 'TEMPLATE_OFFERS_FILTER_CONFIG',
}

export const getStoredFilterConfig = (type: FilterConfigType): StoredFilterConfig => {
  const isLocalStorageAvailable = localStorageAvailable()
  const storedFilterConfig: StoredFilterConfig = isLocalStorageAvailable ?
    JSON.parse(localStorage.getItem(locallyStoredFilterConfig[type]) || '{}') :
    {}
  const { filtersVisibility, storedFilters } = storedFilterConfig

  return {
    filtersVisibility,
    storedFilters,
  }
}

export const useStoredFilterConfig = (type: FilterConfigType) => {
  const isLocalStorageAvailable = localStorageAvailable()

  const initialFilterConfig = getStoredFilterConfig(type)
  const [filterConfig, setFilterConfig] = useState(initialFilterConfig)
  const { filtersVisibility, storedFilters } = filterConfig

  const onFiltersToggle = () => {
    const newFilterConfig: StoredFilterConfig = {
      ...filterConfig,
      filtersVisibility: !filtersVisibility,
    }

    if (isLocalStorageAvailable) {
      localStorage.setItem(
        locallyStoredFilterConfig[type],
        JSON.stringify(newFilterConfig)
      )
    }

    setFilterConfig(newFilterConfig)
  }

  const onApplyFilters = (selectedFilters: SelectedFilters) => {
    const newFilterConfig: StoredFilterConfig = {
      ...filterConfig,
      storedFilters: {
        ...filterConfig.storedFilters,
        ...selectedFilters,
      }
    }

    if (isLocalStorageAvailable) {
      localStorage.setItem(
        locallyStoredFilterConfig[type],
        JSON.stringify(newFilterConfig)
      )
    }

    setFilterConfig(newFilterConfig)
  }

  return {
    filtersVisibility,
    onFiltersToggle,
    storedFilters,
    onApplyFilters,
  }
}