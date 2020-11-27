import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'

import Icon from 'components/layout/Icon'

import { getBookingStatusDisplayInformations } from '../CellsFormatter/utils/bookingStatusConverter'

class FilterByBookingStatus extends Component {
  constructor(props) {
    super(props)
    this.state = {
      bookingStatusFilters: [],
      showFilterStatusTooltip: false,
    }
  }

  componentDidMount() {
    if (window) {
      window.addEventListener('click', this.toggleFilterVisibilityOnClick, false)
      window.addEventListener('focus', this.toggleFilterVisibilityForKeyNavigation, true)
    }
  }

  componentWillUnmount() {
    window.removeEventListener('click', this.toggleFilterVisibilityOnClick, false)
    window.removeEventListener('focus', this.toggleFilterVisibilityForKeyNavigation, true)
  }

  STATUS_FILTER_ELEMENT_IDENTIFIER = 'data-status-filter-tooltip'

  toggleFilterVisibilityOnClick = event => {
    if (!event.target.getAttribute(this.STATUS_FILTER_ELEMENT_IDENTIFIER)) {
      this.hideFilters()
    }
  }

  toggleFilterVisibilityForKeyNavigation = event => {
    if (
      event.target.attributes &&
      !event.target.getAttribute(this.STATUS_FILTER_ELEMENT_IDENTIFIER)
    ) {
      this.hideFilters()
    }
  }

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
      title: getBookingStatusDisplayInformations(bookingStatus).status,
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
      <Fragment>
        <button
          className="bs-filter-button"
          data-status-filter-tooltip
          onClick={this.showFilter}
          onFocus={this.showFilter}
          type="button"
        >
          <Icon
            alt="Filtrer par statut"
            data-status-filter-tooltip
            svg={this.computeIconSrc()}
          />
        </button>
        <span
          className="bs-filter"
          data-status-filter-tooltip
        >
          {showFilterStatusTooltip && (
            <div
              className="bs-filter-tooltip"
              data-status-filter-tooltip
            >
              <div
                className="bs-filter-label"
                data-status-filter-tooltip
              >
                {'Afficher les statuts'}
              </div>
              {bookingStatuses.map(bookingStatus => (
                <Fragment key={bookingStatus.value}>
                  <label data-status-filter-tooltip>
                    <input
                      checked={!bookingStatusFilters.includes(bookingStatus.value)}
                      data-status-filter-tooltip
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
      </Fragment>
    )
  }
}

FilterByBookingStatus.propTypes = {
  bookingsRecap: PropTypes.arrayOf(PropTypes.shape({})).isRequired,
  updateGlobalFilters: PropTypes.func.isRequired,
}

export default FilterByBookingStatus
