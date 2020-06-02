import React, { Component } from 'react'
import PropTypes from 'prop-types'
import debounce from 'lodash.debounce'
import DatePicker from 'react-datepicker'
import moment from 'moment'
import InputWithCalendar from './InputWithCalendar'
import { fetchAllVenuesByProUser } from '../../../../../services/venuesService'

const DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS = 300

class Filters extends Component {
  constructor(props) {
    super(props)
    this.state = {
      filters: {
        bookingBeginningDate: null,
        bookingEndingDate: null,
        offerDate: null,
        offerName: null,
        offerVenue: '',
      },
      keywords: '',
      selectedOfferDate: null,
      selectedBookingBeginningDate: null,
      selectedBookingEndingDate: moment(),
      selectedVenue: '',
      venues: []
    }
  }

  componentDidMount() {
    fetchAllVenuesByProUser().then((venues) => this.setState({ venues: venues }))
  }

  shouldComponentUpdate() {
    return true
  }

  resetAllFilters = () => {
    this.setState(
      {
        filters: {
          offerName: null,
          offerDate: null,
          offerVenue: '',
          bookingBeginningDate: null,
          bookingEndingDate: null,
        },
        keywords: '',
        selectedOfferDate: null,
        selectedBookingBeginningDate: null,
        selectedBookingEndingDate: moment(),
        selectedVenue: ''
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  applyFilters = debounce(filterValues => {
    const { offerName, offerDate, offerVenue, bookingBeginningDate, bookingEndingDate } = filterValues
    const { setFilters } = this.props
    setFilters({
      offerDate: offerDate,
      offerName: offerName,
      offerVenue: offerVenue,
      bookingBeginningDate: bookingBeginningDate,
      bookingEndingDate: bookingEndingDate,
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
      }, () => {
        const { filters } = this.state
        this.applyFilters(filters)
      })
  }

  handleVenueSelection = (event) => {
    const venueId = event.target.value
    const { filters } = this.state

    this.setState({
        filters: {
          ...filters,
          offerVenue: venueId
        },
        selectedVenue: venueId
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
      selectedVenue,
      venues
    } = this.state

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
            placeholder={'Rechercher par nom d\'offre'}
            type="text"
            value={keywords}
          />
        </div>
        <div className="fw-second-line">
          <div className="fw-offer-date">
            <label
              className="fw-offer-date-label"
              htmlFor="select-filter-date"
            >
              {'Date de l\'évènement'}
            </label>
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
          <div className="fw-venues">
            <label
              className="fw-offer-venue-label"
              htmlFor="text-filter-input"
            >
              {'Lieu'}
            </label>
            <select
              onBlur={this.handleVenueSelection}
              onChange={this.handleVenueSelection}
              value={selectedVenue}
            >
              <option
                value=""
              >
                {'Tous les lieux'}
              </option>
              {venues.map(venue => (
                <option
                  key={venue.id}
                  value={venue.id}
                >
                  {venue.isVirtual ? `${venue.name} - Offre numérique` : venue.name}
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
              <DatePicker
                className="fw-booking-date-input"
                customInput={<InputWithCalendar customClass="field-date-only field-date-begin" />}
                dropdownMode="select"
                maxDate={moment()}
                minDate={oldestBookingDate}
                onChange={this.handleBookingBeginningDateChange}
                placeholderText="JJ/MM/AAAA"
                selected={selectedBookingBeginningDate}
              />
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
    )
  }
}

Filters.propTypes = {
  setFilters: PropTypes.func.isRequired,
}

export default Filters
