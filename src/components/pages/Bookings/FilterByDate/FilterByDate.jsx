import React, { PureComponent } from 'react'
import PropTypes from 'prop-types'
import moment from 'moment'

import MONTH_OPTIONS from '../utils/months'
import YEAR_OPTIONS from '../utils/years'

const FRENCH_DATE_FORMAT = 'dddd D MMMM YYYY, HH:mm'

class FilterByDate extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      month: null,
      year: null,
    }
  }

  handleOnChangeMonth = event => {
    const month = event.target.value
    this.setState({ month: month })

    const { year } = this.state
    if (year !== null) {
      this.updateBookingsDates(month, year)
    }
  }

  handleOnChangeYear = event => {
    const year = event.target.value
    this.setState({ year: year })

    const { month } = this.state
    if (month !== null) {
      this.updateBookingsDates(month, year)
    }
  }

  handleOnChangeEventDate = event => {
    const { updateBookingsFrom, updateBookingsTo } = this.props
    const bookingDate = event.target.value

    updateBookingsFrom(bookingDate)
    updateBookingsTo(bookingDate)
  }

  updateBookingsDates = (month, year) => {
    const { updateBookingsFrom, updateBookingsTo } = this.props
    const firstDayOfTheMonth = 1
    const date = moment()
      .date(firstDayOfTheMonth)
      .month(month)
      .year(year)
      .utc()
    const startDate = date.startOf('day').format()
    const endDate = date.endOf('month').format()

    updateBookingsFrom(startDate)
    updateBookingsTo(endDate)
  }

  render() {
    const { showEventDateSection, showThingDateSection, stocks } = this.props

    if (showThingDateSection) {
      return (
        <div id="filter-thing-by-date">
          <div>
            {'Effectuées en :'}
          </div>
          <label
            className="is-invisible"
            htmlFor="month"
          >
            {'Sélectionnez le mois.'}
          </label>
          <select
            className="pc-selectbox"
            id="month"
            onBlur={this.handleOnChangeMonth}
            onChange={this.handleOnChangeMonth}
          >
            <option
              disabled
              label=" - Mois - "
              selected
            />
            {MONTH_OPTIONS.map((value, index) => (
              <option
                key={value}
                value={index}
              >
                {value}
              </option>
            ))}
          </select>

          <label
            className="is-invisible"
            htmlFor="year"
          >
            {"Sélectionnez l'année."}
          </label>
          <select
            className="pc-selectbox"
            id="year"
            onBlur={this.handleOnChangeYear}
            onChange={this.handleOnChangeYear}
          >
            <option
              disabled
              label=" - Année - "
              selected
            />
            {YEAR_OPTIONS.map(value => (
              <option
                key={value}
                value={value}
              >
                {value}
              </option>
            ))}
          </select>
        </div>
      )
    }

    if (showEventDateSection) {
      return (
        <div id="filter-event-by-date">
          <label htmlFor="event-date">
            {'Pour la date du :'}
          </label>
          <select
            className="pc-selectbox"
            id="event-date"
            onBlur={this.handleOnChangeEventDate}
            onChange={this.handleOnChangeEventDate}
          >
            <option
              disabled
              label=" - Choisissez une date - "
              selected
            />
            {stocks.map(({ beginningDatetime }) => (
              <option
                key={beginningDatetime}
                value={beginningDatetime}
              >
                {moment(beginningDatetime)
                  .utc()
                  .format(FRENCH_DATE_FORMAT)}
              </option>
            ))}
          </select>
        </div>
      )
    }
  }
}

FilterByDate.defaultProps = {
  stocks: [],
}

FilterByDate.propTypes = {
  showEventDateSection: PropTypes.bool.isRequired,
  showThingDateSection: PropTypes.bool.isRequired,
  stocks: PropTypes.arrayOf(PropTypes.shape()),
  updateBookingsFrom: PropTypes.func.isRequired,
  updateBookingsTo: PropTypes.func.isRequired,
}

export default FilterByDate
