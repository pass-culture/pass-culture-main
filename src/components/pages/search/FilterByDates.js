import get from 'lodash.get'
import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Component } from 'react'

const checkboxes = [
  {
    label: 'Tout de suite !',
    value: '0-1',
  },
  {
    label: 'Entre 1 et 5 jours',
    value: '1-5',
  },
  {
    label: 'Plus de 5 jours',
    // will the pass culture live for ever?
    // guess that 273 years are enough
    value: '5-100000',
  },
]

class FilterByDates extends Component {
  onChange = day => {
    const { filter } = this.props

    const days = decodeURI(filter.query.jours || '')
    const isAlreadyIncluded = days.includes(day)

    // WE ADD THE DATE AT THE FIRST DAYS SEGMENTS CLICKED
    // WE REMOVE THE DATE AT THE LAST DAYS SEGMENTS CLICKED
    let callback
    if (!get(days, 'length')) {
      const date = moment(moment.now()).toISOString()
      callback = () => filter.change({ date })
    } else if (isAlreadyIncluded && days.split(',').length === 1) {
      callback = () => filter.change({ date: null })
    }

    if (isAlreadyIncluded) {
      filter.remove('jours', day, callback)
      return
    }

    filter.add('jours', day, callback)
  }

  render() {
    const { filter, title } = this.props

    const days = decodeURI(filter.query.jours || '')

    return (
      <div className="dotted-bottom-primary" id="filter-by-dates">
        <h2 className="fs18 is-italic is-uppercase text-center">
          {title}
        </h2>
        <div className="filter-menu-outer">
          {checkboxes.map(({ label, value }) => (
            <div id="date-checkbox" className="filter-menu-inner" key={value}>
              <div className="field field-checkbox">
                <label className="fs22"> 
                  {' '}
                  {label}
                </label>
                <input
                  checked={days.includes(value)}
                  className="input is-normal"
                  onChange={() => this.onChange(value)}
                  type="checkbox"
                />
              </div>
            </div>
          ))}
          <div className="filter-menu-inner">
DATE PICKER TO DO
          </div>
        </div>
      </div>
    )
  }
}

FilterByDates.propTypes = {
  filter: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
}

export default FilterByDates
