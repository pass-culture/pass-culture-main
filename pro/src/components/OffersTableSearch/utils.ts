import type { CollectiveSearchFiltersParams } from '@/commons/core/Offers/types'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { ensureSelectedPartnerVenue } from '@/commons/store/user/selectors'
import {
  SESSION_STORAGE_KEY,
  sessionStorageManager,
} from '@/commons/utils/sessionStorageManager'
import type { IndividualOffersFilters } from '@/pages/IndividualOffers/common/types'

type StoredFilterConfig = {
  filtersVisibility: boolean
  storedFilters: Partial<
    IndividualOffersFilters | CollectiveSearchFiltersParams
  >
}

type StoredFilterConfigWithVenue = StoredFilterConfig & {
  storedVenueId?: string | number
}

export type FilterConfigType = 'individual' | 'collective' | 'template'

const locallyStoredFilterConfig: Record<FilterConfigType, SESSION_STORAGE_KEY> =
  {
    individual: SESSION_STORAGE_KEY.INDIVIDUAL_OFFERS_FILTER_CONFIG,
    collective: SESSION_STORAGE_KEY.COLLECTIVE_OFFERS_FILTER_CONFIG,
    template: SESSION_STORAGE_KEY.TEMPLATE_OFFERS_FILTER_CONFIG,
  }

const getStoredFilterConfigKey = (type: FilterConfigType) =>
  locallyStoredFilterConfig[type]

export function getStoredFilterConfig(
  type: FilterConfigType,
  venueId?: string | number
): StoredFilterConfig {
  const storageKey = getStoredFilterConfigKey(type)

  const storedFilterConfig =
    sessionStorageManager.getJSON<StoredFilterConfigWithVenue>(storageKey)
  if (!storedFilterConfig) {
    return {
      filtersVisibility: false,
      storedFilters: {},
    }
  }

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

  sessionStorageManager.removeItem(storageKey)
  return {
    filtersVisibility: false,
    storedFilters: {},
  }
}

export function useStoredFilterConfig<
  T extends 'individual' | 'collective' | 'template',
>(type: T) {
  const selectedPartnerVenue = useAppSelector(ensureSelectedPartnerVenue)
  const filterConfig = getStoredFilterConfig(type, selectedPartnerVenue.id)

  const onFiltersToggle = (filtersVisibility: boolean) => {
    const newFilterConfig: StoredFilterConfigWithVenue = {
      ...filterConfig,
      filtersVisibility,
      storedVenueId: selectedPartnerVenue.id,
    }

    sessionStorageManager.setJSON(
      getStoredFilterConfigKey(type),
      newFilterConfig
    )
  }

  const onApplyFilters = (
    selectedFilters: Partial<
      IndividualOffersFilters | CollectiveSearchFiltersParams
    >
  ) => {
    const newFilterConfig: StoredFilterConfigWithVenue = {
      ...filterConfig,
      storedFilters: {
        ...filterConfig.storedFilters,
        ...selectedFilters,
      } as StoredFilterConfig['storedFilters'],
      storedVenueId: selectedPartnerVenue.id,
    }

    sessionStorageManager.setJSON(
      getStoredFilterConfigKey(type),
      newFilterConfig
    )
  }

  const onResetFilters = (resetNameOrIsbn = true) => {
    const nameKey = type === 'individual' ? 'nameOrIsbn' : 'name'
    const newFilterConfig: StoredFilterConfigWithVenue = {
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

    sessionStorageManager.setJSON(
      getStoredFilterConfigKey(type),
      newFilterConfig
    )
  }

  return {
    ...filterConfig,
    onFiltersToggle,
    onApplyFilters,
    onResetFilters,
  }
}
