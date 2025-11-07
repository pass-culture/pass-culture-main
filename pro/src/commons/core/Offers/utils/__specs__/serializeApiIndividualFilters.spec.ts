import { describe, expect, it } from 'vitest'

import { OfferStatus } from '@/apiClient/v1'
import { serializeApiIndividualFilters } from '@/commons/core/Offers/utils/serializeApiIndividualFilters'

describe('serializeApiIndividualFilters', () => {
  it('should set computed fields to null when no filters are provided', () => {
    const result = serializeApiIndividualFilters({})

    expect(result).toEqual({
      offererAddressId: null,
      offererId: null,
      status: null,
      venueId: null,
    })
  })

  it('should compute all entries as expected', () => {
    const result = serializeApiIndividualFilters({
      categoryId: 'BOOKS',
      creationMode: 'manual',
      offererAddressId: '123',
      offererId: '456',
      periodBeginningDate: '2025-01-01',
      periodEndingDate: '2025-12-31',
      status: OfferStatus.PENDING,
      venueId: '789',
    })

    expect(result).toMatchObject({
      categoryId: 'BOOKS',
      creationMode: 'manual',
      offererAddressId: 123,
      offererId: 456,
      periodBeginningDate: '2025-01-01',
      periodEndingDate: '2025-12-31',
      status: OfferStatus.PENDING,
      venueId: 789,
    })

    expect('nameOrIsbn' in result).toBe(false)
  })
})
