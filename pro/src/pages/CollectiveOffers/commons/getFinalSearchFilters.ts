import { CollectiveSearchFiltersParams } from 'commons/core/Offers/types'
import { getStoredFilterConfig } from 'components/OffersTable/OffersTableSearch/utils'

export function getFinalSearchFilters(
  urlSearchFilters: Partial<CollectiveSearchFiltersParams>,
  isToggleAndMemorizeFiltersEnabled: boolean
) {
  const { storedFilters } = getStoredFilterConfig('collective')

  return {
    ...(isToggleAndMemorizeFiltersEnabled
      ? (storedFilters as Partial<CollectiveSearchFiltersParams>)
      : {}),
    ...urlSearchFilters,
  }
}
