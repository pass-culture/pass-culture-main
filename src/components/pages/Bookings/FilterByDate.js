import React, { PureComponent } from 'react'
import classnames from 'classnames'

import { MONTH_OPTIONS, YEAR_OPTIONS } from './utils'


export class FilterByDate extends PureComponent {

  onChangeMonth = event => {
    const selectedMonth = document.getElementById("month")
    const month = selectedMonth[selectedMonth.selectedIndex].value
    console.log("month", month)
  }

  onChangeYear = event => {
    const selectedYear = document.getElementById("year")
    const year = selectedYear[selectedYear.selectedIndex].value
    console.log("year", year)
  }

  render() {
    const isDigitalChecked = false

    return (
      <React.Fragment>
        <div id="filter-by-date"
             className={classnames({'is-invisible': isDigitalChecked,})} >
          <h2>
            {'Effectuées en :'}
          </h2>
          <select
            onChange={this.onChangeMonth}
            className="pc-selectbox pl24 py5 fs19"
            defaultValue="all"
            id="month"
          >
            {MONTH_OPTIONS.map(({ label, value }) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
          <select
            onChange={this.onChangeYear}
            className="pc-selectbox pl24 py5 fs19"
            defaultValue="all"
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

