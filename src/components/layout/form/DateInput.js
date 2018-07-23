import moment from 'moment'
import React from 'react'
import DatePicker from 'react-datepicker'

import Icon from '../Icon'

const DateInput = props => {

  const onChange = date => {
    props.onChange(date.toISOString())
  }

  return props.readOnly
    ? (
      <span className={`label is-${props.size}`}>
        {props.value && moment(props.value).format(props.dateFormat)}
      </span>
      )
    : (
      <div className={`input is-${props.size} date-picker`}>
        <span>
          <DatePicker
            className='date'
            filterDate={props.filterDate}
            highlightDates={(props.highlightedDates || []).map(d => moment(d))}
            minDate={props.minDate === 'today' ? moment() : (props.minDate && moment(props.minDate))}
            maxDate={props.maxDate === 'today' ? moment() : (props.maxDate && moment(props.maxDate))}
            onChange={onChange}
            readOnly={props.readOnly}
            selected={props.value ? moment(props.value) : null}
          />
        </span>
        <span className='icon'>
          <Icon
            alt='Horaires'
            className="input-icon"
            svg="ico-calendar"
          />
        </span>
      </div>
    )
}

DateInput.defaultProps = {
  dateFormat: 'DD/MM/YYYY',
}

export default DateInput
