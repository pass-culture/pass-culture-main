import React, { Component } from 'react'
import PropTypes from 'prop-types'
import debounce from 'lodash.debounce'
import moment from 'moment'
import { fetchAllVenuesByProUser } from '../../../../../services/venuesService'
import { ALL_VENUES } from '../utils/filterBookingsRecap'
import formatAndOrderVenues from '../utils/formatAndOrderVenues'
import FilterByOmniSearch from './FilterByOmniSearch'
import FilterByEventDate from './FilterByEventDate.jsx'
import FilterByVenue from './FilterByVenue'
import FilterByBookingPeriod from './FilterByBookingPeriod'

export const EMPTY_FILTER_VALUE = ''
const DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS = 300
const DEFAULT_OMNISEARCH_CRITERIA = 'offre'

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
        offerVenue: ALL_VENUES,
      },
      keywords: EMPTY_FILTER_VALUE,
      selectedBookingBeginningDate: EMPTY_FILTER_VALUE,
      selectedBookingEndingDate: moment(),
      selectedOfferDate: EMPTY_FILTER_VALUE,
      selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
      selectedVenue: EMPTY_FILTER_VALUE,
      venues: [],
    }
  }

  componentDidMount() {
    fetchAllVenuesByProUser().then(venues => this.setState({ venues: venues }))
  }

  shouldComponentUpdate() {
    return true
  }

  applyFilters = debounce(filterValues => {
    const { setFilters } = this.props
    setFilters({
      ...filterValues,
    })
  }, DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS)

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
        },
        keywords: EMPTY_FILTER_VALUE,
        selectedBookingBeginningDate: EMPTY_FILTER_VALUE,
        selectedBookingEndingDate: moment(),
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
    const { oldestBookingDate } = this.props
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
          keywords={keywords}
          selectedOmniSearchCriteria={selectedOmniSearchCriteria}
          updateFilters={this.updateFilters}
        />
        <div className="fw-second-line">
          <FilterByEventDate
            selectedOfferDate={selectedOfferDate}
            updateFilters={this.updateFilters}
          />
          <FilterByVenue
            selectedVenue={selectedVenue}
            updateFilters={this.updateFilters}
            venuesFormattedAndOrdered={venuesFormattedAndOrdered}
          />
          <FilterByBookingPeriod
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
  setFilters: PropTypes.func.isRequired,
}

export default Filters
