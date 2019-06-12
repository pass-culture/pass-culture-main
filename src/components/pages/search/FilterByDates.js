import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { DatePickerField } from '../../forms/inputs'
import { DAYS_CHECKBOXES, isDaysChecked } from './utils'

class FilterByDates extends PureComponent {
  constructor(props) {
    super(props)
    this.state = {
      pickedDate: null,
    }
    this.datepickerPopper = React.createRef()
  }

  componentDidUpdate() {
    const { initialDateParams, filterState } = this.props

    if (initialDateParams && filterState.params.date === undefined) {
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
    const isdayAlreadyChecked = pickedDaysInQuery.includes(day)
    let callback

    if (pickedDaysInQuery.length === 0) {
      const date = new Date().toISOString()
      callback = () => filterActions.change({ date })
    } else if (
      isdayAlreadyChecked &&
      pickedDaysInQuery.split(',').length === 1
    ) {
      callback = () => filterActions.change({ date: null })
    }

    if (isdayAlreadyChecked) {
      filterActions.remove('jours', day, callback)
      return
    }

    filterActions.add('jours', day, callback)
  }

  onChangePickedDate = (date = null) => {
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
      <div id="filter-by-dates" className="pt18">
        <h2 className="fs15 is-italic is-medium is-uppercase text-center mb12">
          {'Quand'}
        </h2>
        <div className="pc-scroll-horizontal is-relative pb18">
          <div className="pc-list flex-columns">
            {DAYS_CHECKBOXES.map(({ label, value }, index) => {
              const checked = isDaysChecked(
                pickedDate,
                pickedDaysInQuery,
                value
              )

              return (
                <label
                  htmlFor={`filter-by-dates-days-${index}-checkbox`}
                  key={value}
                  className="item flex-columns items-center py5 pl7 pr22"
                >
                  <span className="flex-0 field field-checkbox">
                    <input
                      id={`filter-by-dates-days-${index}-checkbox`}
                      type="checkbox"
                      className="input no-background"
                      checked={checked}
                      onChange={this.onChangeDate(value)}
                      value={value}
                    />
                  </span>
                  <span className="fs19 flex-1">{label}</span>
                </label>
              )
            })}
            <DatePickerField
              name="pick-by-date-filter"
              className="item fs19 py5 px7"
              minDate={new Date()}
              selected={pickedDate}
              onChange={this.onChangePickedDate}
              popperRefContainer={this.datepickerPopper}
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
  initialDateParams: PropTypes.bool.isRequired,
}

export default FilterByDates
