import PropTypes from 'prop-types'
import React, { createRef, PureComponent } from 'react'

import DatePickerField from '../../../forms/inputs/DatePickerField/DatePickerField'
import { DAYS_CHECKBOXES, isDaysChecked } from '../helpers'

class FilterByDates extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      pickedDate: null,
    }
    this.datepickerPopper = createRef()
  }

  componentDidUpdate() {
    const { filterState, shouldResetDate } = this.props

    if (shouldResetDate && filterState.params.date === undefined) {
      this.setPickedDate(null)
    }
  }

  setPickedDate = value => {
    this.setState({
      pickedDate: value,
    })
  }

  onChangeDate = day => () => {
    this.setPickedDate(null)
    const { filterActions, filterState } = this.props
    const pickedDaysInQuery = decodeURI(filterState.params.jours || '')
    const isDayAlreadyChecked = pickedDaysInQuery.includes(day)
    let callback

    if (pickedDaysInQuery.length === 0) {
      const date = new Date().toISOString()
      callback = () => filterActions.change({ date })
    } else if (isDayAlreadyChecked && pickedDaysInQuery.split(',').length === 1) {
      callback = () => filterActions.change({ date: null })
    }

    if (isDayAlreadyChecked) {
      filterActions.remove('jours', day, callback)
      return
    }

    filterActions.add('jours', day, callback)
  }

  handleOnChangePickedDate = (date = null) => {
    const { filterActions } = this.props

    const formattedDate =
      (date &&
        date
          .utcOffset(0)
          .add(100, 'milliseconds')
          .toISOString()) ||
      null
    filterActions.change({ date: formattedDate, jours: '0-0' })

    const pickedDate = (date && date.utcOffset(100)) || null
    this.setPickedDate(pickedDate)
  }

  render() {
    const { pickedDate } = this.state
    const { filterState } = this.props
    const pickedDaysInQuery = decodeURI(filterState.params.jours || '')

    return (
      <div id="filter-by-dates">
        <h2 className="fd-when-label">
          {'Quand'}
        </h2>
        <div className="fd-date-picker-container">
          <div className="fd-date-picker">
            <DatePickerField
              className="fd-date-picker-selectbox"
              minDate={new Date()}
              name="pick-by-date-filter"
              onChange={this.handleOnChangePickedDate}
              placeholder="Par date"
              selected={pickedDate}
            />
          </div>
        </div>
        <div className="fd-checkboxes">
          {DAYS_CHECKBOXES.map(({ label, value }, index) => {
            const checked = isDaysChecked(pickedDate, pickedDaysInQuery, value)

            return (
              <label
                className="flex-columns items-center py5 pl7"
                htmlFor={`filter-by-dates-days-${index}-checkbox`}
                key={value}
              >
                <input
                  checked={checked}
                  className="input form-checkbox field field-checkbox"
                  id={`filter-by-dates-days-${index}-checkbox`}
                  onChange={this.onChangeDate(value)}
                  type="checkbox"
                  value={value}
                />
                <span className="fs19">
                  {label}
                </span>
              </label>
            )
          })}
        </div>
        <hr className="dotted-bottom-primary" />
      </div>
    )
  }
}

FilterByDates.propTypes = {
  filterActions: PropTypes.shape({
    add: PropTypes.func.isRequired,
    change: PropTypes.func.isRequired,
    remove: PropTypes.func.isRequired,
  }).isRequired,
  filterState: PropTypes.shape({
    isNew: PropTypes.bool,
    params: PropTypes.shape({
      categories: PropTypes.string,
      date: PropTypes.string,
      distance: PropTypes.string,
      jours: PropTypes.string,
      latitude: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      longitude: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
      'mots-cles': PropTypes.string,
      orderBy: PropTypes.string,
    }),
  }).isRequired,
  shouldResetDate: PropTypes.bool.isRequired,
}

export default FilterByDates
