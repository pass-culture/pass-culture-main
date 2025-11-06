import { isEqual } from 'commons/utils/isEqual'

import type { ListCollectiveOffersQueryModel } from '@/apiClient/v1'
import { CollectiveLocationType } from '@/apiClient/v1/models/CollectiveLocationType'

import type { CollectiveSearchFiltersParams } from '../types'

export const serializeApiCollectiveFilters = (
  searchFilters: Partial<CollectiveSearchFiltersParams>,
  defaultFilters: CollectiveSearchFiltersParams
): ListCollectiveOffersQueryModel => {
  const listOffersQueryKeys = [
    'nameOrIsbn',
    'offererId',
    'status',
    'venueId',
    'periodBeginningDate',
    'periodEndingDate',
    'collectiveOfferType',
    'format',
    'locationType',
    'offererAddressId',
  ] satisfies (keyof CollectiveSearchFiltersParams)[]

  const body: ListCollectiveOffersQueryModel = {}

  return listOffersQueryKeys.reduce((accumulator, field) => {
    const filterValue = searchFilters[field]

    if (field === 'locationType' && filterValue) {
      switch (filterValue) {
        case CollectiveLocationType.ADDRESS:
          accumulator.locationType = CollectiveLocationType.ADDRESS
          accumulator.offererAddressId = searchFilters.offererAddressId
            ? Number(searchFilters.offererAddressId)
            : null
          return accumulator
        case CollectiveLocationType.SCHOOL:
          accumulator.locationType = CollectiveLocationType.SCHOOL
          accumulator.offererAddressId = null
          return accumulator

        case CollectiveLocationType.TO_BE_DEFINED:
          accumulator.locationType = CollectiveLocationType.TO_BE_DEFINED
          accumulator.offererAddressId = null
          return accumulator
        default:
          return accumulator
      }
    }

    if (field === 'venueId') {
      accumulator.venueId = undefined
      return accumulator
    }

    if (filterValue && !isEqual(filterValue, defaultFilters[field])) {
      if (field === 'offererAddressId') {
        accumulator.offererAddressId = filterValue ? Number(filterValue) : null
      } else {
        ;(accumulator as any)[field] = filterValue
      }
      return accumulator
    }
    return accumulator
  }, body)
}
