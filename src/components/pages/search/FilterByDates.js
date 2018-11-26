import get from 'lodash.get'
import moment from 'moment'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { TODAY_DATE, DAYS_CHECKBOXES } from './utils'
import { DatePickerField } from '../../forms/inputs'

class FilterByDates extends PureComponent {
  constructor(props) {
    super(props)
    this.datepickerPopper = React.createRef()
    this.state = {
      pickedDate: null,
    }
  }

  onChange = day => {
    this.setState({ pickedDate: null })
    const { filterActions, filterState } = this.props

    const daysInUrlParams = decodeURI(filterState.query.jours || '')

    const isdayAlreadyChecked = daysInUrlParams.includes(day)

    let callback

    if (!get(daysInUrlParams, 'length')) {
      const date = moment(moment.now()).toISOString()
      callback = () => filterActions.change({ date })
      // Change valeur de callBack
    } else if (isdayAlreadyChecked && daysInUrlParams.split(',').length === 1) {
      callback = () => filterActions.change({ date: null })
      // Change valeur de callBack
    }

    if (isdayAlreadyChecked) {
      filterActions.remove('jours', day, callback)
      return
    }
    filterActions.add('jours', day, callback)
  }

  onPickedDateChange = date => {
    const { filterActions } = this.props
    const formatedDate = (date && date.toISOString()) || null
    filterActions.change({ date: formatedDate, jours: null })
    this.setState({ pickedDate: date })
  }

  isDateChecked = (pickedDate, daysInUrlParams, inputValue) =>
    pickedDate !== null && inputValue === '0-1'
      ? false
      : daysInUrlParams.includes(inputValue)

  render() {
    const { filterState, title } = this.props
    const daysInUrlParams = decodeURI(filterState.query.jours || '')

    const { pickedDate } = this.state

    return (
      <div id="filter-by-dates" className="pt18">
        <h2 className="fs15 is-italic is-medium is-uppercase text-center mb12">
          {title}
        </h2>
        {/* FIXME: le scroll sous ios est pas terrible
          du fait que le input soit cliquable */}
        <div className="pc-scroll-horizontal is-relative pb18">
          <div className="pc-list flex-columns">
            {DAYS_CHECKBOXES.map(({ label, value }) => {
              const checked = this.isDateChecked(
                pickedDate,
                daysInUrlParams,
                value
              )
              return (
                <label
                  key={value}
                  className="item flex-columns items-center py5 pl7 pr22"
                >
                  <span className="flex-0 field field-checkbox">
                    <input
                      type="checkbox"
                      className="input no-background"
                      checked={checked}
                      onChange={() => this.onChange(value)}
                    />
                  </span>
                  <span className="fs19 flex-1" style={{ whiteSpace: 'pre' }}>
                    {label}
                  </span>
                </label>
              )
            })}
            <DatePickerField
              name="pick-by-date-filter"
              className="item fs19 py5 px7"
              minDate={TODAY_DATE}
              selected={pickedDate}
              onChange={this.onPickedDateChange}
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
  filterActions: PropTypes.object.isRequired,
  filterState: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
}

export default FilterByDates
