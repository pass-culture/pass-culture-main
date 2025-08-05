import {
  BookingRecapResponseModel,
  CollectiveBookingResponseModel,
} from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import cn from 'classnames'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { Audience } from 'commons/core/shared/types'
import { useOnClickOrFocusOutside } from 'commons/hooks/useOnClickOrFocusOutside'
import { Checkbox } from 'design-system/Checkbox/Checkbox'
import fullSortIcon from 'icons/full-sort.svg'
import React, { ChangeEvent, useRef, useState } from 'react'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { BookingsFilters } from '../types'
import {
  COLLECTIVE_BOOKING_STATUS_DISPLAY_INFORMATIONS,
  INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS,
} from '../utils/bookingStatusConverter'

import styles from './Filters.module.scss'

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

  const handleCheckboxChange = (
    event: ChangeEvent<HTMLInputElement>,
    checkboxId: string
  ) => {
    const isSelected = event.target.checked

    if (!isSelected) {
      updateGlobalFilters({
        bookingStatus: [...bookingStatuses, checkboxId],
      })
    } else {
      updateGlobalFilters({
        bookingStatus: bookingStatuses.filter((el) => el !== checkboxId),
      })
    }
  }

  const bookingStatusOptions = getAvailableBookingStatuses(audience)

  return (
    <div ref={containerRef}>
      <button
        className={styles['bs-filter-button']}
        onClick={toggleTooltip}
        onKeyDown={handleKeyDown}
        type="button"
        aria-expanded={isToolTipVisible}
        aria-controls="booking-filter-tooltip"
      >
        <span
          className={cn(styles['table-head-label'], styles['status-filter'])}
        >
          Statut
        </span>
        <span className={styles['status-container']}>
          <SvgIcon
            alt="Filtrer par statut"
            src={fullSortIcon}
            className={cn(
              styles['status-icon'],
              (bookingStatuses.length > 0 || isToolTipVisible) &&
                styles['active']
            )}
          />
          {bookingStatuses.length > 0 && <span className="status-badge-icon" />}
        </span>
      </button>
      <div className={styles['bs-filter']} id="booking-filter-tooltip">
        {isToolTipVisible && (
          <div className={styles['bs-filter-tooltip']}>
            <fieldset>
              <legend className={styles['bs-filter-legend']}>
                Afficher les réservations
              </legend>
              <div className={styles['bs-filter-checkboxes']}>
                {bookingStatusOptions.map((bookingStatus) => (
                  <Checkbox
                    variant="default"
                    key={bookingStatus.value}
                    checked={!bookingStatuses.includes(bookingStatus.value)}
                    onChange={(e) =>
                      handleCheckboxChange(e, bookingStatus.value)
                    }
                    label={bookingStatus.title}
                  />
                ))}
              </div>
            </fieldset>
          </div>
        )}
      </div>
    </div>
  )
}
