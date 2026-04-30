import { describe, expect, it } from 'vitest'

import { OfferStatus } from '@/apiClient/v1'
import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import { ALL_FORMATS } from '@/commons/core/Offers/constants'
import type { SearchListParams } from '@/commons/core/Offers/types'
import { serializeApiIndividualFilters } from '@/commons/core/Offers/utils/serializeApiIndividualFilters'

const baseFilters: ListOffersQueryModel & SearchListParams = {
  categoryId: undefined,
  creationMode: undefined,
  format: ALL_FORMATS,
  nameOrIsbn: undefined,
  offererAddressId: undefined,
  offererId: undefined,
  periodBeginningDate: undefined,
  periodEndingDate: undefined,
  status: undefined,
  venueId: undefined,
}

describe('serializeApiIndividualFilters', () => {
  it('should strip the frontend-only `format` and `page` fields', () => {
    const result = serializeApiIndividualFilters({
      ...baseFilters,
      page: 3,
    })

    expect('format' in result).toBe(false)
    expect('page' in result).toBe(false)
  })

  it('should forward backend-shaped fields untouched', () => {
    const result = serializeApiIndividualFilters({
      ...baseFilters,
      categoryId: 'BOOKS',
      creationMode: 'manual',
      offererAddressId: 123,
      offererId: 456,
      periodBeginningDate: '2025-01-01',
      periodEndingDate: '2025-12-31',
      status: OfferStatus.PENDING,
      venueId: 789,
    })

    expect(result).toEqual({
      categoryId: 'BOOKS',
      creationMode: 'manual',
      nameOrIsbn: undefined,
      offererAddressId: 123,
      offererId: 456,
      periodBeginningDate: '2025-01-01',
      periodEndingDate: '2025-12-31',
      status: OfferStatus.PENDING,
      venueId: 789,
    })
  })
})
