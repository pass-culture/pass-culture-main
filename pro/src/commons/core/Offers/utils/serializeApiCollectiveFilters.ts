import { EacFormat, type ListCollectiveOffersQueryModel } from '@/apiClient/v1'
import { CollectiveLocationType } from '@/apiClient/v1/models/CollectiveLocationType'
import { nullifyEmptyProps } from '@/commons/utils/nullifyEmptyProps'
import { toEnumOrNull } from '@/commons/utils/toEnumOrNull'
import { toNumberOrNull } from '@/commons/utils/toNumberOrNull'

import type { CollectiveSearchFiltersParams } from '../types'

export const serializeApiCollectiveFilters = (
  searchFilters: Partial<CollectiveSearchFiltersParams>
): ListCollectiveOffersQueryModel => {
  const { page: _page, ...params } = searchFilters

  return nullifyEmptyProps({
    ...params,
    format: toEnumOrNull(searchFilters.format, EacFormat),
    locationType: toEnumOrNull(
      searchFilters.locationType,
      CollectiveLocationType
    ),
    offererAddressId:
      searchFilters.locationType === CollectiveLocationType.SCHOOL ||
      searchFilters.locationType === CollectiveLocationType.TO_BE_DEFINED
        ? null
        : toNumberOrNull(searchFilters.offererAddressId),
    offererId: toNumberOrNull(searchFilters.offererId),
    venueId: toNumberOrNull(searchFilters.venueId),
  })
}
