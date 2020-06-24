import React, { Component, Fragment } from 'react'
import PropTypes from 'prop-types'
import Icon from '../../../../layout/Icon'
import { getStatusTitle } from '../CellsFormatter/utils/bookingStatusConverter'

class FilterByBookingStatus extends Component {
  constructor(props) {
    super(props)
    this.state = {
      bookingStatusFilters: [],
      showFilterStatusTooltip: false,
    }
  }

  TIME_NEEDED_TO_TAB_IN_FILTER = 150
  canHideFilter = true
  keyHideFilterTimeout

  showFilter = () => {
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

  hideFiltersIfAllowed = () => {
    if (this.canHideFilter) {
      this.hideFilters()
    }
  }

  handleHidingFilterForKeyDown = event => {
    if (event.key === 'Tab') {
      this.preventHidingFilter()
      this.keyHideFilterTimeout = setTimeout(() => {
        this.authorizeHidingFilter()
        this.hideFilters()
      }, this.TIME_NEEDED_TO_TAB_IN_FILTER)
    }
  }

  preventHidingFilterOfKeyDown = () => {
    this.authorizeHidingFilter()
    clearTimeout(this.keyHideFilterTimeout)
  }

  handleCheckboxChange = event => {
    const { updateGlobalFilters } = this.props
    const { bookingStatusFilters } = this.state

    const statusId = event.target.name
    const isSelected = event.target.checked

    if (!isSelected) {
      bookingStatusFilters.push(statusId)
    } else {
      const index = bookingStatusFilters.indexOf(statusId)
      if (index !== -1) bookingStatusFilters.splice(index, 1)
    }

    updateGlobalFilters({
      bookingStatus: bookingStatusFilters,
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

  byStatusTitle(bookingStatusA, bookingStatusB) {
    const titleA = bookingStatusA.title
    const titleB = bookingStatusB.title
    return titleA < titleB ? -1 : titleA > titleB ? 1 : 0
  }

  computeIconSrc() {
    const { bookingStatusFilters, showFilterStatusTooltip } = this.state

    if (bookingStatusFilters.length > 0) {
      return 'ico-filter-status-active'
    } else if (showFilterStatusTooltip) {
      return 'ico-filter-status-red'
    } else {
      return 'ico-filter-status-black'
    }
  }

  render() {
    const { bookingsRecap } = this.props
    const { bookingStatusFilters, showFilterStatusTooltip } = this.state
    const bookingStatuses = this.getAvailableStatuses(bookingsRecap).sort(this.byStatusTitle)

    return (
      // eslint-disable-next-line jsx-a11y/interactive-supports-focus
      <span
        className="bs-filter"
        onBlur={this.hideFiltersIfAllowed}
        onFocus={this.showFilter}
        onKeyDown={this.handleHidingFilterForKeyDown}
        onKeyUp={this.preventHidingFilterOfKeyDown}
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
                    checked={!bookingStatusFilters.includes(bookingStatus.value)}
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
