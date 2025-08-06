import { act, renderHook } from '@testing-library/react'
import { Provider } from 'react-redux'

import { configureTestStore } from '@/commons/store/testUtils'
import { isEqual } from '@/commons/utils/isEqual'

import {
  getStoredFilterConfig,
  SelectedFilters,
  useStoredFilterConfig,
} from './utils'

const renderStoredFilterConfigHook = () => {
  const store = configureTestStore({})
  const wrapper = ({ children }: { children: any }) => (
    <Provider store={store}>{children}</Provider>
  )
  const { result } = renderHook(() => useStoredFilterConfig('individual'), {
    wrapper,
  })
  return result
}

const MOCKED_FILTERS: SelectedFilters = {
  nameOrIsbn: 'nameOrIsbn',
  offererId: 'offererId',
  venueId: 'venueId',
  categoryId: 'categoryId',
  status: 'all',
  creationMode: 'creationMode',
  periodBeginningDate: 'periodBeginningDate',
  periodEndingDate: 'periodEndingDate',
  offererAddressId: 'offererAddressId',
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

      const { filtersVisibility } = getStoredFilterConfig('individual')
      expect(filtersVisibility).toBe(true)
    })
  })

  describe('onApplyFilters', () => {
    it('should store the new selected filters, without offererId', () => {
      const result = renderStoredFilterConfigHook()
      const { onApplyFilters } = result.current

      act(() => {
        onApplyFilters(MOCKED_FILTERS)
      })

      const { storedFilters } = getStoredFilterConfig('individual')
      expect(isEqual(storedFilters, MOCKED_FILTERS)).toBeFalsy()
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      const { offererId: _offererId, ...expectedFilters } = MOCKED_FILTERS
      expect(isEqual(storedFilters, expectedFilters)).toBeTruthy()
    })
  })

  describe('onResetFilters', () => {
    it('should reset the stored filters', () => {
      const result = renderStoredFilterConfigHook()
      const { onResetFilters } = result.current

      act(() => {
        onResetFilters()
      })

      const { storedFilters } = getStoredFilterConfig('individual')
      expect(isEqual(storedFilters, {})).toBeTruthy()
    })
  })
})
