import { describe, expect, it } from 'vitest'

import { CollectiveLocationType } from '@/apiClient/v1/models/CollectiveLocationType'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'

describe('serializeApiCollectiveFilters', () => {
  it('should set computed fields to null when no filters are provided', () => {
    const result = serializeApiCollectiveFilters({})

    expect(result).toEqual({
      format: null,
      locationType: null,
      offererAddressId: null,
      offererId: null,
      venueId: null,
    })
  })

  it('should coerce offererAddressId, offererId and venueId to numbers', () => {
    const result = serializeApiCollectiveFilters({
      offererAddressId: '123',
      offererId: '456',
      venueId: '789',
    })

    expect(result).toEqual({
      format: null,
      locationType: null,
      offererAddressId: 123,
      offererId: 456,
      venueId: 789,
    })
  })

  it('should handle locationType ADDRESS with and without offererAddressId', () => {
    const withAddress = serializeApiCollectiveFilters({
      locationType: CollectiveLocationType.ADDRESS,
      offererAddressId: '42',
    })
    const withoutAddress = serializeApiCollectiveFilters({
      locationType: CollectiveLocationType.ADDRESS,
    })

    expect(withAddress).toEqual({
      format: null,
      locationType: CollectiveLocationType.ADDRESS,
      offererAddressId: 42,
      offererId: null,
      venueId: null,
    })
    expect(withoutAddress).toEqual({
      format: null,
      locationType: CollectiveLocationType.ADDRESS,
      offererAddressId: null,
      offererId: null,
      venueId: null,
    })
  })

  it('should handle locationType SCHOOL by nulling offererAddressId', () => {
    const result = serializeApiCollectiveFilters({
      locationType: CollectiveLocationType.SCHOOL,
      offererAddressId: '999',
    })

    expect(result).toEqual({
      format: null,
      locationType: CollectiveLocationType.SCHOOL,
      offererAddressId: null,
      offererId: null,
      venueId: null,
    })
  })

  it('should handle locationType TO_BE_DEFINED by nulling offererAddressId', () => {
    const result = serializeApiCollectiveFilters({
      locationType: CollectiveLocationType.TO_BE_DEFINED,
      offererAddressId: '999',
    })

    expect(result).toEqual({
      format: null,
      locationType: CollectiveLocationType.TO_BE_DEFINED,
      offererAddressId: null,
      offererId: null,
      venueId: null,
    })
  })

  it('should ignore unknown locationType values', () => {
    const result = serializeApiCollectiveFilters({
      locationType:
        'UNKNOWN' as unknown as (typeof CollectiveLocationType)[keyof typeof CollectiveLocationType],
    })

    expect(result).toEqual({
      format: null,
      locationType: null,
      offererAddressId: null,
      offererId: null,
      venueId: null,
    })
  })
})
