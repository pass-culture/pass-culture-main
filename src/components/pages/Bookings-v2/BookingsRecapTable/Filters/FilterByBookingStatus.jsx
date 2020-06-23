import React, { Component, Fragment } from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../../layout/Icon'
import { getStatusTitle } from '../CellsFormatter/utils/bookingStatusConverter'

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

  getAvailableStatuses(bookingsRecap) {
    const presentBookingStatues = new Set(
      bookingsRecap.map(bookingRecap => bookingRecap.booking_status)
    )
    return Array.from(presentBookingStatues).map(bookingStatus => ({
      title: getStatusTitle(bookingStatus),
      value: bookingStatus,
    }))
  }

  byStatusTitle(a, b) {
    const titleA = a.title
    const titleB = b.title
    return titleA < titleB ? -1 : titleA > titleB ? 1 : 0
  }

  render() {
    const { bookingsRecap } = this.props
    const { bookingStatusFilter, showFilterStatusTooltip } = this.state
    const bookingStatuses = this.getAvailableStatuses(bookingsRecap).sort(this.byStatusTitle)

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
            svg={bookingStatusFilter.length > 0 ? 'ico-filter-status-active' : 'ico-filter-status'}
          />
        </button>

        {showFilterStatusTooltip && (
          <div className="bs-filter-tooltip">
            <div className="bs-filter-label">
              {'Afficher les statuts'}
            </div>
            {bookingStatuses.map(bookingStatus => (
              <Fragment key={bookingStatus.value}>
                <label
                  /* eslint-disable-next-line react/jsx-handler-names */
                  onMouseDown={this.preventHidingFilter}
                  /* eslint-disable-next-line react/jsx-handler-names */
                  onMouseUp={this.authorizeHidingFilter}
                >
                  <input
                    checked={!bookingStatusFilter.includes(bookingStatus.value)}
                    id={`bs-${bookingStatus.value}`}
                    name={bookingStatus.value}
                    onChange={this.handleCheckboxChange}
                    type="checkbox"
                  />
                  {bookingStatus.title}
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
