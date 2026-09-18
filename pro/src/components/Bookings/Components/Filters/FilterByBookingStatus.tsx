import cn from 'classnames'
import type React from 'react'
import { type ChangeEvent, useId, useRef, useState } from 'react'

import { useAnalytics } from '@/app/App/analytics/firebase'
import { Events } from '@/commons/core/FirebaseEvents/constants'
import { useOnClickOrFocusOutside } from '@/commons/hooks/useOnClickOrFocusOutside'
import { pluralizeFr } from '@/commons/utils/pluralize'
import { Checkbox } from '@/design-system/Checkbox/Checkbox'
import fullSortIcon from '@/icons/full-sort.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import type { BookingsFilters } from '../types'
import { INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS } from '../utils/bookingStatusConverter'
import styles from './Filters.module.scss'

export interface FilterByBookingStatusProps {
  bookingStatuses: string[]
  updateGlobalFilters: (filters: Partial<BookingsFilters>) => void
}

export const FilterByBookingStatus = ({
  bookingStatuses,
  updateGlobalFilters,
}: FilterByBookingStatusProps) => {
  const [isToolTipVisible, setIsToolTipVisible] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const { logEvent } = useAnalytics()

  const showTooltip = () => {
    setIsToolTipVisible(true)
    logEvent(Events.CLICKED_SHOW_STATUS_FILTER)
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

  const bookingStatusOptions = INDIVIDUAL_BOOKING_STATUS_DISPLAY_INFORMATIONS

  const tooltipId = useId()
  const filterPanelId = `booking-filter-tooltip-${tooltipId}`
  const filterDescriptionId = `booking-filter-description-${tooltipId}`
  const hiddenBookingStatuses = bookingStatusOptions.filter((status) =>
    bookingStatuses.includes(status.value)
  )

  const filterDescription =
    hiddenBookingStatuses.length === 0
      ? 'Tous les statuts sont affichés'
      : `${hiddenBookingStatuses.length} ${pluralizeFr(hiddenBookingStatuses.length, 'statut masqué', 'statuts masqués')} : ${hiddenBookingStatuses.map((status) => status.title).join(', ')}`

  return (
    <div ref={containerRef}>
      <button
        type="button"
        className={styles['bs-filter-button']}
        onClick={toggleTooltip}
        onKeyDown={handleKeyDown}
        aria-controls={filterPanelId}
        aria-expanded={isToolTipVisible}
        aria-describedby={filterDescriptionId}
      >
        <span
          className={cn(styles['table-head-label'], styles['status-filter'])}
        >
          Statut
        </span>
        <span className={styles['status-container']}>
          <SvgIcon
            alt=""
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
      <span id={filterDescriptionId} className={styles['visually-hidden']}>
        {filterDescription}
      </span>
      <div
        className={styles['bs-filter']}
        id={filterPanelId}
        hidden={!isToolTipVisible}
        aria-hidden={!isToolTipVisible}
      >
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
