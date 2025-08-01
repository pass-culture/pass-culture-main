import * as utils from 'components/OffersTable/OffersTableSearch/utils'

import { getFinalSearchFilters } from './getFinalSearchFilters'

describe('getFinalSearchFilters', () => {
  beforeEach(() => {
    vi.spyOn(utils, 'getStoredFilterConfig').mockReturnValue({
      storedFilters: { nameOrIsbn: 'Mon offre' },
      filtersVisibility: false,
    })
  })

  it('should add the session storage filters to the url filters when the FF WIP_COLLAPSED_MEMORIZED_FILTERS is active', () => {
    expect(getFinalSearchFilters({}, true)).toEqual({ nameOrIsbn: 'Mon offre' })
  })

  it('should add the session storage filters to the url filters when the FF WIP_COLLAPSED_MEMORIZED_FILTERS is inactive', () => {
    expect(getFinalSearchFilters({}, false)).toEqual({})
  })
})
