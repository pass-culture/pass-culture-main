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
        offerDate: EMPTY_FILTER_VALUE,
        offerName: EMPTY_FILTER_VALUE,
        offerISBN: EMPTY_FILTER_VALUE,
        offerVenue: ALL_VENUES,
      },
      keywords: '',
      selectedBookingBeginningDate: EMPTY_FILTER_VALUE,
      selectedBookingEndingDate: moment(),
      selectedOfferDate: EMPTY_FILTER_VALUE,
      selectedOmniSearchCriteria: DEFAULT_OMNISEARCH_CRITERIA,
      selectedVenue: '',
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
    const {
      bookingBeginningDate,
      bookingBeneficiary,
      bookingEndingDate,
      offerName,
      offerDate,
      offerVenue,
      offerISBN,
    } = filterValues
    const { setFilters } = this.props
    setFilters({
      bookingBeginningDate: bookingBeginningDate,
      bookingEndingDate: bookingEndingDate,
      bookingBeneficiary: bookingBeneficiary,
      offerDate: offerDate,
      offerName: offerName,
      offerVenue: offerVenue,
      offerISBN: offerISBN,
    })
  }, DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS)

  resetAllFilters = () => {
    this.setState(
      {
        filters: {
          bookingBeneficiary: EMPTY_FILTER_VALUE,
          bookingBeginningDate: EMPTY_FILTER_VALUE,
          bookingEndingDate: EMPTY_FILTER_VALUE,
          offerDate: EMPTY_FILTER_VALUE,
          offerName: EMPTY_FILTER_VALUE,
          offerISBN: EMPTY_FILTER_VALUE,
          offerVenue: ALL_VENUES,
        },
        keywords: '',
        selectedBookingBeginningDate: EMPTY_FILTER_VALUE,
        selectedBookingEndingDate: moment(),
        selectedOfferDate: EMPTY_FILTER_VALUE,
        selectedVenue: '',
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
        this.OMNISEARCH_FILTERS.find(
          criteria => criteria.id === newOmniSearchCriteria
        ).handleChange(currentFilterKeywords)
      }
    )
  }

  handleOmniSearchChange = event => {
    const { selectedOmniSearchCriteria } = this.state
    this.OMNISEARCH_FILTERS.find(
      criteria => criteria.id === selectedOmniSearchCriteria
    ).handleChange(event.target.value)
  }

  handleOfferNameChange = keywords => {
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          bookingBeneficiary: EMPTY_FILTER_VALUE,
          offerISBN: EMPTY_FILTER_VALUE,
          offerName: keywords && keywords.length > 0 ? keywords : EMPTY_FILTER_VALUE,
        },
        keywords: keywords,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  handleBeneficiaryChange = keywords => {
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          bookingBeneficiary: keywords && keywords.length > 0 ? keywords : EMPTY_FILTER_VALUE,
          offerISBN: EMPTY_FILTER_VALUE,
          offerName: EMPTY_FILTER_VALUE,
        },
        keywords: keywords,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  handleISBNChange = keywords => {
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          bookingBeneficiary: EMPTY_FILTER_VALUE,
          offerISBN: keywords && keywords.length > 0 ? keywords : EMPTY_FILTER_VALUE,
          offerName: EMPTY_FILTER_VALUE,
        },
        keywords: keywords,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  OMNISEARCH_FILTERS = [
    {
      id: 'offre',
      handleChange: this.handleOfferNameChange,
      placeholderText: "Rechercher par nom d'offre",
      stateKey: 'offerName',
      selectOptionText: 'Offre',
    },
    {
      id: 'bénéficiaire',
      handleChange: this.handleBeneficiaryChange,
      placeholderText: 'Rechercher par nom ou email',
      stateKey: 'bookingBeneficiary',
      selectOptionText: 'Bénéficiaire',
    },
    {
      id: 'isbn',
      handleChange: this.handleISBNChange,
      placeholderText: 'Rechercher par ISBN',
      stateKey: 'offerISBN',
      selectOptionText: 'ISBN',
    },
  ]

  handleOfferDateChange = offerDate => {
    const dateToFilter = offerDate === null ? EMPTY_FILTER_VALUE : offerDate.format('YYYY-MM-DD')
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          offerDate: dateToFilter,
        },
        selectedOfferDate: offerDate,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  handleBookingBeginningDateChange = bookingBeginningDate => {
    const dateToFilter =
      bookingBeginningDate === null ? EMPTY_FILTER_VALUE : bookingBeginningDate.format('YYYY-MM-DD')
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          bookingBeginningDate: dateToFilter,
        },
        selectedBookingBeginningDate: bookingBeginningDate,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  handleBookingEndingDateChange = bookingEndingDate => {
    const dateToFilter =
      bookingEndingDate === null ? EMPTY_FILTER_VALUE : bookingEndingDate.format('YYYY-MM-DD')
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          bookingEndingDate: dateToFilter,
        },
        selectedBookingEndingDate: bookingEndingDate,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  handleVenueSelection = event => {
    const venueId = event.target.value
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          offerVenue: venueId,
        },
        selectedVenue: venueId,
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
            onHandleOfferDateChange={this.handleOfferDateChange}
            selectedOfferDate={selectedOfferDate}
          />
          <FilterByVenue
            onHandleVenueSelection={this.handleVenueSelection}
            selectedVenue={selectedVenue}
            venuesFormattedAndOrdered={venuesFormattedAndOrdered}
          />
          <FilterByBookingPeriod
            oldestBookingDate={oldestBookingDate}
            onHandleBookingBeginningDateChange={this.handleBookingBeginningDateChange}
            onHandleBookingEndingDateChange={this.handleBookingEndingDateChange}
            selectedBookingBeginningDate={selectedBookingBeginningDate}
            selectedBookingEndingDate={selectedBookingEndingDate}
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
