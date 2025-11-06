import { describe, expect, it } from 'vitest'

import { OfferStatus } from '@/apiClient/v1'
import { DEFAULT_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { serializeApiFilters } from '@/commons/core/Offers/utils/serializeApiFilters'

describe('serializeApiFilters', () => {
  it('should return an empty object when no filters are provided', () => {
    const result = serializeApiFilters({})

    expect(result).toEqual({})
  })

  it('should include only whitelisted keys that differ from defaults', () => {
    const result = serializeApiFilters({
      // truthy and different from default (default ""), should be included
      nameOrIsbn: 'Le Petit Prince',
      // equal to default, should be omitted
      offererId: DEFAULT_SEARCH_FILTERS.offererId,
    })

    expect(result).toEqual({ nameOrIsbn: 'Le Petit Prince' })
  })

  it('should omit falsy values even if different from defaults', () => {
    const result = serializeApiFilters({
      // default is 'all' but provided value is '', which is falsy -> omitted
      categoryId: '',
      // default is '' and provided is '' (falsy) -> omitted
      nameOrIsbn: '',
    })

    expect(result).toEqual({})
  })

  it('should include multiple non-default values unchanged', () => {
    const result = serializeApiFilters({
      status: OfferStatus.PENDING,
      creationMode: 'manual',
      periodBeginningDate: '2025-01-01',
      periodEndingDate: '2025-12-31',
      offererAddressId: '123',
      categoryId: 'BOOKS',
      collectiveOfferType: 'offer',
      offererId: 'off_42',
      venueId: 'v_99',
    })

    expect(result).toMatchObject({
      status: OfferStatus.PENDING,
      creationMode: 'manual',
      periodBeginningDate: '2025-01-01',
      periodEndingDate: '2025-12-31',
      offererAddressId: '123',
      categoryId: 'BOOKS',
      collectiveOfferType: 'offer',
      offererId: 'off_42',
      venueId: 'v_99',
    })

    expect('nameOrIsbn' in result).toBe(false)
  })
})
