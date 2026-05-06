import { act } from '@testing-library/react'
import type { RouteObject } from 'react-router'

import { BookingStatusFilter } from '@/apiClient/v1/new'
import { DEFAULT_PRE_FILTERS } from '@/commons/core/Bookings/constants'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { useBookingsFilters } from './useBookingsFilters'

vi.mock('@/commons/utils/date', async () => ({
  ...(await vi.importActual('@/commons/utils/date')),
  getToday: vi.fn().mockReturnValue(new Date('2020-06-15T12:00:00Z')),
}))

type HookReturn = ReturnType<typeof useBookingsFilters>

let hookResult: HookReturn

function HookConsumer() {
  hookResult = useBookingsFilters()

  return (
    <div data-testid="hook-output">
      <span data-testid="bookingBeginningDate">
        {hookResult.selectedPreFilters.bookingBeginningDate}
      </span>
      <span data-testid="bookingEndingDate">
        {hookResult.selectedPreFilters.bookingEndingDate}
      </span>
      <span data-testid="bookingStatusFilter">
        {hookResult.selectedPreFilters.bookingStatusFilter}
      </span>
      <span data-testid="offerEventDate">
        {hookResult.selectedPreFilters.offerEventDate}
      </span>
      <span data-testid="offererAddressId">
        {hookResult.selectedPreFilters.offererAddressId}
      </span>
      <span data-testid="hasPreFilters">
        {String(hookResult.hasPreFilters)}
      </span>
      <span data-testid="isRefreshRequired">
        {String(hookResult.isRefreshRequired)}
      </span>
      <span data-testid="wereBookingsRequested">
        {String(hookResult.wereBookingsRequested)}
      </span>
    </div>
  )
}

function renderHook(initialRouterEntries: string[] = ['/test']) {
  const routes: RouteObject[] = [
    {
      path: '/test',
      id: 'test',
      element: <HookConsumer />,
    },
  ]

  return renderWithProviders(null, { routes, initialRouterEntries })
}

