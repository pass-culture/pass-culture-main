import React, { Component } from 'react'
import PropTypes from 'prop-types'
import debounce from 'lodash.debounce'
import DatePicker from 'react-datepicker'
import moment from 'moment'
import InputWithCalendar from './InputWithCalendar'
import { fetchAllVenuesByProUser } from '../../../../../services/venuesService'
import { ALL_VENUES } from '../utils/filterBookingsRecap'

const DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS = 300

class Filters extends Component {
  constructor(props) {
    super(props)
    this.state = {
      filters: {
        bookingBeginningDate: null,
        bookingEndingDate: null,
        bookingBeneficiary: null,
        offerDate: null,
        offerName: null,
        offerVenue: ALL_VENUES,
      },
      keywords: '',
      keywordsForBeneficiary: '',
      selectedBookingBeginningDate: null,
      selectedBookingEndingDate: moment(),
      selectedOfferDate: null,
      selectedVenue: '',
      venues: [],
    }
    this.venueSelect = React.createRef()
  }

  componentDidMount() {
    fetchAllVenuesByProUser().then(venues => this.setState({ venues: venues }))
  }

  shouldComponentUpdate() {
    return true
  }

  resetAllFilters = () => {
    this.setState(
      {
        filters: {
          bookingBeneficiary: null,
          offerName: null,
          offerDate: null,
          offerVenue: ALL_VENUES,
          bookingBeginningDate: null,
          bookingEndingDate: null,
        },
        keywords: '',
        keywordsForBeneficiary: '',
        selectedBookingBeginningDate: null,
        selectedBookingEndingDate: moment(),
        selectedOfferDate: null,
        selectedVenue: '',
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  applyFilters = debounce(filterValues => {
    const {
      offerName,
      offerDate,
      offerVenue,
      bookingBeginningDate,
      bookingBeneficiary,
      bookingEndingDate,
    } = filterValues
    const { setFilters } = this.props
    setFilters({
      bookingBeginningDate: bookingBeginningDate,
      bookingEndingDate: bookingEndingDate,
      bookingBeneficiary: bookingBeneficiary,
      offerDate: offerDate,
      offerName: offerName,
      offerVenue: offerVenue,
    })
  }, DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS)

  handleOfferNameChange = event => {
    const keywords = event.target.value
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          offerName: keywords.length > 0 ? keywords : null,
        },
        keywords: keywords,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  handleOfferDateChange = offerDate => {
    const dateToFilter = offerDate === null ? null : offerDate.format('YYYY-MM-DD')
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

  handleBeneficiaryChange = event => {
    const keywordsForBeneficiary = event.target.value
    const { filters } = this.state

    this.setState(
      {
        filters: {
          ...filters,
          bookingBeneficiary: keywordsForBeneficiary.length > 0 ? keywordsForBeneficiary : null,
        },
        keywordsForBeneficiary: keywordsForBeneficiary,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  handleBookingBeginningDateChange = bookingBeginningDate => {
    const dateToFilter =
      bookingBeginningDate === null ? null : bookingBeginningDate.format('YYYY-MM-DD')
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
    const dateToFilter = bookingEndingDate === null ? null : bookingEndingDate.format('YYYY-MM-DD')
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
        this.venueSelect.current.blur()
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  formatAndOrderVenues = venues => {
    const sortAlphabeticallyByDisplayName = (a, b) => {
      let aDisplayName = a.displayName.toLowerCase()
      let bDisplayName = b.displayName.toLowerCase()
      return aDisplayName < bDisplayName ? -1 : aDisplayName > bDisplayName ? 1 : 0
    }

    return venues
      .map(venue => {
        const displayName = venue.isVirtual ? `${venue.offererName} - Offre numérique` : venue.name
        return { id: venue.id, displayName }
      })
      .sort(sortAlphabeticallyByDisplayName)
  }

  render() {
    const { oldestBookingDate } = this.props
    const {
      keywords,
      keywordsForBeneficiary,
      selectedOfferDate,
      selectedBookingBeginningDate,
      selectedBookingEndingDate,
      selectedVenue,
      venues,
    } = this.state

    const venuesFormattedAndOrdered = this.formatAndOrderVenues(venues)

    return (
      <div className="filters-wrapper">
        <div className="fw-offer-name">
          <label
            className="fw-offer-name-label"
            htmlFor="text-filter-input"
          >
            {'Offre'}
          </label>
          <input
            className="fw-offer-name-input"
            id="text-filter-input"
            onChange={this.handleOfferNameChange}
            placeholder={"Rechercher par nom d'offre"}
            type="text"
            value={keywords}
          />
        </div>
        <div className="fw-offer-name">
          <label
            className="fw-offer-name-label"
            htmlFor="text-filter-input"
          >
            {'Beneficiaire / to merge'}
          </label>
          <input
            className="fw-beneficiary-input"
            id="text-filter-input"
            onChange={this.handleBeneficiaryChange}
            placeholder="Rechercher par nom ou email"
            type="text"
            value={keywordsForBeneficiary}
          />
        </div>
        <div className="fw-second-line">
          <div className="fw-offer-date">
            <label
              className="fw-offer-date-label"
              htmlFor="select-filter-date"
            >
              {"Date de l'évènement"}
            </label>
            <div className="fw-offer-date-picker">
              <DatePicker
                className="fw-offer-date-input"
                customInput={<InputWithCalendar customClass="field-date-only" />}
                dropdownMode="select"
                id="select-filter-date"
                onChange={this.handleOfferDateChange}
                placeholderText="JJ/MM/AAAA"
                selected={selectedOfferDate}
              />
            </div>
          </div>
          <div className="fw-venues">
            <label
              className="fw-offer-venue-label"
              htmlFor="offer-venue-input"
            >
              {'Lieu'}
            </label>
            <select
              id="offer-venue-input"
              onBlur={this.handleVenueSelection}
              onChange={this.handleVenueSelection}
              ref={this.venueSelect}
              value={selectedVenue}
            >
              <option value={ALL_VENUES}>
                {'Tous les lieux'}
              </option>
              {venuesFormattedAndOrdered.map(venue => (
                <option
                  key={venue.id}
                  value={venue.id}
                >
                  {venue.displayName}
                </option>
              ))}
            </select>
          </div>
          <div className="fw-booking-date">
            <label
              className="fw-booking-date-label"
              htmlFor="select-filter-booking-date"
            >
              {'Période de réservation'}
            </label>
            <div
              className="fw-booking-date-inputs"
              id="select-filter-booking-date"
            >
              <div className="fw-booking-date-begin-picker">
                <DatePicker
                  className="fw-booking-date-input"
                  customInput={<InputWithCalendar customClass="field-date-only field-date-begin" />}
                  dropdownMode="select"
                  maxDate={selectedBookingEndingDate}
                  minDate={oldestBookingDate}
                  onChange={this.handleBookingBeginningDateChange}
                  placeholderText="JJ/MM/AAAA"
                  selected={selectedBookingBeginningDate}
                />
              </div>
              <span className="vertical-bar" />
              <div className="fw-booking-date-end-picker">
                <DatePicker
                  className="fw-booking-date-input"
                  customInput={<InputWithCalendar customClass="field-date-only field-date-end" />}
                  dropdownMode="select"
                  maxDate={moment()}
                  minDate={selectedBookingBeginningDate}
                  onChange={this.handleBookingEndingDateChange}
                  placeholderText="JJ/MM/AAAA"
                  selected={selectedBookingEndingDate}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }
}

Filters.propTypes = {
  setFilters: PropTypes.func.isRequired,
}

export default Filters
