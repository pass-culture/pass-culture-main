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

  it('returns defaults with offererId set to selected offerer and removes page', () => {
    const selectedVenueId = 123
    const result = computeIndividualApiFilters({}, selectedVenueId)

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
    const result = computeIndividualApiFilters(
      {
        nameOrIsbn: 'harry',
        creationMode: 'manual',
        periodBeginningDate: '2020-01-01',
        periodEndingDate: '2020-12-31',
        offererAddressId: 1,
        page: 7,
      },
      selectedVenueId
    )

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

  it('selected offererId overrides any provided offererId in finalSearchFilters', () => {
    const result = computeIndividualApiFilters(
      {
        venueId: 42,
      },
      999
    )

    expect(result.venueId).toBe(999)
  })
})
