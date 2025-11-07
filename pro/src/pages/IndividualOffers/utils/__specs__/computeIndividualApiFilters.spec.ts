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

  it('returns defaults with offererId coerced to string and removes page', () => {
    const selectedOffererId = 123
    const result = computeIndividualApiFilters({}, selectedOffererId)

    expect('page' in result).toBe(false)

    expect(result.offererId).toBe('123')

    const expected = {
      ...(DEFAULT_SEARCH_FILTERS as unknown as Record<string, unknown>),
      offererId: '123',
    } as Record<string, unknown>
    delete expected.page
    expect(result).toEqual(expected)

    expect(DEFAULT_SEARCH_FILTERS.page).toBe(DEFAULT_PAGE)
  })

  it('applies overrides from finalSearchFilters and still removes page', () => {
    const selectedOffererId = 5
    const result = computeIndividualApiFilters(
      {
        nameOrIsbn: 'harry',
        creationMode: 'manual',
        periodBeginningDate: '2020-01-01',
        periodEndingDate: '2020-12-31',
        offererAddressId: 'a1',
        page: 7,
      },
      selectedOffererId
    )

    expect('page' in result).toBe(false)

    expect(result).toMatchObject({
      nameOrIsbn: 'harry',
      creationMode: 'manual',
      periodBeginningDate: '2020-01-01',
      periodEndingDate: '2020-12-31',
      offererAddressId: 'a1',
    })

    expect(result.offererId).toBe('5')
  })

  it('selected offererId overrides any provided offererId in finalSearchFilters', () => {
    const result = computeIndividualApiFilters(
      {
        offererId: 'should-not-stick',
      },
      999
    )

    expect(result.offererId).toBe('999')
  })
})
