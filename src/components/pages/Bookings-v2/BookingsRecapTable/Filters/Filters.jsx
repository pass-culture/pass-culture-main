import React, { Component } from 'react'
import PropTypes from 'prop-types'
import debounce from 'lodash.debounce'
import DatePicker from 'react-datepicker'
import { InputWithCalendar } from '../../../../layout/form/fields/DateField/InputWithCalendar'

const DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS = 300

class Filters extends Component {
  constructor(props) {
    super(props)
    this.state = {
      selectedOfferDate: null,
      filters: {
        offerName: null,
        offerDate: null,
      },
    }
  }

  shouldComponentUpdate() {
    return true
  }

  applyFilters = debounce(filterValues => {
    const { offerName, offerDate } = filterValues
    const { setFilters } = this.props
    setFilters({ offerName: offerName, offerDate: offerDate })
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

  render() {
    const { selectedOfferDate } = this.state
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
      </div>
    )
  }
}

Filters.propTypes = {
  setFilters: PropTypes.func.isRequired,
}

export default Filters
