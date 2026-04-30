import { act, renderHook } from '@testing-library/react'
import { Provider } from 'react-redux'

import type { ListOffersQueryModel } from '@/apiClient/v1/new'
import type {
  CollectiveSearchFiltersParams,
  SearchListParams,
} from '@/commons/core/Offers/types'
import { configureTestStore } from '@/commons/store/testUtils'
import { isEqual } from '@/commons/utils/isEqual'

import { getStoredFilterConfig, useStoredFilterConfig } from './utils'

const renderStoredFilterConfigHook = (venueId = 1) => {
  const store = configureTestStore({
    user: {
      selectedPartnerVenue: { id: venueId } as any,
    } as any,
  })
  const wrapper = ({ children }: { children: any }) => (
    <Provider store={store}>{children}</Provider>
  )
  const { result } = renderHook(() => useStoredFilterConfig('individual'), {
    wrapper,
  })
  return result
}

const MOCKED_FILTERS:
  | (ListOffersQueryModel & SearchListParams)
  | CollectiveSearchFiltersParams = {
  nameOrIsbn: 'nameOrIsbn',
  offererId: 1,
  venueId: 2,
  categoryId: 'categoryId',
  format: 'all',
  creationMode: 'creationMode',
  periodBeginningDate: 'periodBeginningDate',
  periodEndingDate: 'periodEndingDate',
  offererAddressId: 3,
}

describe('getStoredFilterConfig', () => {
  beforeEach(() => {
    window.sessionStorage.clear()
  })

  describe('when session storage is available', () => {
    it('should return the stored filter config', () => {
      const storedValue = {
        filtersVisibility: true,
        storedFilters: MOCKED_FILTERS,
      }
      window.sessionStorage.setItem(
        'INDIVIDUAL_OFFERS_FILTER_CONFIG',
        JSON.stringify(storedValue)
      )

      const { filtersVisibility, storedFilters } =
        getStoredFilterConfig('individual')

      expect(filtersVisibility).toBe(storedValue.filtersVisibility)
      expect(isEqual(storedFilters, storedValue.storedFilters)).toBeTruthy()
    })

    it('should return filtersVisibility=false & an empty object as default in absence of stored filter config', () => {
      const { filtersVisibility, storedFilters } =
        getStoredFilterConfig('individual')

      expect(filtersVisibility).toBe(false)
      expect(isEqual(storedFilters, {})).toBeTruthy()
    })

    it('should return venue-specific stored config when available', () => {
      const storedValue = {
        filtersVisibility: true,
        storedFilters: MOCKED_FILTERS,
        storedVenueId: 'venue-id',
      }
      window.sessionStorage.setItem(
        'INDIVIDUAL_OFFERS_FILTER_CONFIG',
        JSON.stringify(storedValue)
      )

      const { filtersVisibility, storedFilters } = getStoredFilterConfig(
        'individual',
        'venue-id'
      )

      expect(filtersVisibility).toBe(storedValue.filtersVisibility)
      expect(isEqual(storedFilters, storedValue.storedFilters)).toBeTruthy()
    })

    it('should ignore stored config when no venueId is provided but storedVenueId exists', () => {
      const storedValue = {
        filtersVisibility: true,
        storedFilters: MOCKED_FILTERS,
        storedVenueId: 'venue-id',
      }
      window.sessionStorage.setItem(
        'INDIVIDUAL_OFFERS_FILTER_CONFIG',
        JSON.stringify(storedValue)
      )

      const { filtersVisibility, storedFilters } =
        getStoredFilterConfig('individual')

      expect(filtersVisibility).toBe(false)
      expect(isEqual(storedFilters, {})).toBeTruthy()
    })

    it('should switch venue and reset filters when venue changes', () => {
      const result1 = renderStoredFilterConfigHook(1)
      const { onApplyFilters: onApplyFilters1 } = result1.current

      act(() => {
        onApplyFilters1(MOCKED_FILTERS)
      })

      const { storedFilters } = getStoredFilterConfig('individual', 1)
      expect(isEqual(storedFilters, MOCKED_FILTERS)).toBeTruthy()

      const { storedFilters: filtersForVenue2 } = getStoredFilterConfig(
        'individual',
        2
      )

      expect(isEqual(filtersForVenue2, {})).toBeTruthy()

      const { storedFilters: filtersAfterVenueChange } = getStoredFilterConfig(
        'individual',
        1
      )
      expect(isEqual(filtersAfterVenueChange, {})).toBeTruthy()
    })
  })

  describe('when session storage is not available', () => {
    it('should return an empty object as stored filter config', () => {
      vi.spyOn(window.sessionStorage.__proto__, 'getItem').mockImplementation(
        () => {
          throw new DOMException()
        }
      )

      const { filtersVisibility, storedFilters } =
        getStoredFilterConfig('individual')

      expect(filtersVisibility).toBe(false)
      expect(isEqual(storedFilters, {})).toBeTruthy()
    })
  })
})

describe('useStoredFilterConfig', () => {
  afterEach(() => {
    window.sessionStorage.clear()
  })

  describe('onFiltersToggle', () => {
    it('should store the new filters visibility', () => {
      const result = renderStoredFilterConfigHook()
      const { onFiltersToggle } = result.current

      act(() => {
        onFiltersToggle(true)
      })

      const { filtersVisibility } = getStoredFilterConfig('individual', 1)
      expect(filtersVisibility).toBe(true)
    })

    it('should expose filtersVisibility from session storage for the current venue', () => {
      const storedValue = {
        filtersVisibility: true,
        storedFilters: MOCKED_FILTERS,
        storedVenueId: 1,
      }
      window.sessionStorage.setItem(
        'INDIVIDUAL_OFFERS_FILTER_CONFIG',
        JSON.stringify(storedValue)
      )

      const result = renderStoredFilterConfigHook(1)
      expect(result.current.filtersVisibility).toBe(true)
    })
  })

  describe('onApplyFilters', () => {
    it('should store the new selected filters', () => {
      const result = renderStoredFilterConfigHook()
      const { onApplyFilters } = result.current

      act(() => {
        onApplyFilters(MOCKED_FILTERS)
      })

      const { storedFilters } = getStoredFilterConfig('individual', 1)
      expect(isEqual(storedFilters, MOCKED_FILTERS)).toBeTruthy()
    })
  })

  describe('onResetFilters', () => {
    it('should reset the stored filters', () => {
      const result = renderStoredFilterConfigHook()
      const { onResetFilters } = result.current

      act(() => {
        onResetFilters()
      })

      const { storedFilters } = getStoredFilterConfig('individual', 1)
      expect(isEqual(storedFilters, {})).toBeTruthy()
    })
  })
})
