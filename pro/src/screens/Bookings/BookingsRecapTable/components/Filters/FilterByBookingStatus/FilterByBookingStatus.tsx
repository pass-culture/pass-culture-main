import React, { ChangeEvent, useEffect, useRef, useState } from 'react'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { Events } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared'
import useAnalytics from 'hooks/useAnalytics'
import useOnClickOrFocusOutside from 'hooks/useOnClickOrFocusOutside'
import Icon from 'ui-kit/Icon/Icon'

import { BookingsFilters } from '../../../types'
import {
  getBookingStatusDisplayInformations,
  getCollectiveBookingStatusDisplayInformations,
} from '../../../utils/bookingStatusConverter'

function getAvailableBookingStatuses<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>(audience: Audience, bookingsRecap: T[]) {
  const titleFormatter =
    audience === Audience.INDIVIDUAL
      ? getBookingStatusDisplayInformations
      : getCollectiveBookingStatusDisplayInformations
  const presentBookingStatues = Array.from(
    new Set(bookingsRecap.map(bookingRecap => bookingRecap.bookingStatus))
  ).map(bookingStatus => ({
    title: titleFormatter(bookingStatus)?.status ?? '',
    value: bookingStatus,
  }))

  const byStatusTitle = (
    bookingStatusA: { title: string; value: string },
    bookingStatusB: { title: string; value: string }
  ) => {
    const titleA = bookingStatusA.title
    const titleB = bookingStatusB.title
    return titleA < titleB ? -1 : titleA > titleB ? 1 : 0
  }

  return presentBookingStatues.sort(byStatusTitle)
}

export interface FilterByBookingStatusProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
> {
  bookingStatuses: string[]
  bookingsRecap: T[]
  updateGlobalFilters: (filters: Partial<BookingsFilters>) => void
  audience: Audience
}

const FilterByBookingStatus = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel
>({
  bookingStatuses,
  bookingsRecap,
  updateGlobalFilters,
  audience,
}: FilterByBookingStatusProps<T>) => {
  const [bookingStatusFilters, setBookingStatusFilters] =
    useState(bookingStatuses)
  const [isToolTipVisible, setIsToolTipVisible] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const { logEvent } = useAnalytics()

  function showFilter() {
    setIsToolTipVisible(true)
    logEvent?.(Events.CLICKED_SHOW_STATUS_FILTER, {
      from: location.pathname,
    })
  }

  function hideFilters() {
    setIsToolTipVisible(false)
  }

  useOnClickOrFocusOutside(containerRef, hideFilters)

  function handleCheckboxChange(event: ChangeEvent<HTMLInputElement>) {
    const statusId = event.target.name
    const isSelected = event.target.checked

    if (!isSelected) {
      setBookingStatusFilters(previousFilters => [...previousFilters, statusId])
    } else {
      setBookingStatusFilters(previousFilters =>
        previousFilters.filter(el => el !== statusId)
      )
    }
  }

  useEffect(() => {
    updateGlobalFilters({
      bookingStatus: bookingStatusFilters,
    })
  }, [bookingStatusFilters, updateGlobalFilters])

  const computeIconSrc = () => {
    if (bookingStatusFilters.length > 0) {
      return 'ico-filter-status-active'
    } else if (isToolTipVisible) {
      return 'ico-filter-status-red'
    } else {
      return 'ico-filter-status-black'
    }
  }

  const filteredBookingStatuses = getAvailableBookingStatuses(
    audience,
    bookingsRecap
  )

  return (
    <div ref={containerRef}>
      <button
        className="bs-filter-button"
        onClick={showFilter}
        onFocus={showFilter}
        type="button"
      >
        <span className="table-head-label status-filter">Statut</span>

        <Icon alt="Filtrer par statut" svg={computeIconSrc()} />
      </button>
      <span className="bs-filter">
        {isToolTipVisible && (
          <div className="bs-filter-tooltip">
            <div className="bs-filter-label">Afficher les offres</div>
            {filteredBookingStatuses.map(bookingStatus => (
              <label key={bookingStatus.value}>
                <input
                  checked={!bookingStatusFilters.includes(bookingStatus.value)}
                  id={`bs-${bookingStatus.value}`}
                  name={bookingStatus.value}
                  onChange={handleCheckboxChange}
                  type="checkbox"
                />
                {bookingStatus.title}
              </label>
            ))}
          </div>
        )}
      </span>
    </div>
  )
}

export default FilterByBookingStatus
