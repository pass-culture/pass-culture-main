import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  DEFAULT_PAGE,
  DEFAULT_SEARCH_FILTERS,
} from '@/commons/core/Offers/constants'

import { computeIndividualApiFilters } from '../computeIndividualApiFilters'

describe('computeIndividualApiFilters', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  it('returns defaults with venueId set to selected venue and removes page', () => {
    const selectedVenueId = 123
    const result = computeIndividualApiFilters({
      finalSearchFilters: {},
      selectedVenueId,
    })

    expect('page' in result).toBe(false)
    expect(result.venueId).toBe(123)

    const expected = {
      ...(DEFAULT_SEARCH_FILTERS as unknown as Record<string, unknown>),
      venueId: 123,
    } as Record<string, unknown>
    delete expected.page
    expect(result).toEqual(expected)

    expect(DEFAULT_SEARCH_FILTERS.page).toBe(DEFAULT_PAGE)
  })

  it('applies overrides from finalSearchFilters and still removes page', () => {
    const selectedVenueId = 5
    const result = computeIndividualApiFilters({
      finalSearchFilters: {
        nameOrIsbn: 'harry',
        creationMode: 'manual',
        periodBeginningDate: '2020-01-01',
        periodEndingDate: '2020-12-31',
        offererAddressId: 1,
        page: 7,
      },
      selectedVenueId,
    })

    expect('page' in result).toBe(false)

    expect(result).toMatchObject({
      nameOrIsbn: 'harry',
      creationMode: 'manual',
      periodBeginningDate: '2020-01-01',
      periodEndingDate: '2020-12-31',
      offererAddressId: 1,
    })

    expect(result.venueId).toBe(5)
  })

  it('selected venueId overrides any provided venueId in finalSearchFilters', () => {
    const result = computeIndividualApiFilters({
      finalSearchFilters: {
        venueId: 42,
      },
      selectedVenueId: 999,
    })

    expect(result.venueId).toBe(999)
  })
})
