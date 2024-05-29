import cn from 'classnames'
import React, { ChangeEvent, useRef, useState } from 'react'

import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { Events } from 'core/FirebaseEvents/constants'
import { Audience } from 'core/shared/types'
import { useOnClickOrFocusOutside } from 'hooks/useOnClickOrFocusOutside'
import fullSortIcon from 'icons/full-sort.svg'
import { BaseCheckbox } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { BookingsFilters } from '../types'
import {
  INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS,
  COLLECTIVE_BOOKING_STATUS_DISPLAY_INFORMATIONS,
} from '../utils/bookingStatusConverter'

const getAvailableBookingStatuses = (audience: Audience) => {
  const statuses =
    audience === Audience.INDIVIDUAL
      ? INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS
      : COLLECTIVE_BOOKING_STATUS_DISPLAY_INFORMATIONS

  const statusOptions = statuses.map((bookingStatus) => ({
    title: bookingStatus.status,
    value: bookingStatus.id,
  }))

  const byStatusTitle = (
    bookingStatusA: { title: string; value: string },
    bookingStatusB: { title: string; value: string }
  ) => {
    const titleA = bookingStatusA.title
    const titleB = bookingStatusB.title
    return titleA < titleB ? -1 : titleA > titleB ? 1 : 0
  }

  return statusOptions.sort(byStatusTitle)
}

export interface FilterByBookingStatusProps<
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
> {
  bookingStatuses: string[]
  bookingsRecap: T[]
  updateGlobalFilters: (filters: Partial<BookingsFilters>) => void
  audience: Audience
}

export const FilterByBookingStatus = <
  T extends BookingRecapResponseModel | CollectiveBookingResponseModel,
>({
  bookingStatuses,
  updateGlobalFilters,
  audience,
}: FilterByBookingStatusProps<T>) => {
  const [isToolTipVisible, setIsToolTipVisible] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const { logEvent } = useAnalytics()

  const showTooltip = () => {
    setIsToolTipVisible(true)
    logEvent(Events.CLICKED_SHOW_STATUS_FILTER, {
      from: location.pathname,
    })
  }

  const hideTooltip = () => {
    setIsToolTipVisible(false)
  }

  function toggleTooltip() {
    if (isToolTipVisible) {
      hideTooltip()
    } else {
      showTooltip()
    }
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLButtonElement>) {
    switch (event.key) {
      case 'Space':
        toggleTooltip()
        break
      case 'Escape':
        hideTooltip()
        break
    }
  }

  useOnClickOrFocusOutside(containerRef, hideTooltip)

  const handleCheckboxChange = (event: ChangeEvent<HTMLInputElement>) => {
    const statusId = event.target.name
    const isSelected = event.target.checked

    if (!isSelected) {
      updateGlobalFilters({
        bookingStatus: [...bookingStatuses, statusId],
      })
    } else {
      updateGlobalFilters({
        bookingStatus: bookingStatuses.filter((el) => el !== statusId),
      })
    }
  }

  const bookingStatusOptions = getAvailableBookingStatuses(audience)

  return (
    <div ref={containerRef}>
      <button
        className="bs-filter-button"
        onClick={toggleTooltip}
        onKeyDown={handleKeyDown}
        type="button"
        aria-expanded={isToolTipVisible}
        aria-controls="booking-filter-tooltip"
      >
        <span className="table-head-label status-filter">Statut</span>
        <span className="status-container">
          <SvgIcon
            alt="Filtrer par statut"
            src={fullSortIcon}
            className={cn(
              'status-icon',
              (bookingStatuses.length > 0 || isToolTipVisible) && 'active'
            )}
          />
          {bookingStatuses.length > 0 && <span className="status-badge-icon" />}
        </span>
      </button>
      <div className="bs-filter" id="booking-filter-tooltip">
        {isToolTipVisible && (
          <div className="bs-filter-tooltip">
            <fieldset>
              <legend className="bs-filter-label">
                Afficher les réservations
              </legend>

              {bookingStatusOptions.map((bookingStatus) => (
                <BaseCheckbox
                  key={bookingStatus.value}
                  checked={!bookingStatuses.includes(bookingStatus.value)}
                  id={`bs-${bookingStatus.value}`}
                  name={bookingStatus.value}
                  onChange={handleCheckboxChange}
                  label={bookingStatus.title}
                />
              ))}
            </fieldset>
          </div>
        )}
      </div>
    </div>
  )
}