describe('useBookingsFilters', () => {
  describe('selectedPreFilters initialization', () => {
    it('should initialize selectedPreFilters from DEFAULT_PRE_FILTERS', () => {
      renderHook()

      expect(hookResult.selectedPreFilters.bookingStatusFilter).toBe(
        BookingStatusFilter.BOOKED
      )
    })

    it('should initialize with default dates', () => {
      renderHook()

      expect(hookResult.selectedPreFilters.bookingBeginningDate).toBe(
        DEFAULT_PRE_FILTERS.bookingBeginningDate
      )
      expect(hookResult.selectedPreFilters.bookingEndingDate).toBe(
        DEFAULT_PRE_FILTERS.bookingEndingDate
      )
    })
  })

  describe('URL params synchronization', () => {
    it('should read filters from URL search params on mount', () => {
      renderHook([
        '/test?bookingStatusFilter=validated&bookingBeginningDate=2020-01-01&bookingEndingDate=2020-06-01',
      ])

      expect(hookResult.selectedPreFilters.bookingStatusFilter).toBe(
        BookingStatusFilter.VALIDATED
      )
      expect(hookResult.selectedPreFilters.bookingBeginningDate).toBe(
        '2020-01-01'
      )
      expect(hookResult.selectedPreFilters.bookingEndingDate).toBe('2020-06-01')
    })

    it('should read offererAddressId from URL', () => {
      renderHook(['/test?offererAddressId=77&bookingStatusFilter=booked'])

      expect(hookResult.selectedPreFilters.offererAddressId).toBe('77')
    })

    it('should clear booking dates when URL has offerEventDate but no booking dates', () => {
      renderHook(['/test?offerEventDate=2020-06-10'])

      expect(hookResult.selectedPreFilters.offerEventDate).toBe('2020-06-10')
      expect(hookResult.selectedPreFilters.bookingBeginningDate).toBe('')
      expect(hookResult.selectedPreFilters.bookingEndingDate).toBe('')
    })

    it('should keep booking dates from URL when both offerEventDate and dates are present', () => {
      renderHook([
        '/test?offerEventDate=2020-06-10&bookingBeginningDate=2020-01-01&bookingEndingDate=2020-06-01',
      ])

      expect(hookResult.selectedPreFilters.offerEventDate).toBe('2020-06-10')
      expect(hookResult.selectedPreFilters.bookingBeginningDate).toBe(
        '2020-01-01'
      )
      expect(hookResult.selectedPreFilters.bookingEndingDate).toBe('2020-06-01')
    })

    it('should fallback invalid bookingStatusFilter to default', () => {
      renderHook(['/test?bookingStatusFilter=invalid_value'])

      expect(hookResult.selectedPreFilters.bookingStatusFilter).toBe(
        DEFAULT_PRE_FILTERS.bookingStatusFilter
      )
    })

    it('should not apply URL overrides when no recognized params are in URL', () => {
      renderHook(['/test?unrelated=true'])

      expect(hookResult.selectedPreFilters).toEqual(DEFAULT_PRE_FILTERS)
    })
  })

  describe('updateSelectedFilters', () => {
    it('should update a single filter', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({
          bookingStatusFilter: BookingStatusFilter.REIMBURSED,
        })
      })

      expect(hookResult.selectedPreFilters.bookingStatusFilter).toBe(
        BookingStatusFilter.REIMBURSED
      )
    })

    it('should clear booking dates when offerEventDate is updated to a new value', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({ offerEventDate: '2020-06-10' })
      })

      expect(hookResult.selectedPreFilters.offerEventDate).toBe('2020-06-10')
      expect(hookResult.selectedPreFilters.bookingBeginningDate).toBe('')
      expect(hookResult.selectedPreFilters.bookingEndingDate).toBe('')
    })

    it('should restore booking dates when offerEventDate matches the applied value', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({ offerEventDate: '2020-06-10' })
      })

      expect(hookResult.selectedPreFilters.bookingBeginningDate).toBe('')

      act(() => {
        hookResult.updateSelectedFilters({
          offerEventDate: DEFAULT_PRE_FILTERS.offerEventDate,
        })
      })

      expect(hookResult.selectedPreFilters.bookingBeginningDate).toBe(
        DEFAULT_PRE_FILTERS.bookingBeginningDate
      )
      expect(hookResult.selectedPreFilters.bookingEndingDate).toBe(
        DEFAULT_PRE_FILTERS.bookingEndingDate
      )
    })

    it('should preserve other filters when updating one', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({
          bookingBeginningDate: '2020-01-01',
        })
      })

      expect(hookResult.selectedPreFilters.bookingStatusFilter).toBe(
        BookingStatusFilter.BOOKED
      )
      expect(hookResult.selectedPreFilters.bookingBeginningDate).toBe(
        '2020-01-01'
      )
    })
  })

  describe('hasPreFilters', () => {
    it('should be false when selectedPreFilters match defaults', () => {
      renderHook()

      expect(hookResult.hasPreFilters).toBe(false)
    })

    it('should be true when a non-date filter differs', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({
          bookingStatusFilter: BookingStatusFilter.VALIDATED,
        })
      })

      expect(hookResult.hasPreFilters).toBe(true)
    })

    it('should be true when a date filter differs', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({
          bookingBeginningDate: '2020-01-01',
        })
      })

      expect(hookResult.hasPreFilters).toBe(true)
    })

    it('should be false after resetPreFilters', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({
          bookingStatusFilter: BookingStatusFilter.VALIDATED,
        })
      })

      expect(hookResult.hasPreFilters).toBe(true)

      act(() => {
        hookResult.resetPreFilters()
      })

      expect(hookResult.hasPreFilters).toBe(false)
    })
  })

  describe('isRefreshRequired', () => {
    it('should be false initially', () => {
      renderHook()

      expect(hookResult.isRefreshRequired).toBe(false)
    })

    it('should be false when filters changed but bookings were never requested', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({
          bookingStatusFilter: BookingStatusFilter.VALIDATED,
        })
      })

      expect(hookResult.isRefreshRequired).toBe(false)
    })

    it('should be true when filters changed after bookings were requested', () => {
      renderHook()

      act(() => {
        hookResult.applyNow()
      })

      act(() => {
        hookResult.updateSelectedFilters({
          bookingStatusFilter: BookingStatusFilter.VALIDATED,
        })
      })

      expect(hookResult.isRefreshRequired).toBe(true)
    })

    it('should be false after applyNow syncs filters', () => {
      renderHook()

      act(() => {
        hookResult.applyNow()
      })

      act(() => {
        hookResult.updateSelectedFilters({
          bookingStatusFilter: BookingStatusFilter.VALIDATED,
        })
      })

      expect(hookResult.isRefreshRequired).toBe(true)

      act(() => {
        hookResult.applyNow()
      })

      expect(hookResult.isRefreshRequired).toBe(false)
    })
  })

  describe('applyNow', () => {
    it('should synchronize appliedPreFilters with selectedPreFilters', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({
          bookingStatusFilter: BookingStatusFilter.VALIDATED,
        })
      })

      expect(hookResult.appliedPreFilters.bookingStatusFilter).toBe(
        BookingStatusFilter.BOOKED
      )

      act(() => {
        hookResult.applyNow()
      })

      expect(hookResult.appliedPreFilters.bookingStatusFilter).toBe(
        BookingStatusFilter.VALIDATED
      )
    })
  })

  describe('resetPreFilters', () => {
    it('should reset all filters to defaults', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({
          bookingStatusFilter: BookingStatusFilter.VALIDATED,
          bookingBeginningDate: '2020-01-01',
        })
        hookResult.applyNow()
      })

      act(() => {
        hookResult.resetPreFilters()
      })

      expect(hookResult.selectedPreFilters).toEqual(DEFAULT_PRE_FILTERS)
      expect(hookResult.appliedPreFilters).toEqual(DEFAULT_PRE_FILTERS)
      expect(hookResult.wereBookingsRequested).toBe(false)
    })
  })

  describe('applyNow URL navigation', () => {
    it('should include non-default filters in urlParams after applyNow', () => {
      renderHook()

      act(() => {
        hookResult.updateSelectedFilters({
          bookingStatusFilter: BookingStatusFilter.VALIDATED,
          bookingBeginningDate: '2020-03-01',
          bookingEndingDate: '2020-06-15',
        })
      })

      act(() => {
        hookResult.applyNow()
      })

      expect(hookResult.urlParams.bookingStatusFilter).toBe(
        BookingStatusFilter.VALIDATED
      )
    })
  })
})
