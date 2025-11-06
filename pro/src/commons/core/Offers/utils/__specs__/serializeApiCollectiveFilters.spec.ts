import { describe, expect, it } from 'vitest'

import { CollectiveOfferDisplayedStatus } from '@/apiClient/v1'
import { CollectiveLocationType } from '@/apiClient/v1/models/CollectiveLocationType'
import { DEFAULT_COLLECTIVE_SEARCH_FILTERS } from '@/commons/core/Offers/constants'
import { CollectiveOfferTypeEnum } from '@/commons/core/Offers/types'
import { serializeApiCollectiveFilters } from '@/commons/core/Offers/utils/serializeApiCollectiveFilters'

describe('serializeApiCollectiveFilters', () => {
  it('should set venueId to undefined and otherwise return empty when no filters provided', () => {
    const result = serializeApiCollectiveFilters(
      {},
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )

    expect(result).toEqual({ venueId: undefined })
  })

  it('should include non-default simple fields and omit defaults', () => {
    const result = serializeApiCollectiveFilters(
      {
        nameOrIsbn: 'Projet Arts',
        collectiveOfferType: CollectiveOfferTypeEnum.TEMPLATE, // default is ALL
        // equal to default -> omitted
        format: DEFAULT_COLLECTIVE_SEARCH_FILTERS.format,
      },
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )

    expect(result).toMatchObject({
      nameOrIsbn: 'Projet Arts',
      collectiveOfferType: CollectiveOfferTypeEnum.TEMPLATE,
    })
    expect(result.venueId).toBeUndefined()
    expect('format' in result).toBe(false)
  })

  it('should coerce offererAddressId to number via general branch when provided without locationType', () => {
    const result = serializeApiCollectiveFilters(
      { offererAddressId: '123' },
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )

    expect(result).toEqual({ offererAddressId: 123, venueId: undefined })
  })

  it('should include status array when it differs from default empty array', () => {
    const result = serializeApiCollectiveFilters(
      { status: [CollectiveOfferDisplayedStatus.PUBLISHED] },
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )

    expect(result).toEqual({
      status: [CollectiveOfferDisplayedStatus.PUBLISHED],
      venueId: undefined,
    })
  })

  it('should not include status when equal to default (empty array)', () => {
    const result = serializeApiCollectiveFilters(
      { status: [] },
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )

    expect(result).toEqual({ venueId: undefined })
  })

  it('should handle locationType ADDRESS with and without offererAddressId', () => {
    const withAddress = serializeApiCollectiveFilters(
      { locationType: CollectiveLocationType.ADDRESS, offererAddressId: '42' },
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )
    const withoutAddress = serializeApiCollectiveFilters(
      { locationType: CollectiveLocationType.ADDRESS },
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )

    expect(withAddress).toEqual({
      locationType: CollectiveLocationType.ADDRESS,
      offererAddressId: 42,
      venueId: undefined,
    })
    expect(withoutAddress).toEqual({
      locationType: CollectiveLocationType.ADDRESS,
      offererAddressId: null,
      venueId: undefined,
    })
  })

  it('should handle locationType SCHOOL by nulling offererAddressId', () => {
    const result = serializeApiCollectiveFilters(
      { locationType: CollectiveLocationType.SCHOOL, offererAddressId: '999' },
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )

    expect(result).toEqual({
      locationType: CollectiveLocationType.SCHOOL,
      offererAddressId: null,
      venueId: undefined,
    })
  })

  it('should handle locationType TO_BE_DEFINED by nulling offererAddressId', () => {
    const result = serializeApiCollectiveFilters(
      {
        locationType: CollectiveLocationType.TO_BE_DEFINED,
        offererAddressId: '999',
      },
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )

    expect(result).toEqual({
      locationType: CollectiveLocationType.TO_BE_DEFINED,
      offererAddressId: null,
      venueId: undefined,
    })
  })

  it('should ignore unknown locationType values', () => {
    const result = serializeApiCollectiveFilters(
      {
        locationType:
          'UNKNOWN' as unknown as (typeof CollectiveLocationType)[keyof typeof CollectiveLocationType],
      },
      DEFAULT_COLLECTIVE_SEARCH_FILTERS
    )

    expect(result).toEqual({ venueId: undefined })
  })
})
