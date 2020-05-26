import React, { Component } from 'react'
import PropTypes from 'prop-types'
import debounce from 'lodash.debounce'
import DatePicker from 'react-datepicker'
import { InputWithCalendar } from '../../../../layout/form/fields/DateField/InputWithCalendar'

const DELAY_BEFORE_APPLYING_FILTERS_IN_MILLISECONDS = 300

class Filters extends Component {
  constructor() {
    super()
    this.state = {
      startDate: null,
      filters: {
        offerName: '',
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
    let dateToFilter = offerDate === null ? null : offerDate.format('YYYY-MM-DD')
    const { filters } = this.state
    this.setState(
      {
        filters: {
          ...filters,
          offerDate: dateToFilter,
        },
        startDate: offerDate,
      },
      () => {
        const { filters } = this.state
        this.applyFilters(filters)
      }
    )
  }

  render() {
    const { startDate } = this.state
    return (
      <div>
        <div className="bookings-recap-filters">
          <label
            className="select-filters"
            htmlFor="text-filter-input"
          >
            {'Offre'}
          </label>
          <input
            className="text-filter"
            id="text-filter-input"
            onChange={this.handleOfferNameChange}
            placeholder={"Rechercher par nom d'offre"}
            type="text"
          />
        </div>
        <div className="bookings-recap-filters">
          <label
            className="select-filters"
            htmlFor="text-filter-input"
          >
            {"Date de l'évènement"}
          </label>
          <DatePicker
            className="offerDate"
            customInput={<InputWithCalendar />}
            dropdownMode="select"
            onChange={this.handleOfferDateChange}
            placeholderText="JJ/MM/AAAA"
            selected={startDate}
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
