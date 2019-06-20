import React, { PureComponent } from 'react'
import classnames from 'classnames'
import PropTypes from 'prop-types'

import { MONTH_OPTIONS, YEAR_OPTIONS } from './utils'
import {FilterByVenue} from './FilterByVenue'

export class FilterByDate extends PureComponent {

  onChangeDate = event => {
    const selectedMonth = document.getElementById("month")
    const month = selectedMonth[selectedMonth.selectedIndex].value
    const selectedYear = document.getElementById("year")
    const year = selectedYear[selectedYear.selectedIndex].value
    const updatedDate = new Date(year, month-1, 1, 12)
    this.props.selectBookingsForDate(updatedDate)
  }

  render() {
    const isDigitalChecked = false

    return (
      <React.Fragment>
        <div id="filter-by-date"
             className={classnames({'is-invisible': isDigitalChecked,})} >
          <div>
            {'Effectuées en :'}
          </div>
          <select
            onChange={this.onChangeDate}
            className="pc-selectbox pl24 py5 fs19"
            defaultValue="1"
            id="month"
          >
            {MONTH_OPTIONS.map(({ label, value }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <select
            onChange={this.onChangeDate}
            className="pc-selectbox pl24 py5 fs19"
            defaultValue="2019"
            id="year"
          >
            {YEAR_OPTIONS.map(({ label, value }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </React.Fragment>
    )
  }
}

FilterByVenue.propTypes = {
  date: PropTypes.instanceOf(Date).isRequired,
}
