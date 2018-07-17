import React from 'react'
import DatePicker from 'react-datepicker'
import moment from 'moment'

import Icon from '../Icon'

const DateInput = props => {

  return props.readOnly ? (
    <span> {props.value && props.value.format(props.dateFormat)} </span>
    ) : (
    <div className={`input is-${props.size} date-picker`}>
      <DatePicker
        className='date'
        filterDate={props.filterDate}
        highlightDates={props.highlightedDates || []}
        minDate={props.minDate || moment()}
        onChange={props.onChange}
        selected={props.value ? moment(props.value) : null}
      />
      <Icon
        alt='Horaires'
        className="input-icon"
        svg="ico-calendar"
      />
    </div>
  )
}

DateInput.defaultProps = {
  dateFormat: 'DD/MM/YYYY',
}

export default DateInput

