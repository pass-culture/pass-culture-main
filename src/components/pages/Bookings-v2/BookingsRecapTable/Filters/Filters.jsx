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

  handleOmniSearchCriteriaChange = event => {
    const { selectedOmniSearchCriteria, filters } = this.state
    const newOmniSearchCriteria = event.target.value.toLowerCase()
    const currentOmniSearchStateKey = this.OMNISEARCH_FILTERS.find(
      criteria => criteria.id === selectedOmniSearchCriteria
    ).stateKey
    const currentFilterKeywords = filters[currentOmniSearchStateKey]
    this.setState(
      {
        selectedOmniSearchCriteria: newOmniSearchCriteria,
      },
      () => {
        this.updateOmniSearchKeywords(newOmniSearchCriteria, currentFilterKeywords)
      }
    )
  }

  handleOmniSearchChange = event => {
    const { selectedOmniSearchCriteria } = this.state
    this.updateOmniSearchKeywords(selectedOmniSearchCriteria, event.target.value)
  }

  updateOmniSearchKeywords(omniSearchCriteria, keywords) {
    const cleanedOmnisearchFilters = {
      bookingBeneficiary: EMPTY_FILTER_VALUE,
      bookingToken: EMPTY_FILTER_VALUE,
      offerISBN: EMPTY_FILTER_VALUE,
      offerName: EMPTY_FILTER_VALUE,
    }

    const omniSearchStateKey = this.OMNISEARCH_FILTERS.find(
      criteria => criteria.id === omniSearchCriteria
    ).stateKey
    cleanedOmnisearchFilters[omniSearchStateKey] =
      keywords && keywords.length > 0 ? keywords : EMPTY_FILTER_VALUE

    const updatedSelectedContent = { keywords: keywords }
    this.updateFilters(cleanedOmnisearchFilters, updatedSelectedContent)
  }

  OMNISEARCH_FILTERS = [
    {
      id: 'offre',
      placeholderText: "Rechercher par nom d'offre",
      stateKey: 'offerName',
      selectOptionText: 'Offre',
    },
    {
      id: 'bénéficiaire',
      placeholderText: 'Rechercher par nom ou email',
      stateKey: 'bookingBeneficiary',
      selectOptionText: 'Bénéficiaire',
    },
    {
      id: 'isbn',
      placeholderText: 'Rechercher par ISBN',
      stateKey: 'offerISBN',
      selectOptionText: 'ISBN',
    },
    {
      id: 'token',
      placeholderText: 'Rechercher par contremarque',
      stateKey: 'bookingToken',
      selectOptionText: 'Contremarque',
    },
  ]

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
    const placeholderText = this.OMNISEARCH_FILTERS.find(
      criteria => criteria.id === selectedOmniSearchCriteria
    ).placeholderText

    return (
      <div className="filters-wrapper">
        <FilterByOmniSearch
          keywords={keywords}
          omniSearchSelectOptions={this.OMNISEARCH_FILTERS}
          onHandleOmniSearchChange={this.handleOmniSearchChange}
          onHandleOmniSearchCriteriaChange={this.handleOmniSearchCriteriaChange}
          placeholderText={placeholderText}
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
