import React, { Fragment, PureComponent } from 'react'
import classnames from 'classnames'
import PropTypes from 'prop-types'

import { MONTH_OPTIONS, YEAR_OPTIONS } from './utils'
import { FilterByVenue } from './FilterByVenue'

export class FilterByDate extends PureComponent {

  constructor(props) {
    super(props)
    this.state = {
      month: '1',
      year: new Date().getFullYear(),
    }
  }

  onChangeMonth = event => {
    this.setState({month:event.target.value})
    const {year} = this.state
    const date = new Date(year, event.target.value - 1, 1, 12)
    this.props.selectBookingsForDate(date)
  }

  onChangeYear = event => {
    this.setState({year:event.target.value})
    const {month} = this.state
    const date = new Date(event.target.value, month - 1, 1, 12)
    this.props.selectBookingsForDate(date)
  }

  render() {
    const isDigitalChecked = false

    return (
      <Fragment>
        <div
          id="filter-by-date"
          className={classnames({ 'is-invisible': isDigitalChecked })}>
          <div>{'Effectuées en :'}</div>
          <label htmlFor="month" className={classnames({ 'is-invisible': true })}>
            Sélectionnez le mois.
          </label>
          <select
            onChange={this.onChangeMonth}
            className="pc-selectbox pl24 py5 fs19"
            defaultValue={this.state.month}
            id="month">
            {MONTH_OPTIONS.map((value, index) => (
              <option key={value} value={index + 1}>
                {value}
              </option>
            ))}
          </select>
          <label htmlFor="year" className={classnames({ 'is-invisible': true })}>
            Sélectionnez l'année.
          </label>
          <select
            onChange={this.onChangeYear}
            className="pc-selectbox pl24 py5 fs19"
            defaultValue={this.state.year}
            id="year">
            {YEAR_OPTIONS.map(value => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </div>
        <hr />
      </Fragment>
    )
  }
}

FilterByVenue.propTypes = {
  date: PropTypes.instanceOf(Date).isRequired,
}
