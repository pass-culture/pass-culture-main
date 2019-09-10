import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { DatePickerField } from '../../../forms/inputs'
import { DAYS_CHECKBOXES, isDaysChecked } from '../helpers'

class FilterByDates extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      pickedDate: null,
    }
    this.datepickerPopper = React.createRef()
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
    const formatedDate = (date && date.toISOString()) || null

    filterActions.change({ date: formatedDate, jours: null })

    this.setPickedDate(date)
  }

  render() {
    const { pickedDate } = this.state
    const { filterState } = this.props
    const pickedDaysInQuery = decodeURI(filterState.params.jours || '')

    return (
      <div
        className="pt18"
        id="filter-by-dates"
      >
        <h2 className="fs15 is-italic is-medium is-uppercase text-center mb12">{'Quand'}</h2>
        <div className="pc-scroll-horizontal is-relative pb18">
          <div className="pc-list flex-columns">
            {DAYS_CHECKBOXES.map(({ label, value }, index) => {
              const checked = isDaysChecked(pickedDate, pickedDaysInQuery, value)

              return (
                <label
                  className="item flex-columns items-center py5 pl7 pr22"
                  htmlFor={`filter-by-dates-days-${index}-checkbox`}
                  key={value}
                >
                  <span className="flex-0 field field-checkbox">
                    <input
                      checked={checked}
                      className="input no-background"
                      id={`filter-by-dates-days-${index}-checkbox`}
                      onChange={this.onChangeDate(value)}
                      type="checkbox"
                      value={value}
                    />
                  </span>
                  <span className="fs19 flex-1">{label}</span>
                </label>
              )
            })}
            <DatePickerField
              className="item fs19 py5 px7"
              minDate={new Date()}
              name="pick-by-date-filter"
              onChange={this.handleOnChangePickedDate}
              placeholder="Par date"
              popperRefContainer={this.datepickerPopper}
              selected={pickedDate}
            />
          </div>
        </div>
        <hr className="dotted-bottom-primary" />
        <div
          id="filter-by-dates-datepicker-popper-container"
          ref={this.datepickerPopper}
        />
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
