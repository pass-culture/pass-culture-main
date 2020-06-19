import React, { Component, Fragment } from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../../layout/Icon'

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
      <span className="bs-filter">
        <Icon svg="ico-filter-status" />
        <div className="bs-filter-tooltip">
          <div className="bs-filter-label">
            {'Afficher les statuts'}
          </div>
          {bookingStatusValues.map(row => (
            <Fragment key={row}>
              <label>
                <input
                  defaultChecked
                  id={`bs-${row}`}
                  name={row}
                  onChange={handleCheckboxChange}
                  type="checkbox"
                />
                {row}
              </label>
            </Fragment>
          ))}
        </div>
      </span>
    )
  }
}

FilterByBookingStatus.propTypes = {
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  updateGlobalFilters: PropTypes.func.isRequired,
}

export default FilterByBookingStatus
