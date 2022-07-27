import isEqual from 'lodash.isequal'
import PropTypes from 'prop-types'
import React, { useEffect, useRef, useState } from 'react'

import useOnClickOrFocusOutside from 'components/hooks/useOnClickOrFocusOutside'
import Icon from 'components/layout/Icon'

import { getBookingStatusDisplayInformations } from '../../CellsFormatter/utils/bookingStatusConverter'

function getAvailableBookingStatuses(bookingsRecap) {
  const presentBookingStatues = Array.from(
    new Set(bookingsRecap.map(bookingRecap => bookingRecap.booking_status))
  ).map(bookingStatus => ({
    title: getBookingStatusDisplayInformations(bookingStatus).status,
    value: bookingStatus,
  }))

  const byStatusTitle = (bookingStatusA, bookingStatusB) => {
    const titleA = bookingStatusA.title
    const titleB = bookingStatusB.title
    return titleA < titleB ? -1 : titleA > titleB ? 1 : 0
  }

  return presentBookingStatues.sort(byStatusTitle)
}

const FilterByBookingStatus = ({
  bookingStatuses,
  bookingsRecap,
  updateGlobalFilters,
}) => {
  const [bookingStatusFilters, setBookingStatusFilters] =
    useState(bookingStatuses)
  const [isToolTipVisible, setIsToolTipVisible] = useState(false)
  const containerRef = useRef()

  function showFilter() {
    setIsToolTipVisible(true)
  }

  function hideFilters() {
    setIsToolTipVisible(false)
  }

  useOnClickOrFocusOutside(containerRef, hideFilters)

  function handleCheckboxChange(event) {
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
    if (!isEqual(bookingStatuses, bookingStatusFilters)) {
      updateGlobalFilters({
        bookingStatus: bookingStatusFilters,
      })
    }
  }, [bookingStatusFilters, bookingStatuses, updateGlobalFilters])

  const computeIconSrc = () => {
    if (bookingStatusFilters.length > 0) {
      return 'ico-filter-status-active'
    } else if (isToolTipVisible) {
      return 'ico-filter-status-red'
    } else {
      return 'ico-filter-status-black'
    }
  }

  const filteredBookingStatuses = getAvailableBookingStatuses(bookingsRecap)

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
            <div className="bs-filter-label">Afficher les statuts</div>
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

FilterByBookingStatus.propTypes = {
  bookingStatuses: PropTypes.arrayOf(PropTypes.string).isRequired,
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  updateGlobalFilters: PropTypes.func.isRequired,
}

export default FilterByBookingStatus
