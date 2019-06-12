import React, { PureComponent } from 'react'
import classnames from "classnames";

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

    const months = [
      {
        label: 'janvier',
        value: 1,
      },
      {
        label: 'fevruer',
        value: 2,
      },
      {
        label: 'mars',
        value: 3,
      },
      {
        label: 'avril',
        value: 4,
      },
      {
        label: 'mai',
        value: 5,
      },
      {
        label: 'juin',
        value: 6,
      },
      {
        label: 'juillet',
        value: 7,
      },
      {
        label: 'aout',
        value: 8,
      },
      {
        label: 'septembre',
        value: 9,
      },
      {
        label: 'ocotbre',
        value: 10,
      },
      {
        label: 'novembre',
        value: 11,
      },
      {
        label: 'décembre',
        value: 12,
      },
    ]

    const year = [
      {
        label: '2019',
        value: 2019,
      },
      {
        label: '2020',
        value: 2020,
      },
      {
        label: '2021',
        value: 2021,
      }
    ]

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
            {months.map(({ label, value }) => (
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
            {year.map(({ label, value }) => (
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

