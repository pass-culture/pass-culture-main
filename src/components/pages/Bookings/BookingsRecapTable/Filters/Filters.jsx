import debounce from 'lodash.debounce'
import PropTypes from 'prop-types'
import React, { Component } from 'react'

import { formatAndOrderVenues, fetchAllVenuesByProUser } from 'repository/venuesService'

import {
  ALL_BOOKING_STATUS,
  ALL_VENUES,
  DEFAULT_OMNISEARCH_CRITERIA,
  EMPTY_FILTER_VALUE,
} from './_constants'
import FilterByBookingPeriod from './FilterByBookingPeriod'
import FilterByEventDate from './FilterByEventDate.jsx'
import FilterByOmniSearch from './FilterByOmniSearch'
import FilterByVenue from './FilterByVenue'

class Filters extends Component {
  constructor(props) {
    super(props)
    this.state = {
      filters: {
        bookingBeginningDate: EMPTY_FILTER_VALUE,
        bookingEndingDate: EMPTY_FILTER_VALUE,
        bookingBeneficiary: EMPTY_FILTER_VALUE,
        bookingToken: EMPTY_FILTER_VALUE,
        offerDate: EMPTY_FILTER_VALUE,
        offerISBN: EMPTY_FILTER_VALUE,
        offerName: EMPTY_FILTER_VALUE,
        offerVenue: props.offerVenue,
      },
      keywords: EMPTY_FILTER_VALUE,
      selectedBookingBeginningDate: EMPTY_FILTER_VALUE,
      selectedBookingEndingDate: new Date(),
      selectedOfferDate: EMPTY_FILTER_VALUE,
      selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
      selectedVenue: props.offerVenue !== ALL_VENUES ? props.offerVenue : EMPTY_FILTER_VALUE,
      venues: [],
    }
  }

  componentDidMount() {
    fetchAllVenuesByProUser().then(venues => this.setState({ venues: venues }))
  }

  DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS = 300

  applyFilters = debounce(filterValues => {
    const { updateGlobalFilters } = this.props
    updateGlobalFilters({
      ...filterValues,
    })
  }, this.DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS)

  resetAllFilters = () => {
    this.setState(
      {
        filters: {
          bookingBeneficiary: EMPTY_FILTER_VALUE,
          bookingBeginningDate: EMPTY_FILTER_VALUE,
          bookingEndingDate: EMPTY_FILTER_VALUE,
          bookingToken: EMPTY_FILTER_VALUE,
          offerDate: EMPTY_FILTER_VALUE,
          offerISBN: EMPTY_FILTER_VALUE,
          offerName: EMPTY_FILTER_VALUE,
          offerVenue: ALL_VENUES,
          bookingStatus: ALL_BOOKING_STATUS,
        },
        keywords: EMPTY_FILTER_VALUE,
        selectedBookingBeginningDate: EMPTY_FILTER_VALUE,
        selectedBookingEndingDate: new Date(),
        selectedOfferDate: EMPTY_FILTER_VALUE,
        selectedVenue: EMPTY_FILTER_VALUE,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  updateFilters = (updatedFilter, updatedSelectedContent) => {
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          ...updatedFilter,
        },
        ...updatedSelectedContent,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  render() {
    const { isLoading, oldestBookingDate } = this.props
    const {
      keywords,
      selectedOfferDate,
      selectedBookingBeginningDate,
      selectedBookingEndingDate,
      selectedOmniSearchCriteria,
      selectedVenue,
      venues,
    } = this.state

    const venuesFormattedAndOrdered = formatAndOrderVenues(venues)

    return (
      <div className="filters-wrapper">
        <FilterByOmniSearch
          isDisabled={isLoading}
          keywords={keywords}
          selectedOmniSearchCriteria={selectedOmniSearchCriteria}
          updateFilters={this.updateFilters}
        />
        <div className="fw-second-line">
          <FilterByEventDate
            isDisabled={isLoading}
            selectedOfferDate={selectedOfferDate}
            updateFilters={this.updateFilters}
          />
          <FilterByVenue
            isDisabled={isLoading}
            selectedVenue={selectedVenue}
            updateFilters={this.updateFilters}
            venuesFormattedAndOrdered={venuesFormattedAndOrdered}
          />
          <FilterByBookingPeriod
            isDisabled={isLoading}
            oldestBookingDate={oldestBookingDate}
            selectedBookingBeginningDate={selectedBookingBeginningDate}
            selectedBookingEndingDate={selectedBookingEndingDate}
            updateFilters={this.updateFilters}
          />
        </div>
      </div>
    )
  }
}

Filters.propTypes = {
  isLoading: PropTypes.bool.isRequired,
  offerVenue: PropTypes.string.isRequired,
  oldestBookingDate: PropTypes.string.isRequired,
  updateGlobalFilters: PropTypes.func.isRequired,
}

export default Filters
