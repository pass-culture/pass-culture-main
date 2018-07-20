import React from 'react'
import DatePicker from 'react-datepicker'
import moment from 'moment'

import Icon from '../Icon'

const DateInput = props => {

  const onChange = date => {
    props.onChange({[props.dataKey]: date})
  }

  return props.readOnly ? (
    <span> {props.value && props.value.format(props.dateFormat)} </span>
    ) : (
    <div className={`input is-${props.size} date-picker`}>
      <span>
        <DatePicker
          className='date'
          filterDate={props.filterDate}
          highlightDates={props.highlightedDates || []}
          minDate={props.minDate === 'today' ? moment() : props.minDate}
          maxDate={props.maxDate === 'today' ? moment() : props.maxDate}
          onChange={onChange}
          readOnly={props.readOnly}
          selected={props.value || null}
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

