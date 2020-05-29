import React, { Component } from 'react'
import PropTypes from 'prop-types'
import debounce from 'lodash.debounce'
import DatePicker from 'react-datepicker'
import { InputWithCalendar } from '../../../../layout/form/fields/DateField/InputWithCalendar'
import moment from 'moment'

const DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS = 300

class Filters extends Component {
  constructor(props) {
    super(props)
    const { oldestBookingDate } = this.props
    this.state = {
      filters: {
        offerDate: null,
        offerName: null,
        bookingBeginDate: null,
        bookingEndDate: null,
      },
      keywords: '',
      selectedOfferDate: null,
      selectedBookingBeginDate: moment(oldestBookingDate),
      selectedBookingEndDate: moment(),
    }
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
          bookingBeginDate: null,
          bookingEndDate: null,
        },
        keywords: '',
        selectedOfferDate: null,
        selectedBookingBeginDate: null,
        selectedBookingEndDate: null,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  applyFilters = debounce(filterValues => {
    const { offerName, offerDate, bookingBeginDate, bookingEndDate } = filterValues
    const { setFilters } = this.props
    setFilters({
      offerName: offerName,
      offerDate: offerDate,
      bookingBeginDate: bookingBeginDate,
      bookingEndDate: bookingEndDate,
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

  handleBookingBeginDateChange = bookingBeginDate => {
    const dateToFilter = bookingBeginDate === null ? null : bookingBeginDate.format('YYYY-MM-DD')
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          bookingBeginDate: dateToFilter,
        },
        selectedBookingBeginDate: bookingBeginDate,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  handleBookingEndDateChange = bookingEndDate => {
    const dateToFilter = bookingEndDate === null ? null : bookingEndDate.format('YYYY-MM-DD')
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          bookingEndDate: dateToFilter,
        },
        selectedBookingEndDate: bookingEndDate,
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
      selectedBookingBeginDate,
      selectedBookingEndDate,
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
            placeholder={"Rechercher par nom d'offre"}
            type="text"
            value={keywords}
          />
        </div>
        <div className="fw-offer-date">
          <label
            className="fw-offer-date-label"
            htmlFor="select-filter-date"
          >
            {"Date de l'évènement"}
          </label>
          <DatePicker
            className="fw-offer-date-input"
            customInput={<InputWithCalendar />}
            dropdownMode="select"
            id="select-filter-date"
            onChange={this.handleOfferDateChange}
            placeholderText="JJ/MM/AAAA"
            selected={selectedOfferDate}
          />
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
              customInput={<InputWithCalendar />}
              dropdownMode="select"
              minDate={oldestBookingDate}
              onChange={this.handleBookingBeginDateChange}
              placeholderText="JJ/MM/AAAA"
              selected={selectedBookingBeginDate}
            />
            <DatePicker
              className="fw-booking-date-input"
              customInput={<InputWithCalendar />}
              dropdownMode="select"
              maxDate={moment()}
              minDate={selectedBookingBeginDate}
              onChange={this.handleBookingEndDateChange}
              placeholderText="JJ/MM/AAAA"
              selected={selectedBookingEndDate}
            />
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
