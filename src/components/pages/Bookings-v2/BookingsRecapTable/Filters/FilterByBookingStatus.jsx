import React, { Component, Fragment } from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../../layout/Icon'
import { getStatusTitle } from '../CellsFormatter/utils/bookingStatusConverter'

const TIME_NEEDED_TO_TAB_IN_FILTER = 150

class FilterByBookingStatus extends Component {
  constructor(props) {
    super(props)
    this.state = {
      bookingStatusFilter: [],
      showFilterStatusTooltip: false,
    }
  }

  canHideFilter = true
  keyHideFilterTimeout

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

  handleKeyDown = event => {
    if (event.key === 'Tab') {
      this.preventHidingFilter()
      this.keyHideFilterTimeout = setTimeout(() => {
        this.authorizeHidingFilter()
        this.hideFilters()
      }, TIME_NEEDED_TO_TAB_IN_FILTER)
    }
  }

  handleKeyUp = () => {
    this.authorizeHidingFilter()
    clearTimeout(this.keyHideFilterTimeout)
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

  computeIconSrc() {
    const { bookingStatusFilter, showFilterStatusTooltip } = this.state

    if (bookingStatusFilter.length > 0) {
      return 'ico-filter-status-active'
    } else if (showFilterStatusTooltip) {
      return 'ico-filter-status-red'
    } else {
      return 'ico-filter-status-black'
    }
  }

  render() {
    const { bookingsRecap } = this.props
    const { bookingStatusFilter, showFilterStatusTooltip } = this.state
    const bookingStatuses = this.getAvailableStatuses(bookingsRecap).sort(this.byStatusTitle)

    return (
      // eslint-disable-next-line jsx-a11y/interactive-supports-focus
      <span
        className="bs-filter"
        onBlur={this.handleBlur}
        onFocus={this.showFilters}
        onKeyDown={this.handleKeyDown}
        onKeyUp={this.handleKeyUp}
        role="button"
      >
        <button type="button">
          <Icon
            alt="Filtrer par statut"
            svg={this.computeIconSrc()}
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
                  onMouseDown={this.preventHidingFilter}
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
