import React, { Component, Fragment } from 'react'
import PropTypes from 'prop-types'

const getAvailableStatusValues = bookingsRecap => {
  const bookingStatusValues = new Set()
  bookingsRecap.forEach(row => {
    bookingStatusValues.add(row.booking_status)
  })
  return [...bookingStatusValues]
}

class FilterByBookingStatus extends Component {
  constructor(props) {
    super(props)
    this.state = {
      bookingStatusFilter: [],
    }
  }

  shouldComponentUpdate() {
    return true
  }

  render() {
    const { updateGlobalFilters, bookingsRecap } = this.props
    const { bookingStatusFilter } = this.state
    const bookingStatusValues = getAvailableStatusValues(bookingsRecap).sort()

    function handleCheckboxChange(event) {
      const statusId = event.target.name
      const isSelected = event.target.checked

      if (!isSelected) {
        bookingStatusFilter.push(statusId)
      } else {
        const index = bookingStatusFilter.indexOf(statusId)
        if (index !== -1) bookingStatusFilter.splice(index, 1)
      }

      updateGlobalFilters({
        bookingStatus: bookingStatusFilter,
      })
    }

    return (
      <div>
        {bookingStatusValues.map(row => (
          <Fragment key={row}>
            <input
              defaultChecked
              id={`bs-${row}`}
              name={row}
              onChange={handleCheckboxChange}
              type="checkbox"
            />
            <label htmlFor={`bs-${row}`}>
              {row}
            </label>
          </Fragment>
        ))}
      </div>
    )
  }
}

FilterByBookingStatus.propTypes = {
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  updateGlobalFilters: PropTypes.func.isRequired,
}

export default FilterByBookingStatus
