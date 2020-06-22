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
      showFilterStatusTooltip: false,
    }
  }

  shouldComponentUpdate() {
    return true
  }

  canHideFilter = true

  showFilters = () => {
    this.setState({
      showFilterStatusTooltip: true,
    })
  }

  hideFilters = () => {
    this.setState({
      showFilterStatusTooltip: false,
    })
  }

  preventHidingFilter = () => {
    this.canHideFilter = false
  }

  authorizeHidingFilter = () => {
    this.canHideFilter = true
  }

  handleBlur = () => {
    if (this.canHideFilter) {
      this.hideFilters()
    }
  }

  handleCheckboxChange = event => {
    const { updateGlobalFilters } = this.props
    const { bookingStatusFilter } = this.state

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

  render() {
    const { bookingsRecap } = this.props
    const { showFilterStatusTooltip } = this.state
    const bookingStatusValues = getAvailableStatusValues(bookingsRecap).sort()

    return (
      <span
        className="bs-filter"
        onBlur={this.handleBlur}
        /* eslint-disable-next-line react/jsx-handler-names */
        onFocus={this.showFilters}
        role="button"
      >
        <button type="button">
          <Icon
            alt="Filtrer par statut"
            svg="ico-filter-status"
          />
        </button>

        {showFilterStatusTooltip && (
          <div className="bs-filter-tooltip">
            <div className="bs-filter-label">
              {'Afficher les statuts'}
            </div>
            {bookingStatusValues.map(row => (
              <Fragment key={row}>
                <label
                  /* eslint-disable-next-line react/jsx-handler-names */
                  onMouseDown={this.preventHidingFilter}
                  /* eslint-disable-next-line react/jsx-handler-names */
                  onMouseUp={this.authorizeHidingFilter}
                >
                  <input
                    defaultChecked
                    id={`bs-${row}`}
                    name={row}
                    onChange={this.handleCheckboxChange}
                    type="checkbox"
                  />
                  {row}
                </label>
              </Fragment>
            ))}
          </div>
        )}
      </span>
    )
  }
}

FilterByBookingStatus.propTypes = {
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  updateGlobalFilters: PropTypes.func.isRequired,
}

export default FilterByBookingStatus
