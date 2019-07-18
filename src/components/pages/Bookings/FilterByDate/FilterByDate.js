import React, { Fragment, PureComponent } from 'react'
import classnames from 'classnames'
import PropTypes from 'prop-types'

import { MONTH_OPTIONS, YEAR_OPTIONS } from '../utils'

export class FilterByDate extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      month: '1',
      year: new Date().getFullYear(),
    }
  }

  componentDidMount() {
    const { selectBookingsDateFrom, selectBookingsDateTo, showEventDateSection } = this.props
    if (showEventDateSection) {
      const e = document.getElementById('event-date').toISOString()
      const selectOffersFrom = e.options[e.selectedIndex].value
      selectBookingsDateFrom(selectOffersFrom)
    } else {
      const selectOffersFrom = new Date(2018, 1, 1).toISOString()
      selectBookingsDateFrom(selectOffersFrom)
      const selectOffersTo = new Date(2018, 1, 1).toISOString()
      selectBookingsDateTo(selectOffersTo)
    }
  }

  handleOnChangeMonth = event => {
    this.setState({ month: event.target.value })
    const { year } = this.state
    const { selectBookingsDateFrom, selectBookingsDateTo } = this.props
    const first_day_of_the_month = new Date(year, event.target.value - 1, 1, 12)
    selectBookingsDateFrom(first_day_of_the_month.toISOString())
    const first_day_of_the_next_month = new Date(year, event.target.value, 1)
    const last_day_of_the_month = new Date(first_day_of_the_next_month - 1)
    selectBookingsDateTo(last_day_of_the_month.toISOString())
  }

  handleOnChangeYear = event => {
    this.setState({ year: event.target.value })
    const { month } = this.state
    const { selectBookingsDateFrom, selectBookingsDateTo } = this.props
    const first_day_of_the_month = new Date(event.target.value, month - 1, 1, 12)
    selectBookingsDateFrom(first_day_of_the_month.toISOString())
    const first_day_of_the_next_month = new Date(event.target.value, month, 1)
    const last_day_of_the_month = new Date(first_day_of_the_next_month - 1)
    selectBookingsDateTo(last_day_of_the_month.toISOString())
  }

  handleOnChangeEventDate = event => {
    const { selectBookingsDateFrom, selectBookingsDateTo } = this.props
    selectBookingsDateFrom(event.target.value.toISOString())
    selectBookingsDateTo(event.target.value.toISOString())
  }

  render() {
    const isDigitalChecked = false
    const { month, year } = this.state
    const { showEventDateSection, showThingDateSection, stocksOptions } = this.props

    if (showThingDateSection) {
      return (
        <Fragment>
          <div
            className={classnames({ 'is-invisible': isDigitalChecked })}
            id="filter-thing-by-date"
          >
            <div>{'Effectuées en :'}</div>
            <label
              className={classnames({ 'is-invisible': true })}
              htmlFor="month"
            >
              {'Sélectionnez le mois.'}
            </label>
            <select
              className="pc-selectbox pl24 py5 fs19"
              defaultValue={month}
              id="month"
              onBlur={this.handleOnChangeMonth}
              onChange={this.handleOnChangeMonth}
            >
              {MONTH_OPTIONS.map((value, index) => (
                <option
                  key={value}
                  value={index + 1}
                >
                  {value}
                </option>
              ))}
            </select>
            <label
              className={classnames({ 'is-invisible': true })}
              htmlFor="year"
            >
              {"Sélectionnez l'année."}
            </label>
            <select
              className="pc-selectbox pl24 py5 fs19"
              defaultValue={year}
              id="year"
              onBlur={this.handleOnChangeYear}
              onChange={this.handleOnChangeYear}
            >
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
          <hr />
        </Fragment>
      )
    } else if (showEventDateSection) {
      return (
        <Fragment>
          <div
            className={classnames({ 'is-invisible': isDigitalChecked })}
            id="filter-event-by-date"
          >
            <label htmlFor="event-date">{'Pour la date du :'}</label>
            <select
              className="pc-selectbox pl24 py5 fs19"
              defaultValue={''}
              id="event-date"
              onBlur={this.handleOnChangeEventDate}
              onChange={this.handleOnChangeEventDate}
            >
              {stocksOptions.map(({ beginingDateTime, id }) => (
                <option
                  key={id}
                  value={beginingDateTime}
                >
                  {beginingDateTime.toISOString()}
                </option>
              ))}
            </select>
          </div>
          <hr />
        </Fragment>
      )
    } else {
      return null
    }
  }
}

FilterByDate.defaultProps = {
  stocksOptions: [],
}

FilterByDate.propTypes = {
  selectBookingsDateFrom: PropTypes.func.isRequired,
  selectBookingsDateTo: PropTypes.func.isRequired,
  showEventDateSection: PropTypes.bool.isRequired,
  showThingDateSection: PropTypes.bool.isRequired,
  stocksOptions: PropTypes.arrayOf(),
}
