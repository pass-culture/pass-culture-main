import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import { storageAvailable } from '@/commons/utils/storageAvailable'
import type { IndividualOffersFilters } from '@/pages/IndividualOffers/common/types'

type StoredFilterConfig = {
  filtersVisibility: boolean
  storedFilters: Partial<
    IndividualOffersFilters | CollectiveSearchFiltersParams
  >
}

export type FilterConfigType = 'individual' | 'collective' | 'template'

const locallyStoredFilterConfig: Record<FilterConfigType, string> = {
  individual: 'INDIVIDUAL_OFFERS_FILTER_CONFIG',
  collective: 'COLLECTIVE_OFFERS_FILTER_CONFIG',
  template: 'TEMPLATE_OFFERS_FILTER_CONFIG',
}

const getStoredFilterConfigKey = (type: FilterConfigType) =>
  locallyStoredFilterConfig[type]

export function getStoredFilterConfig(
  type: FilterConfigType,
  venueId?: string | number
): StoredFilterConfig {
  const isSessionStorageAvailable = storageAvailable('sessionStorage')
  const storageKey = getStoredFilterConfigKey(type)

  if (!isSessionStorageAvailable) {
    return {
      filtersVisibility: false,
      storedFilters: {},
    }
  }

  const rawConfig = sessionStorage.getItem(storageKey)
  if (!rawConfig) {
    return {
      filtersVisibility: false,
      storedFilters: {},
    }
  }

  const storedFilterConfig: StoredFilterConfig & {
    storedVenueId?: string | number
  } = JSON.parse(rawConfig)
  const {
    filtersVisibility = false,
    storedFilters = {},
    storedVenueId,
  } = storedFilterConfig

  if (venueId === undefined) {
    if (storedVenueId === undefined) {
      return {
        filtersVisibility,
        storedFilters,
      }
    }

    return {
      filtersVisibility: false,
      storedFilters: {},
    }
  }

  if (storedVenueId === venueId) {
    return {
      filtersVisibility,
      storedFilters,
    }
  }

  sessionStorage.removeItem(storageKey)
  return {
    filtersVisibility: false,
    storedFilters: {},
  }
}

export function useStoredFilterConfig<
  T extends 'individual' | 'collective' | 'template',
>(type: T) {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const isSessionStorageAvailable = storageAvailable('sessionStorage')
  const filterConfig = getStoredFilterConfig(type, selectedPartnerVenue.id)

  const onFiltersToggle = (filtersVisibility: boolean) => {
    const newFilterConfig: StoredFilterConfig & {
      storedVenueId?: string | number
    } = {
      ...filterConfig,
      filtersVisibility,
      storedVenueId: selectedPartnerVenue.id,
    }

    if (isSessionStorageAvailable) {
      const storageKey = getStoredFilterConfigKey(type)
      sessionStorage.setItem(storageKey, JSON.stringify(newFilterConfig))
    }
  }

  const onApplyFilters = (
    selectedFilters: Partial<
      IndividualOffersFilters | CollectiveSearchFiltersParams
    >
  ) => {
    const newFilterConfig: StoredFilterConfig & {
      storedVenueId?: string | number
    } = {
      ...filterConfig,
      storedFilters: {
        ...filterConfig.storedFilters,
        ...selectedFilters,
      } as StoredFilterConfig['storedFilters'],
      storedVenueId: selectedPartnerVenue.id,
    }

    if (isSessionStorageAvailable) {
      const storageKey = getStoredFilterConfigKey(type)
      sessionStorage.setItem(storageKey, JSON.stringify(newFilterConfig))
    }
  }

  const onResetFilters = (resetNameOrIsbn = true) => {
    const nameKey = type === 'individual' ? 'nameOrIsbn' : 'name'
    const newFilterConfig: StoredFilterConfig & {
      storedVenueId?: string | number
    } = {
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
      storedVenueId: selectedPartnerVenue.id,
    }

    if (isSessionStorageAvailable) {
      const storageKey = getStoredFilterConfigKey(type)
      sessionStorage.setItem(storageKey, JSON.stringify(newFilterConfig))
    }
  }

  return {
    ...filterConfig,
    onFiltersToggle,
    onApplyFilters,
    onResetFilters,
  }
}
