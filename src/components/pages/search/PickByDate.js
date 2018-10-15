import moment from 'moment'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import DatePicker from 'react-datepicker'

import { Icon } from 'pass-culture-shared'

class PickByDate extends Component {
  render() {
    const {
      dateFormat,
      filterDate,
      highlightedDates,
      id,
      maxDate,
      minDate,
      size,
      value,
    } = this.props

    return (
      <div className={`input is-${size} date-picker`}>
        <span>
          <DatePicker
            className="date"
            dateFormat={dateFormat}
            filterDate={filterDate}
            highlightDates={(highlightedDates || []).map(d => moment(d))}
            id={id}
            minDate={
              minDate === 'today' ? moment() : minDate && moment(minDate)
            }
            maxDate={
              maxDate === 'today' ? moment() : maxDate && moment(maxDate)
            }
            onChange={this.onChange}
            selected={value ? moment(value) : null}
          />
        </span>
        <span className="icon">
          <Icon alt="Horaires" className="input-icon" svg="ico-calendar" />
        </span>
      </div>
    )
  }
}

PickByDate.defaultProps = {
  dateFormat: 'DD/MM/YYYY',
}

PickByDate.propTypes = {
  dateFormat: PropTypes.string,
  filterDate: PropTypes.string.isRequired,
  highlightedDates: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  maxDate: PropTypes.string.isRequired,
  minDate: PropTypes.string.isRequired,
  size: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
}

export default PickByDate
